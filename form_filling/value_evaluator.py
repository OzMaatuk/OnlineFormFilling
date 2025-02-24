# form_filling/value_evaluator.py

import logging
from typing import Optional, List
from llm_utils import LLMUtils
from playwright.sync_api import ElementHandle
from form_filling.content_utils import GenerateContentUtils

logger = logging.getLogger(__name__)

class ValueEvaluator:
    
    def __init__(self, content_utils: GenerateContentUtils = None,
                 llm: LLMUtils = None,
                 resume_content: str = None,
                resume_path: str = None):
        if content_utils == None:
            self.content_utils = GenerateContentUtils(llm, resume_content, resume_path)
        else:
            self.content_utils = content_utils
        self.known_types = ["text", "email", "tel", "url", "search", "password", "textarea"]
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
            value = self.content_utils.generate_field_content(field_label=field_name)
            logger.info(f"Generated content for text field '{field_name}'")
            return value
            
        elif element_type in ["select", "select-one"] and element:
            options: List[str] = []
            try:
                option_elements = element.query_selector_all("option")
                logger.debug(f"Found {len(option_elements)} options for select field '{field_name}'")
                options = [opt.text_content() for opt in option_elements if opt.text_content()]
            except Exception as e:
                logger.warning(f"Error getting options for select field '{field_name}': {e}")
                
            if options:
                value = self.content_utils.generate_select_content(options)
                logger.info(f"Generated selection '{value}' for field '{field_name}'")
                return value
            else:
                logger.warning(f"No options found for select field '{field_name}'")
                return None
            
        elif element_type in ["radio", "radiogroup"] and element:
            try:
                if element_type == "radio":
                    label = element.get_attribute("aria-label") or element.get_attribute("value")
                    option_labels = [label, "None"] if label else ["None"]
                    logger.debug(f"Radio options for '{field_name}': {option_labels}")
                else:  # radiogroup
                    radio_buttons = element.query_selector_all("input[type='radio']")
                    logger.debug(f"Found {len(radio_buttons)} radio buttons in group '{field_name}'")
                    option_labels = []
                    for radio in radio_buttons:
                        label = radio.get_attribute("aria-label") or radio.get_attribute("value")
                        if label:
                            option_labels.append(label)
                
                if option_labels:
                    value = self.content_utils.generate_radio_content(option_labels)
                    logger.info(f"Generated radio selection '{value}' for field '{field_name}'")
                    return value
                else:
                    logger.warning(f"No options found for radio field '{field_name}'")
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
            return self.content_utils.resume_path
            
        # Default fallback
        logger.warning(f"No specific evaluation method for element type '{element_type}', returning None")
        return None