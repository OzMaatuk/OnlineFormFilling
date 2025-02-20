# form_filling\form_filling.py

import logging
from typing import Optional, Dict, Any
from fuzzywuzzy import fuzz
from playwright.sync_api import ElementHandle
from llm_utils import LLMUtils
from form_filling.element_utils import ElementUtils
from form_filling.value_evaluator import ValueEvaluator
from form_filling.element_handlers import ElementHandlers
from form_filling.file_handler import FileHandler

logger = logging.getLogger(__name__)

class FormFilling:

    def __init__(self, llm: Optional[LLMUtils] = None, resume_content: Optional[str] = None, 
                 resume_path: Optional[str] = None):
        logger.info("Initializing FormFilling with LLM and resume content")
        self.llm = llm
        self.resume_path = resume_path
        self.element_utils = ElementUtils()
        self.value_evaluator = ValueEvaluator(None, llm, resume_content, resume_path)
        self.element_handlers = ElementHandlers()
        self.file_handler = FileHandler()
        logger.info("FormFilling initialization complete")

    @staticmethod
    def get_value_from_details(field_name: str, details: Optional[Dict[str, Any]]) -> Optional[str]:
        """Find a value in the details dictionary that matches the field name"""
        logger.debug(f"Searching for value matching field '{field_name}' in details dictionary")
        if details:
            for key, value in details.items():
                match_score = fuzz.partial_ratio(field_name.lower(), key.lower())
                logger.debug(f"Match score for '{field_name}' with '{key}': {match_score}")
                if match_score > 80:
                    logger.debug(f"Matched field '{field_name}' with detail key '{key}' and value '{value}'")
                    return str(value) if value is not None else None
            logger.debug(f"No match found for field '{field_name}' in details")
        return None

    def fill_element(self, element: ElementHandle, field_name: Optional[str] = None, 
                    details: Optional[Dict[str, Any]] = None) -> None:
        """Fill a form element based on its type and the provided details"""
        if not field_name:
            field_name = self.element_utils.determine_field_name(element)
        
        logger.info(f"Filling element for field '{field_name}'")
        logger.debug(f"Details for field '{field_name}': {details}")
        
        element_type = self.element_utils.determine_element_type(element)
        logger.debug(f"Element type for field '{field_name}' is '{element_type}'")
        
        if details["resume_path"] != None and details["resume_path"] != self.resume_path:
            self.value_evaluator.content_utils.set_new_resume_from_path(details["resume_path"])

        # Get raw value from details
        raw_value = FormFilling.get_value_from_details(field_name, details)
        logger.debug(f"Raw value for field '{field_name}': {raw_value}")
        
        # Evaluate the value using the centralized method
        value = self.value_evaluator.evaluate_value(element_type, field_name, raw_value, element)
        logger.debug(f"Evaluated value for field '{field_name}': {value}")
        
        # Handle file uploads separately
        if element_type == "file":
            self.file_handler.handle_file_upload(element.page, element, value or self.resume_path)
            return
            
        # Fill the element based on its type
        self.element_handlers.fill_element(element, element_type, field_name, value)
        logger.info(f"Successfully filled element for field '{field_name}'")