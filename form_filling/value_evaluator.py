# form_filling/value_evaluator.py

import logging
from typing import Optional, List
from langchain.chat_models import init_chat_model
from playwright.sync_api import ElementHandle
from form_filling.content_utils import GenerateContentUtils

logger = logging.getLogger(__name__)

class ValueEvaluator:
    
    from langchain.chat_models.base import BaseChatModel

    def __init__(self, content_utils: Optional[GenerateContentUtils] = None,
                 llm: Optional[BaseChatModel] = None,
                 resume_content: Optional[str] = None,
                 resume_path: Optional[str] = None,
                 chat_model_config: Optional[dict] = None):
        if content_utils is None:
            if llm is None:
                llm = init_chat_model(**(chat_model_config or {}))
            self.content_utils: Optional[GenerateContentUtils] = GenerateContentUtils(llm, resume_content, resume_path, chat_model_config)
        else:
            self.content_utils: Optional[GenerateContentUtils] = content_utils
        self.known_types: List[str] = ["text", "email", "tel", "url", "search", "password", "textarea"]
        logger.info("Initialized ValueEvaluator with content utils")
    
    def evaluate_value(self, element_type: str, field_name: str, raw_value: Optional[str], 
                      element: Optional[ElementHandle] = None) -> Optional[str]:
        """Evaluate and generate appropriate value based on element type and field name"""
        logger.debug(f"Evaluating value for field '{field_name}' of type '{element_type}'")
        
        if raw_value is not None:
            logger.debug(f"Using provided value '{raw_value}' for field '{field_name}'")
            return raw_value
            
        # Handle different element types
        if element_type in self.known_types:
            if self.content_utils is not None:
                value = self.content_utils.generate_field_content(field_label=field_name)
                logger.info(f"Generated content for text field '{field_name}'")
                return value
            else:
                logger.warning("content_utils is None")
                return None
            
        elif element_type in ["select", "select-one"] and element:
            options: List[str] = []
            try:
                option_elements = element.query_selector_all("option")
                logger.debug(f"Found {len(option_elements)} options for select field '{field_name}'")
                options_raw = [opt.text_content() for opt in option_elements]
                options: List[str] = [opt for opt in options_raw if opt is not None]
            except Exception as e:
                logger.warning(f"Error getting options for select field '{field_name}': {e}")
                return None
            if options and self.content_utils is not None:
                value = self.content_utils.generate_select_content(options)
                logger.info(f"Generated selection '{value}' for field '{field_name}'")
                return value
            else:
                logger.warning(f"No options found for select field '{field_name}' or content_utils is None")
                return None
            
        elif element_type in ["radio", "radiogroup"] and element:
            option_labels: List[str] = []
            try:
                if element_type == "radio":
                    label = element.get_attribute("aria-label") or element.get_attribute("value")
                    option_labels = [label] if label is not None else []
                else:  # radiogroup
                    radio_buttons = element.query_selector_all("input[type='radio']")
                    option_labels = [label for rb in radio_buttons for label in [rb.get_attribute("aria-label") or rb.get_attribute("value")] if label is not None]
                option_labels_filtered: List[str] = [lbl for lbl in option_labels if lbl is not None]
                logger.debug(f"Radio options for '{field_name}': {option_labels_filtered}")
                if option_labels_filtered and self.content_utils is not None:
                    value = self.content_utils.generate_radio_content(option_labels_filtered)
                    logger.info(f"Generated radio selection '{value}' for field '{field_name}'")
                    return value
                else:
                    logger.warning(f"No radio options found for field '{field_name}' or content_utils is None")
                    return None
            except Exception as e:
                logger.warning(f"Error getting options for radio field '{field_name}': {e}")
                return None
            
        elif element_type in ["checkbox", "checkbox-container"]:
            # Default to not checked for checkboxes unless specified
            logger.debug(f"Default to not checked for checkbox field '{field_name}'")
            return None
            
        elif element_type == "file":
            logger.debug(f"Using resume path for file upload field '{field_name}'")
            if self.content_utils is not None:
                return getattr(self.content_utils, "resume_path", None)
            return None
            
        # Default fallback
        logger.warning(f"No specific evaluation method for element type '{element_type}', returning None")
        return None