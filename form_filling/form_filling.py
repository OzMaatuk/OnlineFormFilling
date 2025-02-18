import logging
from fuzzywuzzy import fuzz
from playwright.sync_api import ElementHandle
from form_filling.content_utils import GenerateContentUtils
from llm_utils import LLMUtils
from form_filling.element_utils import ElementUtils
from form_filling.value_evaluator import ValueEvaluator
from form_filling.element_handlers import ElementHandlers
from form_filling.file_handler import FileHandler

logger = logging.getLogger(__name__)

class FormFilling:

    def __init__(self, llm: LLMUtils = None, resume_content: str = None, resume_path: str = None):
        self.content_utils = GenerateContentUtils(llm, resume_content, resume_path)
        self.llm = llm
        self.resume_path = resume_path
        self.element_utils = ElementUtils()
        self.value_evaluator = ValueEvaluator(self.content_utils)
        self.element_handlers = ElementHandlers(self.content_utils)
        self.file_handler = FileHandler()
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
            field_name = self.element_utils.determine_field_name(element)
        
        logger.debug(f"Filling element for field '{field_name}' with details: {details}")
        
        element_type = self.element_utils.determine_element_type(element)
        logger.debug(f"Element type for field '{field_name}' is '{element_type}'")
        
        # Get raw value from details
        raw_value = FormFilling.get_value_from_details(field_name, details)
        
        # Evaluate the value using the centralized method
        value = self.value_evaluator.evaluate_value(element_type, field_name, raw_value, element)
        
        # Handle file uploads separately
        if element_type == "file":
            self.file_handler.handle_file_upload(element.page, element, value or self.resume_path)
            return
            
        # Fill the element based on its type
        self.element_handlers.fill_element(element, element_type, field_name, value)