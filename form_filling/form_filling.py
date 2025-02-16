# src/form_filling.py

import logging
from form_filling.utils import GenerateContentUtils
from llm_utils import LLMUtils
from fuzzywuzzy import fuzz
from playwright.sync_api import Page, ElementHandle

logger = logging.getLogger(__name__)

class FormFilling:
    
    def __init__(self, llm: LLMUtils = None, resume_content: str = None, resume_path: str = None):
        self.content_utils = GenerateContentUtils(llm, resume_content, resume_path)

    @staticmethod
    def get_value_from_details(field_name: str, details: dict) -> str:
        logger.debug(f"Searching for value matching field '{field_name}' in details")
        for key, value in details.items():
            if fuzz.partial_ratio(field_name.lower(), key.lower()) > 80:
                logger.debug(f"Matched field '{field_name}' with detail key '{key}'")
                return value
        logger.debug(f"No match found for field '{field_name}' in details")
        return None

    def fill_input(self, element: ElementHandle, field_name: str, details: dict = None) -> None:
        logger.debug(f"Filling input for field '{field_name}'")
        input_type = element.evaluate("el => el.type")
        logger.debug(f"Input type for field '{field_name}' is '{input_type}'")
        value = FormFilling.get_value_from_details(field_name, details)
        if not value:
            field_label = element.get_attribute("aria-label") or field_name
            logger.debug(f"Generating content for field '{field_name}' with label '{field_label}'")
            value = self.content_utils.generate_field_content(field_label)
        if input_type in ["text", "email", "tel", "url", "search", "password"]:
            element.fill(value)
            logger.info(f"Filled text field '{field_name}' with value '{value}'")
        elif input_type == "radio":
            self.fill_radio(element, details)
        elif input_type == "checkbox":
            self.fill_checkbox(element, field_name, details)

    def fill_textarea(self, element: ElementHandle, field_name: str, details: dict = None) -> None:
        logger.debug(f"Filling textarea for field '{field_name}'")
        value = FormFilling.get_value_from_details(field_name, details)
        if not value:
            field_label = element.get_attribute("aria-label") or field_name
            logger.debug(f"Generating content for textarea '{field_name}' with label '{field_label}'")
            value = self.content_utils.generate_field_content(field_label)
        element.fill(value)
        logger.info(f"Filled textarea '{field_name}' with value '{value}'")

    def fill_select(self, element: ElementHandle, details: dict = None) -> None:
        logger.debug("Filling select element")
        options = [opt.text_content() for opt in element.query_selector_all("option")]
        logger.debug(f"Available options: {options}")
        chosen_option = None
        if details:
            chosen_option = FormFilling.get_value_from_details(element.get_attribute("name"), details)
        if not chosen_option:
            chosen_option = self.content_utils.generate_select_content(options)
        element.select_option(label=chosen_option)
        logger.info(f"Selected option '{chosen_option}' for select element")

    def fill_radio(self, element: ElementHandle, details: dict = None, options = None) -> None:
        logger.debug("Filling radio element")
        if options is None:
            options = element.query_selector_all("input[type='radio']")
        option_labels = [opt.get_attribute("aria-label") for opt in options]
        logger.debug(f"Available radio options: {option_labels}")
        chosen_option = None
        if details:
            chosen_option = FormFilling.get_value_from_details(element.get_attribute("name"), details)
        if not chosen_option:
            chosen_option = self.content_utils.generate_radio_content(option_labels)
        for opt in options:
            if opt.get_attribute("aria-label") == chosen_option:
                opt.click()
                logger.info(f"Checked radio option '{chosen_option}'")
                return

    def fill_checkbox(self, element: ElementHandle, field_name: str, details: dict = None) -> None:
        logger.debug(f"Filling checkbox for field '{field_name}'")
        value = FormFilling.get_value_from_details(field_name, details)
        if value is None:
            value = self.content_utils.generate_field_content(field_name)
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