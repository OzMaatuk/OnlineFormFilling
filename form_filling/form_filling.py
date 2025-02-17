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

    def determine_element_type(self, element: ElementHandle) -> str:
        """Determine the type of form element to handle specialized cases"""
        # First check for tag name to identify basic element type
        tag_name = element.evaluate("el => el.tagName").lower()
        
        # For input elements, check type attribute
        if tag_name == "input":
            input_type = element.evaluate("el => el.type")
            return input_type
        
        known_types = ["text", "select", "select-one", "textarea", "radio", "checkbox"]
        if tag_name in known_types:
            return tag_name        

        # Check for radiogroup role
        role = element.get_attribute("role")
        if role == "radiogroup":
            return "radiogroup"
        
        # Check for checkbox container
        if element.query_selector("input[type='checkbox']"):
            return "checkbox-container"
            
        raise Exception(f"Cannot determine element type. {element}")

    def fill_element(self, element: ElementHandle, field_name: str = None, details: dict = None) -> None:
        if not field_name:
            field_name = self._determine_field_name(element)
        
        logger.debug(f"Filling element for field '{field_name}' with details: {details}")
        
        element_type = self.determine_element_type(element)
        logger.debug(f"Element type for field '{field_name}' is '{element_type}'")
        
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
            "select-one": self._fill_select,
            "select": self._fill_select,
            "radiogroup": self._fill_radiogroup,
            "checkbox-container": self._fill_checkbox_container,
            "file": self._fill_file
        }
        
        fill_method = fill_methods.get(element_type, self._fill_text)
        logger.debug(f"Using fill method '{fill_method.__name__}' for field '{field_name}'")
        fill_method(element, field_name, value)

    def _determine_field_name(self, element: ElementHandle) -> str:
        """Extract the most appropriate name for the field from various attributes"""
        # Check common attributes for field name
        for attr in ["name", "id", "aria-label", "aria-labelledby", "data-testid"]:
            attr_value = element.get_attribute(attr)
            if attr_value:
                # If this is a labelledby reference, get the text from the referenced element
                if attr == "aria-labelledby":
                    try:
                        page = element.page
                        referenced_element = page.locator(f"#{attr_value}")
                        label_text = referenced_element.text_content()
                        if label_text:
                            return label_text.strip()
                    except Exception as e:
                        logger.warning(f"Failed to get text from aria-labelledby element: {e}")
                else:
                    return attr_value
        
        # Look for an associated label element
        try:
            id_value = element.get_attribute("id")
            if id_value:
                page = element.page
                label = page.locator(f"label[for='{id_value}']")
                if label.count() > 0:
                    return label.first.text_content().strip()
        except Exception as e:
            logger.warning(f"Failed to get text from associated label: {e}")
        
        # Return placeholder text as a fallback
        placeholder = element.get_attribute("placeholder")
        if placeholder:
            return placeholder
        
        return "unknown"

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
        label = element.get_attribute("aria-label") or element.get_attribute("value")
        option_labels = f"[{label}, None]"
        chosen_option = value or self.content_utils.generate_radio_content(option_labels)
        if chosen_option != "None":
            element.click()
            logger.info(f"Checked radio button '{field_name}' with value '{value}'")
    
    def _fill_radiogroup(self, element: ElementHandle, field_name: str, value: str) -> None:
        radio_buttons = element.query_selector_all("input[type='radio']")
        option_labels = []
        
        # Collect all radio button labels
        for radio in radio_buttons:
            label = radio.get_attribute("aria-label") or radio.get_attribute("value")
            if label:
                option_labels.append(label)
                
        logger.debug(f"Available radio options for field '{field_name}': {option_labels}")
        chosen_option = value or self.content_utils.generate_radio_content(option_labels)
        
        for radio in radio_buttons:
            label = radio.get_attribute("aria-label") or radio.get_attribute("value")
            if label and label == chosen_option:
                # Use the existing _fill_radio method for better encapsulation
                radio_field_name = f"{field_name} - {label}"
                self._fill_radio(radio, radio_field_name, "true")
                return
                
        logger.warning(f"Failed to find radio option '{chosen_option}' in group '{field_name}'")

    def _fill_checkbox(self, element: ElementHandle, field_name: str, value: str) -> None:
        should_check = value and value.lower() in ["true", "yes", "1", "on"]
        if should_check:
            element.check()
            logger.info(f"Checked checkbox '{field_name}'")
        else:
            element.uncheck()
            logger.info(f"Unchecked checkbox '{field_name}'")

    def _fill_checkbox_container(self, element: ElementHandle, field_name: str, value: str) -> None:
        checkboxes = element.query_selector_all("input[type='checkbox']")
        if not value:
            logger.warning(f"No value provided for checkbox container '{field_name}'")
            return
            
        if len(checkboxes) == 0:
            logger.warning(f"No checkboxes found in container '{field_name}'")
            return
            
        for checkbox in checkboxes:
            cb_label = checkbox.get_attribute("aria-label") or checkbox.get_attribute("value") or checkbox.get_attribute("id")
            if cb_label and fuzz.partial_ratio(value.lower(), cb_label.lower()) > 80:
                # Use the existing _fill_checkbox method for better encapsulation
                checkbox_field_name = f"{field_name} - {cb_label}"
                self._fill_checkbox(checkbox, checkbox_field_name, "true")
                return
                
        logger.warning(f"No checkbox found in container '{field_name}' matching value '{value}'")

    def _fill_file(self, element: ElementHandle, field_name: str, value: str) -> None:
        resume_path = value or self.content_utils.resume_path
        if resume_path:
            self.handle_file_upload(element.page, element, resume_path)
        else:
            logger.warning(f"No file path provided for file input '{field_name}'")

    @staticmethod
    def handle_file_upload(page: Page, element: ElementHandle, resume_path: str) -> None:
        logger.debug(f"Handling file upload for path '{resume_path}'")
        with page.expect_file_chooser() as fc_info:
            element.click()
        file_chooser = fc_info.value
        file_chooser.set_files(resume_path)
        logger.info(f"Uploaded file '{resume_path}'")