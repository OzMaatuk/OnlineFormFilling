# form_filling/element_utils.py

import logging
from playwright.sync_api import ElementHandle

logger = logging.getLogger(__name__)

class ElementUtils:
    
    def determine_element_type(self, element: ElementHandle) -> str:
        """Determine the type of form element to handle specialized cases"""
        # First check for tag name to identify basic element type
        tag_name = element.evaluate("el => el.tagName").lower()
        logger.debug(f"Element tag name: {tag_name}")
        
        # For input elements, check type attribute
        if tag_name == "input":
            input_type = element.evaluate("el => el.type")
            logger.debug(f"Input element type: {input_type}")
            return input_type
        
        known_types = ["text", "select", "select-one", "textarea", "radio", "checkbox", "fieldset"]
        if tag_name in known_types:
            logger.debug(f"Element has known tag type: {tag_name}")
            return tag_name        

        if tag_name in ["a", "button", "label"]:
            logger.debug(f"Element is clickable: {tag_name}")
            return "clickable"

        # Determine type by other attributes
        if tag_name == "span":
            element_id = element.get_attribute("id")
            element_class = element.get_attribute("class")
            element_name = element.get_attribute("name")
            tmp = next((x for x in [element_id, element_class, element_name] if x is not None), None)
            element_match = next((curr for curr in known_types if tmp and curr in tmp), None)
            if element_match:
                logger.debug(f"Element type evaluated using id/class/name attribute: {tmp} to {element_match}")
                return element_match
            else:
                logger.error(f"Cannot determine element typw with tag {tag_name}.\n element: {element}")
                return tag_name

        # Check for radiogroup role
        role = element.get_attribute("role")
        if role == "radiogroup":
            logger.debug(f"Element has role=radiogroup")
            return "radiogroup"
        
        # Check for checkbox container
        if element.query_selector("input[type='checkbox']"):
            logger.debug(f"Element is a checkbox container")
            return "checkbox-container"
            
        logger.error(f"Cannot determine element type: {element}")
        raise Exception(f"Cannot determine element type: {element}")

    def determine_field_name(self, element: ElementHandle) -> str:
        """Extract the most appropriate name for the field from various attributes"""
        # Check common attributes for field name
        for attr in ["name", "id", "aria-label", "class", "aria-labelledby", "data-testid"]:
            attr_value = element.get_attribute(attr)
            if attr_value:
                # If this is a labelledby reference, get the text from the referenced element
                if attr == "aria-labelledby":
                    try:
                        page = element.page
                        referenced_element = page.locator(f"#{attr_value}")
                        label_text = referenced_element.text_content()
                        if label_text:
                            name = label_text.strip()
                            logger.debug(f"Found field name '{name}' via aria-labelledby reference")
                            return name
                    except Exception as e:
                        logger.warning(f"Failed to get text from aria-labelledby element: {e}")
                else:
                    logger.debug(f"Found field name '{attr_value}' via {attr} attribute")
                    return attr_value
        
        # Look for an associated label element
        try:
            id_value = element.get_attribute("id")
            if id_value:
                page = element.page
                label = page.locator(f"label[for='{id_value}']")
                if label.count() > 0:
                    name = label.first.text_content().strip()
                    logger.debug(f"Found field name '{name}' via associated label")
                    return name
        except Exception as e:
            logger.warning(f"Failed to get text from associated label: {e}")
        
        # Return placeholder text as a fallback
        placeholder = element.get_attribute("placeholder")
        if placeholder:
            logger.debug(f"Using placeholder '{placeholder}' as field name")
            return placeholder
        
        logger.warning(f"Could not determine field name, using 'unknown'")
        return "unknown"
