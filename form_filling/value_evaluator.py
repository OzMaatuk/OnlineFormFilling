# form_filling/value_evaluator.py

import logging
from typing import Optional, List, Union
from playwright.sync_api import ElementHandle
from form_filling.content_utils import GenerateContentUtils
from langchain.chat_models.base import BaseChatModel

logger = logging.getLogger(__name__)


class ValueEvaluator:

    def __init__(
        self,
        content_utils: Optional[GenerateContentUtils] = None,
        llm: Optional[Union[BaseChatModel, dict]] = None,
        resume: Optional[str] = None,
    ):
        logger.info("Init ValueEvaluator")
        logger.debug(
            f"with content_utils: {content_utils}, llm: {llm}, resume: {resume}"
        )
        if content_utils is None:
            self.content_utils: GenerateContentUtils = GenerateContentUtils(llm, resume)
        else:
            self.content_utils: GenerateContentUtils = content_utils
        self.known_types: List[str] = [
            "text",
            "email",
            "tel",
            "url",
            "search",
            "password",
            "textarea",
        ]
        logger.info("ValueEvaluator Initialized")

    def evaluate_value(
        self,
        element_type: str,
        field_name: str,
        raw_value: Optional[str],
        element: Optional[ElementHandle] = None,
    ) -> Optional[str]:
        """Evaluate and generate appropriate value based on element type and field name"""
        logger.debug(
            f"Evaluating value for field '{field_name}' of type '{element_type}'"
        )

        if raw_value:
            logger.debug(f"Using provided value '{raw_value}' for field '{field_name}'")
            return raw_value

        # Handle different element types
        if element_type in self.known_types:
            if self.content_utils is not None:
                value = self.content_utils.generate_field_content(
                    field_label=field_name
                )
                logger.info(f"Generated content for text field '{field_name}'")
                return value
            else:
                logger.warning("content_utils is None")
                return None

        elif element_type in ["select", "select-one"] and element:
            options: List[str] = []
            try:
                option_elements = element.query_selector_all("option")
                logger.debug(
                    f"Found {len(option_elements)} options for select field '{field_name}'"
                )
                options_raw = [opt.text_content() for opt in option_elements]
                options = [opt for opt in options_raw if opt is not None]
            except Exception as e:
                logger.warning(
                    f"Error getting options for select field '{field_name}': {e}"
                )
                return None
            if options and self.content_utils is not None:
                value = self.content_utils.generate_select_content(options)
                logger.info(f"Generated selection '{value}' for field '{field_name}'")
                return value
            else:
                logger.warning(
                    f"No options found for select field '{field_name}' or content_utils is None"
                )
                return None

        elif element_type in ["radio", "radiogroup", "fieldset"] and element:
            if element_type == "fieldset":
                field_name = element.inner_text()
            option_labels: List[str] = []
            try:
                if element_type == "radio":
                    label = element.get_attribute(
                        "aria-label"
                    ) or element.get_attribute("value")
                    option_labels = [label] if label is not None else []
                else:  # radiogroup
                    # Handle both standard and LinkedIn-specific radio groups
                    radio_buttons = element.query_selector_all(
                        "input[type='radio'], input[data-test-text-selectable-option__input]"
                    )
                    option_labels_raw = [
                        rb.get_attribute("data-test-text-selectable-option__input")
                        or rb.get_attribute("aria-label")
                        or rb.get_attribute("value")
                        for rb in radio_buttons
                    ]
                    option_labels = [
                        lbl for lbl in option_labels_raw if lbl is not None
                    ]
                logger.debug(f"Radio options for '{field_name}': {option_labels}")

                if option_labels and self.content_utils is not None:
                    value = self.content_utils.generate_radio_content(option_labels)
                    logger.info(
                        f"Generated radio selection '{value}' for field '{field_name}'"
                    )
                    return value
                else:
                    logger.warning(
                        f"No radio options found for field '{field_name}' or content_utils is None"
                    )
                    return None
            except Exception as e:
                logger.warning(
                    f"Error getting options for radio field '{field_name}': {e}"
                )
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
        logger.warning(
            f"No specific evaluation method for element type '{element_type}', returning None"
        )
        return None
