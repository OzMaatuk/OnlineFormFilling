# form_filling\form_filling.py

import logging
import os.path
from typing import Optional, Dict, Any, Union
from fuzzywuzzy import fuzz
from playwright.sync_api import ElementHandle, Page
from form_filling.element_utils import ElementUtils
from form_filling.value_evaluator import ValueEvaluator
from form_filling.element_handlers import ElementHandlers
from form_filling.file_handler import FileHandler
from langchain.chat_models.base import BaseChatModel
from pathvalidate import is_valid_filepath

logger = logging.getLogger(__name__)


class FormFilling:

    def __init__(
        self,
        llm: Optional[Union[BaseChatModel, dict]] = None,
        resume: Optional[str] = None,
    ):
        logger.info(
            "Initializing FormFilling with LangChain chat model and resume content"
        )

        if isinstance(resume, str):
            if is_valid_filepath(resume):
                if not os.path.exists(resume):
                    raise ValueError(f"Resume file path is invalid: {resume}")
        else:
            raise ValueError(
                f"Resume must be a valid file path or string content, resume: {resume}"
            )
        self.resume = resume
        self.value_evaluator = ValueEvaluator(None, llm, resume)
        self.element_utils = ElementUtils()
        self.element_handlers = ElementHandlers()
        self.file_handler = FileHandler()
        logger.info("FormFilling initialization complete")

    @staticmethod
    def get_value_from_details(
        field_name: str, details: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """Find a value in the details dictionary that matches the field name"""
        logger.debug(
            f"Searching for value matching field '{field_name}' in details dictionary"
        )

        if details:
            # Handle resume_path for file/resume fields
            if "resume_path" in details:
                if "resume" in field_name.lower() or "file" in field_name.lower():
                    return details["resume_path"]
            # Fuzzy and exact match for other fields
            for key, value in details.items():
                match_score = fuzz.partial_ratio(field_name.lower(), key.lower())
                logger.debug(
                    f"Match score for '{field_name}' with '{key}': {match_score}"
                )
                if match_score > 80:
                    logger.debug(
                        f"Matched field '{field_name}' with detail key '{key}' and value '{value}'"
                    )
                    return str(value) if value is not None else None
        logger.debug(f"No match found for field '{field_name}' in details")
        return None

    def fill_element(
        self,
        element: ElementHandle,
        page: Page,
        field_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Fill a form element based on its type and the provided details"""
        logger.info(f"Filling element: {element}, field_name: {field_name}")
        logger.debug(f"Details for filling: {details}")
        if details is None:
            details = {}

        element_type = self.element_utils.determine_element_type(element)
        logger.debug(f"Element type is '{element_type}'")

        if not field_name:
            field_name = self.element_utils.determine_field_name(element)
        logger.debug(f"Filling element for field '{field_name}'")

        resume = details.get("resume_path", None)
        if resume and resume != self.resume:
            self.resume = resume
            if hasattr(self.value_evaluator, "content_utils") and hasattr(
                self.value_evaluator.content_utils, "set_new_resume"
            ):
                self.value_evaluator.content_utils.set_new_resume(resume)

        # Get raw value from details
        raw_value = FormFilling.get_value_from_details(field_name, details)
        logger.debug(f"Raw value for field '{field_name}': {raw_value}")

        # If its resume file upload element, handle it and return.
        if raw_value == self.resume:
            self.file_handler.handle_file_upload(page, element, self.resume)
            return

        # Evaluate the value using the centralized method
        value = self.value_evaluator.evaluate_value(
            element_type, field_name, raw_value, element
        )
        logger.debug(f"Evaluated value for field '{field_name}': {value}")

        # Fill the element based on its type
        self.element_handlers.fill_element(element, element_type, field_name, value)
        logger.info(f"Successfully filled element for field '{field_name}'")
