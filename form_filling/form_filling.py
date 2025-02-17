# src/form_filling.py

import logging
from fuzzywuzzy import fuzz
from playwright.sync_api import Page, ElementHandle
from form_filling.utils import GenerateContentUtils
from llm_utils import LLMUtils

logger = logging.getLogger(__name__)

class FormFilling:
    
    def __init__(self, llm: LLMUtils = None, resume_content: str = None, resume_path: str = None):
        self.content_utils = GenerateContentUtils(llm, resume_content, resume_path)
        logger.info("Initialized FormFilling with provided LLM and resume content")

    @staticmethod
    def get_value_from_details(field_name: str, details: dict) -> str:
        logger.debug(f"Searching for value matching field '{field_name}' in details: {details}")
        if details:
            for key, value in details.items():
                if fuzz.partial_ratio(field_name.lower(), key.lower()) > 80:
                    logger.debug(f"Matched field '{field_name}' with detail key '{key}' and value '{value}'")
                    return value
            logger.debug(f"No match found for field '{field_name}' in details")
        return None

    def fill_element(self, element: ElementHandle, field_name: str = None, details: dict = None) -> None:
        if not field_name:
            field_name = element.get_attribute("name") or element.get_attribute("id") or "unknown"
        logger.debug(f"Filling element for field '{field_name}' with details: {details}")
        input_type = element.evaluate("el => el.type")
        logger.debug(f"Element type for field '{field_name}' is '{input_type}'")
        value = FormFilling.get_value_from_details(field_name, details)
        
        fill_methods = {
            "text": self._fill_text,
            "email": self._fill_text,
            "tel": self._fill_text,
            "url": self._fill_text,
            "search": self._fill_text,
            "password": self._fill_text,
            "radio": self._fill_radio,
            "checkbox": self._fill_checkbox,
            "textarea": self._fill_text,
            "select-one": self._fill_select
        }
        
        fill_method = fill_methods.get(input_type, self._fill_text)
        logger.debug(f"Using fill method '{fill_method.__name__}' for field '{field_name}'")
        fill_method(element, field_name, value)

    def _fill_text(self, element: ElementHandle, field_name: str, value: str) -> None:
        if not value:
            value = self.content_utils.generate_field_content(field_label=field_name)
        element.fill(value)
        logger.info(f"Filled text field '{field_name}' with value '{value}'")

    def _fill_select(self, element: ElementHandle, field_name: str, value: str) -> None:
        options = [opt.text_content() for opt in element.query_selector_all("option")]
        logger.debug(f"Available options for select field '{field_name}': {options}")
        chosen_option = value or self.content_utils.generate_select_content(options)
        element.select_option(label=chosen_option)
        logger.info(f"Selected option '{chosen_option}' for select element '{field_name}'")

    def _fill_radio(self, element: ElementHandle, field_name: str, value: str) -> None:
        options = element.query_selector_all("input[type='radio']")
        option_labels = [opt.get_attribute("aria-label") for opt in options]
        logger.debug(f"Available radio options for field '{field_name}': {option_labels}")
        chosen_option = value or self.content_utils.generate_radio_content(option_labels)
        for opt in options:
            if opt.get_attribute("aria-label") == chosen_option:
                opt.click()
                logger.info(f"Checked radio option '{chosen_option}' for field '{field_name}'")
                return

    def _fill_checkbox(self, element: ElementHandle, field_name: str, value: str) -> None:
        if value:
            element.check()
            logger.info(f"Checked checkbox '{field_name}'")
        else:
            element.uncheck()
            logger.info(f"Unchecked checkbox '{field_name}'")

    @staticmethod
    def handle_file_upload(page: Page, element: ElementHandle, resume_path: str) -> None:
        logger.debug(f"Handling file upload for path '{resume_path}'")
        with page.expect_file_chooser() as fc_info:
            element.click()
        file_chooser = fc_info.value
        file_chooser.set_files(resume_path)
        logger.info(f"Uploaded file '{resume_path}'")