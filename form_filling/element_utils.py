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

        known_types = [
            "text",
            "select",
            "select-one",
            "textarea",
            "radio",
            "checkbox",
            "fieldset",
        ]
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
            tmp = next(
                (x for x in [element_id, element_class, element_name] if x is not None),
                None,
            )
            element_match = next(
                (curr for curr in known_types if tmp and curr in tmp), None
            )
            if element_match:
                logger.debug(
                    f"Element type evaluated using id/class/name attribute: {tmp} to {element_match}"
                )
                return element_match
            else:
                logger.error(
                    f"Cannot determine element typw with tag {tag_name}.\n element: {element}"
                )
                return tag_name

        # Check for radiogroup role
        role = element.get_attribute("role")
        if role == "radiogroup":
            logger.debug("Element has role=radiogroup")
            return "radiogroup"

        # Check for checkbox container
        if element.query_selector("input[type='checkbox']"):
            logger.debug("Element is a checkbox container")
            return "checkbox-container"

        logger.error(f"Cannot determine element type: {element}")
        raise Exception(f"Cannot determine element type: {element}")

    def determine_field_name(self, element: ElementHandle) -> str:
        """Extract the most appropriate name for the field from various attributes"""

        # First, try direct attributes (most reliable)
        for attr in ["name", "id", "aria-label", "data-testid"]:
            attr_value = element.get_attribute(attr)
            if attr_value and attr_value.strip():
                logger.debug(f"Found field name '{attr_value}' via {attr} attribute")
                return attr_value.strip()

        # Try aria-labelledby reference
        aria_labelledby = element.get_attribute("aria-labelledby")
        if aria_labelledby:
            try:
                page = element.page
                referenced_element = page.locator(f"#{aria_labelledby}")
                label_text = referenced_element.text_content()
                if label_text and label_text.strip():
                    name = label_text.strip()
                    logger.debug(f"Found field name '{name}' via aria-labelledby reference")
                    return name
            except Exception as e:
                logger.warning(f"Failed to get text from aria-labelledby element: {e}")

        # Look for associated label element
        id_value = element.get_attribute("id")
        if id_value:
            try:
                page = element.page
                label = page.locator(f"label[for='{id_value}']")
                if label.count() > 0:
                    label_text = label.first.text_content()
                    if label_text and label_text.strip():
                        name = label_text.strip()
                        logger.debug(f"Found field name '{name}' via associated label")
                        return name
            except Exception as e:
                logger.warning(f"Failed to get text from associated label: {e}")

        # Try to extract meaningful text from parent elements
        try:
            # Look for text in immediate parent
            parent = element.evaluate("el => el.parentElement")
            if parent:
                parent_element = element.page.locator("xpath=..").first
                parent_text = parent_element.inner_text()
                if parent_text and parent_text.strip():
                    # Clean up the text - remove common form artifacts
                    cleaned_text = self._clean_field_name(parent_text.strip())
                    if cleaned_text and len(cleaned_text) < 100:  # Reasonable length check
                        logger.debug(f"Found field name '{cleaned_text}' from parent element text")
                        return cleaned_text
        except Exception as e:
            logger.debug(f"Failed to get text from parent element: {e}")

        # Fallback to placeholder
        placeholder = element.get_attribute("placeholder")
        if placeholder and placeholder.strip():
            logger.debug(f"Using placeholder '{placeholder}' as field name")
            return placeholder.strip()

        # Last resort: try class attribute for meaningful names
        class_attr = element.get_attribute("class")
        if class_attr and class_attr.strip():
            # Look for meaningful class names
            classes = class_attr.split()
            for cls in classes:
                if any(keyword in cls.lower() for keyword in ['name', 'email', 'phone', 'address', 'field']):
                    logger.debug(f"Using class '{cls}' as field name")
                    return cls

        logger.warning("Could not determine field name, using 'unknown'")
        return "unknown"

    def _clean_field_name(self, text: str) -> str:
        """Clean and extract meaningful field name from text content"""
        if not text:
            return ""
        
        # Remove common form artifacts and clean up
        text = text.replace("*", "").replace(":", "").strip()
        
        # If text contains multiple lines, take the first meaningful line
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            # Take the shortest non-empty line (likely the label)
            text = min(lines, key=len)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
