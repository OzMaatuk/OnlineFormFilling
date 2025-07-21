# form_filling\form_filling.py

import logging
from typing import Optional, Dict, Any
from fuzzywuzzy import fuzz
from playwright.sync_api import ElementHandle
from langchain.chat_models import init_chat_model
from form_filling.element_utils import ElementUtils
from form_filling.value_evaluator import ValueEvaluator
from form_filling.element_handlers import ElementHandlers
from form_filling.file_handler import FileHandler
from form_filling.content_utils import GenerateContentUtils
from langchain.chat_models.base import BaseChatModel

logger = logging.getLogger(__name__)

class FormFilling:

    def __init__(self, llm: Optional[object] = None, resume_content: Optional[str] = None, 
                 resume_path: Optional[str] = None, chat_model_config: Optional[dict] = None):
        logger.info("Initializing FormFilling with LangChain chat model and resume content")
        if llm is None:
            llm = init_chat_model(**(chat_model_config or {}))
        self.llm: Optional[object] = llm
        self.resume_path: Optional[str] = resume_path
        self.element_utils = ElementUtils()
        # Ensure llm is of type BaseChatModel or None before passing
        llm_for_content_utils = llm if isinstance(llm, BaseChatModel) or llm is None else None
        content_utils = GenerateContentUtils(llm_for_content_utils, resume_content, resume_path, chat_model_config)
        llm_for_evaluator = llm if isinstance(llm, BaseChatModel) or llm is None else None
        self.value_evaluator = ValueEvaluator(content_utils, llm_for_evaluator, resume_content, resume_path, chat_model_config)
        self.element_handlers = ElementHandlers()
        self.file_handler = FileHandler()
        logger.info("FormFilling initialization complete")

    @staticmethod
    def get_value_from_details(field_name: str, details: Optional[Dict[str, Any]]) -> Optional[str]:
        """Find a value in the details dictionary that matches the field name"""
        logger.debug(f"Searching for value matching field '{field_name}' in details dictionary")
        
        if details:
            # Handle resume_path for file/resume fields
            if "resume_path" in details:
                if "resume" in field_name.lower() or "file" in field_name.lower():
                    return details["resume_path"]
            # Fuzzy and exact match for other fields
            for key, value in details.items():
                match_score = fuzz.partial_ratio(field_name.lower(), key.lower())
                logger.debug(f"Match score for '{field_name}' with '{key}': {match_score}")
                if match_score > 80:
                    logger.debug(f"Matched field '{field_name}' with detail key '{key}' and value '{value}'")
                    return str(value) if value is not None else None
        logger.debug(f"No match found for field '{field_name}' in details")
        return None

    def fill_element(self, element: ElementHandle,
                     field_name: Optional[str] = None, 
                     details: Optional[Dict[str, Any]] = None) -> None:
        """Fill a form element based on its type and the provided details"""
        if not field_name:
            field_name = self.element_utils.determine_field_name(element)
        logger.info(f"Filling element for field '{field_name}'")
        logger.debug(f"Details for field '{field_name}': {details}")
        element_type = self.element_utils.determine_element_type(element)
        logger.debug(f"Element type for field '{field_name}' is '{element_type}'")
        resume_path: Optional[str] = None
        if details and isinstance(details, dict) and "resume_path" in details:
            resume_path = details["resume_path"]
        if resume_path is not None and resume_path != self.resume_path:
            self.resume_path = resume_path
            if self.value_evaluator is not None and self.value_evaluator.content_utils is not None:
                self.value_evaluator.content_utils.set_new_resume_from_path(resume_path)
        # Get raw value from details
        raw_value = FormFilling.get_value_from_details(field_name, details)
        logger.debug(f"Raw value for field '{field_name}': {raw_value}")
        # Evaluate the value using the centralized method
        value = self.value_evaluator.evaluate_value(element_type, field_name, raw_value, element)
        logger.debug(f"Evaluated value for field '{field_name}': {value}")
        # Handle file uploads separately
        if resume_path is not None and raw_value == resume_path:
            page = getattr(element, "_page", None)
            if page is not None:
                self.file_handler.handle_file_upload(page, element, value or self.resume_path)
            else:
                logger.error("Could not determine page for file upload.")
            return
        # Fill the element based on its type
        self.element_handlers.fill_element(element, element_type, field_name, value)
        logger.info(f"Successfully filled element for field '{field_name}'")