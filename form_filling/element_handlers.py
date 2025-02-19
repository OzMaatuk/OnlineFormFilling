# form_filling/element_handlers.py

import logging
from typing import Optional, Dict, Callable
from fuzzywuzzy import fuzz
from playwright.sync_api import ElementHandle

logger = logging.getLogger(__name__)

class ElementHandlers:
    
    def __init__(self):
        logger.info("Initialized ElementHandlers with content utils")
    
    def fill_element(self, element: ElementHandle, element_type: str, field_name: str, 
                     value: Optional[str]) -> None:
        """Dispatch to appropriate fill method based on element type"""
        fill_methods: Dict[str, Callable] = {
            "text": self._fill_text,
            "email": self._fill_text,
            "tel": self._fill_text,
            "url": self._fill_text,
            "search": self._fill_text,
            "password": self._fill_text,
            "radio": self._fill_radio,
            "checkbox": self._fill_checkbox,
            "textarea": self._fill_text,
            "select-one": self._fill_select,
            "select": self._fill_select,
            "radiogroup": self._fill_radiogroup,
            "checkbox-container": self._fill_checkbox_container
        }
        
        fill_method = fill_methods.get(element_type, self._fill_text)
        logger.debug(f"Using fill method '{fill_method.__name__}' for field '{field_name}'")
        fill_method(element, field_name, value)
    
    def _fill_text(self, element: ElementHandle, field_name: str, value: Optional[str]) -> None:
        """Fill a text-like input field"""
        actual_value = value or ""
        element.fill(actual_value)
        logger.info(f"Filled text field '{field_name}' with value '{actual_value}'")

    def _fill_select(self, element: ElementHandle, field_name: str, value: Optional[str]) -> None:
        """Select an option from a dropdown menu"""
        if value:
            element.select_option(label=value)
            logger.info(f"Selected option '{value}' for select element '{field_name}'")
        else:
            logger.warning(f"No value provided for select field '{field_name}'")

    def _fill_radio(self, element: ElementHandle, field_name: str, value: Optional[str]) -> None:
        """Check a radio button if value indicates it should be selected"""
        if value and value != "None":
            element.click()
            logger.info(f"Checked radio button '{field_name}' with value '{value}'")
        else:
            logger.debug(f"Not checking radio button '{field_name}' (value: {value})")
    
    def _fill_radiogroup(self, element: ElementHandle, field_name: str, value: Optional[str]) -> None:
        """Select the appropriate radio button in a group"""
        if not value:
            logger.warning(f"No value provided for radiogroup '{field_name}'")
            return
            
        radio_buttons = element.query_selector_all("input[type='radio']")
        logger.debug(f"Found {len(radio_buttons)} radio buttons in group '{field_name}'")
        
        for radio in radio_buttons:
            label = radio.get_attribute("aria-label") or radio.get_attribute("value")
            if label and label == value:
                radio_field_name = f"{field_name} - {label}"
                self._fill_radio(radio, radio_field_name, "true")
                return
                
        logger.warning(f"Failed to find radio option '{value}' in group '{field_name}'")

    def _fill_checkbox(self, element: ElementHandle, field_name: str, value: Optional[str]) -> None:
        """Check or uncheck a checkbox based on value"""
        should_check = value and value.lower() in ["true", "yes", "1", "on"]
        if should_check:
            element.check()
            logger.info(f"Checked checkbox '{field_name}'")
        else:
            element.uncheck()
            logger.info(f"Unchecked checkbox '{field_name}'")

    def _fill_checkbox_container(self, element: ElementHandle, field_name: str, value: Optional[str]) -> None:
        """Find and check the appropriate checkbox in a container"""
        if not value:
            logger.warning(f"No value provided for checkbox container '{field_name}'")
            return
            
        checkboxes = element.query_selector_all("input[type='checkbox']")
        logger.debug(f"Found {len(checkboxes)} checkboxes in container '{field_name}'")
        
        if len(checkboxes) == 0:
            logger.warning(f"No checkboxes found in container '{field_name}'")
            return
            
        for checkbox in checkboxes:
            cb_label = checkbox.get_attribute("aria-label") or checkbox.get_attribute("value") or checkbox.get_attribute("id")
            if cb_label and fuzz.partial_ratio(value.lower(), cb_label.lower()) > 80:
                checkbox_field_name = f"{field_name} - {cb_label}"
                logger.debug(f"Found matching checkbox '{checkbox_field_name}' for value '{value}'")
                self._fill_checkbox(checkbox, checkbox_field_name, "true")
                return
                
        logger.warning(f"No checkbox found in container '{field_name}' matching value '{value}'")