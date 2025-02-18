# form_filling/value_evaluator.py

import logging
from playwright.sync_api import ElementHandle
from form_filling.content_utils import GenerateContentUtils

logger = logging.getLogger(__name__)

class ValueEvaluator:
    
    def __init__(self, content_utils: GenerateContentUtils):
        self.content_utils = content_utils
    
    def evaluate_value(self, element_type: str, field_name: str, raw_value: str, element: ElementHandle = None) -> str:
        """Evaluate and generate appropriate value based on element type and field name"""
        logger.debug(f"Evaluating value for field '{field_name}' of type '{element_type}'")
        
        if raw_value is not None:
            logger.debug(f"Using provided value '{raw_value}' for field '{field_name}'")
            return raw_value
            
        # Handle different element types
        if element_type in ["text", "email", "tel", "url", "search", "password", "textarea"]:
            return self.content_utils.generate_field_content(field_label=field_name)
            
        elif element_type in ["select", "select-one"] and element:
            options = [opt.text_content() for opt in element.query_selector_all("option")]
            return self.content_utils.generate_select_content(options)
            
        elif element_type in ["radio", "radiogroup"] and element:
            if element_type == "radio":
                label = element.get_attribute("aria-label") or element.get_attribute("value")
                option_labels = [label, "None"] if label else ["None"]
            else:  # radiogroup
                radio_buttons = element.query_selector_all("input[type='radio']")
                option_labels = []
                for radio in radio_buttons:
                    label = radio.get_attribute("aria-label") or radio.get_attribute("value")
                    if label:
                        option_labels.append(label)
            
            return self.content_utils.generate_radio_content(option_labels)
            
        elif element_type in ["checkbox", "checkbox-container"]:
            # Default to not checked for checkboxes unless specified
            return None
            
        elif element_type == "file":
            return self.content_utils.resume_path
            
        # Default fallback
        logger.warning(f"No specific evaluation method for element type '{element_type}', returning None")
        return None