# form_filling/element_utils.py

import logging
from playwright.sync_api import ElementHandle

logger = logging.getLogger(__name__)

class ElementUtils:
    
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

    def determine_field_name(self, element: ElementHandle) -> str:
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