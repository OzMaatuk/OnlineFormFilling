# tests\test_element_types.py

import pytest
from unittest.mock import MagicMock, patch
from form_filling.form_filling import FormFilling
from playwright.sync_api import ElementHandle, Page
from typing import List

def test_fill_textarea(form_filling: FormFilling, mock_element: MagicMock):
    mock_element.evaluate.return_value = "textarea"
    details = {"test_field": "This is a long biography text"}
    dummy_page = MagicMock()
    form_filling.fill_element(mock_element, dummy_page, "test_field", details)
    mock_element.fill.assert_called_once_with("This is a long biography text")


def test_fill_select(form_filling: FormFilling, mock_element: MagicMock):
    mock_element.evaluate.return_value = "select-one"
    mock_options: List[MagicMock] = [MagicMock() for _ in range(3)]
    for i, opt in enumerate(mock_options):
        opt.text_content.return_value = f"Option {i}"
    mock_element.query_selector_all.return_value = mock_options

    # First case: with value
    details = {"test_field": "Option 1"}
    dummy_page = MagicMock()
    form_filling.fill_element(mock_element, dummy_page, "test_field", details)
    mock_element.select_option.assert_called_once_with(label="Option 1")
    mock_element.reset_mock()

    # Second case: without value in details
    with patch.object(form_filling.value_evaluator.content_utils, 'generate_select_content',
                      return_value="Option 2") as mock_generate:
        form_filling.fill_element(mock_element, dummy_page, "different_field")  # Use different field name and empty details
        mock_generate.assert_called_once()
        mock_element.select_option.assert_called_once_with(label="Option 2")


def test_fill_radio(form_filling: FormFilling, mock_element: MagicMock):
    mock_element.evaluate.return_value = "radio"
    mock_element.get_attribute.return_value = "Radio 1"

    # First case: with value in details
    details = {"test_field": "Radio 1"}
    dummy_page = MagicMock()
    form_filling.fill_element(mock_element, dummy_page, "test_field", details)
    mock_element.click.assert_called_once()

    mock_element.reset_mock()
    mock_element.get_attribute.side_effect = lambda attr: {
        "name": "test_field",
        "id": "test_id",
        "aria-label": "Radio 1"
    }.get(attr)
    mock_element.evaluate.return_value = "radio"

    # Second case: without value in details
    with patch.object(form_filling.value_evaluator.content_utils, 'generate_radio_content',
                      return_value="Radio 1") as mock_generate:
        form_filling.fill_element(mock_element, dummy_page, "unknown_field", {})  # Use different field to ensure no match
        mock_generate.assert_called_once()
        mock_element.click.assert_called_once()

    mock_element.reset_mock()
    mock_element.get_attribute.side_effect = lambda attr: {
        "name": "test_field",
        "id": "test_id",
        "aria-label": "Radio 1"
    }.get(attr)
    mock_element.evaluate.return_value = "radio"

    # Third case: no click
    with patch.object(form_filling.value_evaluator.content_utils, 'generate_radio_content',
                      return_value="None") as mock_generate:
        form_filling.fill_element(mock_element, dummy_page, "some_field")  # Use different field to ensure no match
        mock_generate.assert_called_once()
        mock_element.click.assert_not_called()


def test_fill_checkbox(form_filling: FormFilling, mock_element: MagicMock):
    mock_element.evaluate.return_value = "checkbox"
    dummy_page = MagicMock()

    # First case: check
    details = {"test_field": "true"}
    form_filling.fill_element(mock_element, dummy_page, "test_field", details)
    mock_element.check.assert_called_once()
    mock_element.uncheck.assert_not_called()

    # Reset mock for next test
    mock_element.reset_mock()

    # Second case: uncheck (empty value)
    details = {"test_field": ""}
    form_filling.fill_element(mock_element, dummy_page, "test_field", details)
    mock_element.uncheck.assert_called_once()
    mock_element.check.assert_not_called()

    # Reset mock for next test
    mock_element.reset_mock()

    # Third case: no value in details - should call generate_field_content
    form_filling.fill_element(mock_element, dummy_page, "unknown_field", {})
    mock_element.uncheck.assert_called_once()
    mock_element.check.assert_not_called()


def test_fill_radiogroup(form_filling: FormFilling, form_page: Page):
    gender_field: ElementHandle = form_page.locator("[role='radiogroup']").element_handle()
    form_filling.fill_element(gender_field, form_page, "gender", {"gender": "Female"})
    assert form_page.locator("#gender_female").is_checked()

    # Test with no pre-defined value, should use LLM to generate a choice
    form_page.reload()  # Reset the form
    with patch.object(form_filling.value_evaluator.content_utils, 'generate_radio_content', return_value="Male") as mock_generate:
        gender_field = form_page.locator("[role='radiogroup']").element_handle()
        form_filling.fill_element(gender_field, form_page, "gender")
        # This assumes the LLM makes a choice - we can't assert the specific value, but we can check that something was selected
        mock_generate.assert_called_once_with(["Male", "Female", "Other", "Prefer not to say"])
        assert form_page.locator("input[name='gender']:checked").count() == 1