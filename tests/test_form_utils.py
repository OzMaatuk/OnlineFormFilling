# # file path: tests/test_form_filling.py

import pytest
import logging
from unittest.mock import MagicMock, patch
from form_filling.form_filling import FormFilling
from form_filling.utils import GenerateContentUtils

logger = logging.getLogger(__name__)

# Constants for tests
MOCK_RESUME_CONTENT = """
John Doe
john.doe@example.com
(123) 456-7890
Software Engineer with 5 years of experience
"""
MOCK_RESUME_PATH = "data/personal/resume.pdf"

# # Basic functionality tests

def test_initialization(form_filling):
    assert form_filling.content_utils is not None
    assert isinstance(form_filling.content_utils, GenerateContentUtils)

def test_get_value_from_details():
    details = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone number": "123-456-7890"
    }
    
    # Exact match
    assert FormFilling.get_value_from_details("email", details) == "john.doe@example.com"
    
    # Fuzzy match
    assert FormFilling.get_value_from_details("phone", details) == "123-456-7890"
    
    # No match
    assert FormFilling.get_value_from_details("address", details) is None

def test_fill_text_element(form_filling, mock_element):
    details = {"test_field": "test value"}
    form_filling.fill_element(mock_element, "test_field", details)
    mock_element.fill.assert_called_once_with("test value")

def test_fill_element_no_value_in_details(form_filling, mock_element):
    mock_element.return_value = "generated content"

    with patch.object(form_filling.content_utils, 'generate_field_content', return_value="generated content") as mock_generate:
        form_filling.fill_element(mock_element, "test_field", {})
        mock_generate.assert_called_once_with(field_label='test_field')
        mock_element.fill.assert_called_once_with("generated content")

# Specific element type tests

def test_fill_textarea(form_filling, mock_element):
    mock_element.evaluate.return_value = "textarea"
    details = {"test_field": "This is a long biography text"}
    form_filling.fill_element(mock_element, "test_field", details)
    mock_element.fill.assert_called_once_with("This is a long biography text")

def test_fill_select(form_filling, mock_element):
    mock_element.evaluate.return_value = "select-one"
    mock_options = [MagicMock() for _ in range(3)]
    for i, opt in enumerate(mock_options):
        opt.text_content.return_value = f"Option {i}"
    mock_element.query_selector_all.return_value = mock_options
    
    # First case: with value
    details = {"test_field": "Option 1"}
    form_filling.fill_element(mock_element, "test_field", details)
    mock_element.select_option.assert_called_once_with(label="Option 1")
    mock_element.reset_mock()
    
    # Second case: without value in details
    with patch.object(form_filling.content_utils, 'generate_select_content', return_value="Option 2") as mock_generate:
        form_filling.fill_element(mock_element, "different_field")  # Use different field name and empty details
        mock_generate.assert_called_once_with(["Option 0", "Option 1", "Option 2"])
        mock_element.select_option.assert_called_once_with(label="Option 2")

def test_fill_radio(form_filling, mock_element):
    mock_element.evaluate.return_value = "radio"
    mock_option_0 = MagicMock()
    mock_option_0.get_attribute.return_value = "Radio 0"
    mock_option_1 = MagicMock()
    mock_option_1.get_attribute.return_value = "Radio 1"
    mock_options = [mock_option_0, mock_option_1]
    mock_element.query_selector_all.return_value = mock_options
    
    # First case: with value in details
    details = {"test_field": "Radio 1"}
    form_filling.fill_element(mock_element, "test_field", details)
    mock_options[1].click.assert_called_once()
    
    # Reset mocks for next test
    for opt in mock_options:
        opt.reset_mock()
    
    # Second case: without value in details
    with patch.object(form_filling.content_utils, 'generate_radio_content', return_value="Radio 0") as mock_generate:
        form_filling.fill_element(mock_element, "unknown_field", {})  # Use different field to ensure no match
        mock_generate.assert_called_once_with(["Radio 0", "Radio 1"])
        mock_options[0].click.assert_called_once()

def test_fill_checkbox(form_filling, mock_element):
    mock_element.evaluate.return_value = "checkbox"
    
    # First case: check
    details = {"test_field": "true"}
    form_filling.fill_element(mock_element, "test_field", details)
    mock_element.check.assert_called_once()
    mock_element.uncheck.assert_not_called()
    
    # Reset mock for next test
    mock_element.reset_mock()
    
    # Second case: uncheck (empty value)
    details = {"test_field": ""}
    form_filling.fill_element(mock_element, "test_field", details)
    mock_element.uncheck.assert_called_once()
    mock_element.check.assert_not_called()
    
    # Reset mock for next test
    mock_element.reset_mock()
    
    # Third case: no value in details - should call generate_field_content
    form_filling.fill_element(mock_element, "unknown_field", {})
    mock_element.uncheck.assert_called_once()
    mock_element.check.assert_not_called()

# Integration tests with the actual form_page fixture

def test_fill_form_email_field(form_filling, form_page):
    email_element = form_page.locator("#email").element_handle()
    form_filling.fill_element(email_element, "email", {"email": "john.doe@example.com"})
    assert form_page.locator("#email").input_value() == "john.doe@example.com"

def test_fill_form_phone_field(form_filling, form_page):
    phone_element = form_page.locator("#phone").element_handle()
    form_filling.fill_element(phone_element, "phone", {"phone": "123-456-7890"})
    assert form_page.locator("#phone").input_value() == "123-456-7890"

def test_fill_form_textarea(form_filling, form_page):
    bio_element = form_page.locator("#bio").element_handle()
    bio_text = "Software engineer with 5 years experience in Python development."
    form_filling.fill_element(bio_element, "bio", {"bio": bio_text})
    assert form_page.locator("#bio").input_value() == bio_text

def test_fill_form_select(form_filling, form_page):
    select_element = form_page.locator("#country").element_handle()
    form_filling.fill_element(select_element, "country", {"country": "Canada"})
    assert form_page.locator("#country").evaluate("el => el.options[el.selectedIndex].text") == "Canada"

def test_fill_form_radio(form_filling, form_page):
    gender_field = form_page.wait_for_selector("[role='radiogroup']")
    form_filling.fill_element(gender_field, "gender", {"gender": "Female"})
    assert form_page.locator("#gender_female").is_checked()

def test_fill_form_checkbox(form_filling, form_page):
    checkbox_element = form_page.locator("#subscribe").element_handle()
    form_filling.fill_element(checkbox_element, "subscribe", {"subscribe": "true"})
    assert form_page.locator("#subscribe").is_checked()

# Edge cases

def test_fill_element_no_field_name(form_filling, mock_element):
    details = {"test_id": "test value"}
    form_filling.fill_element(mock_element, None, details)
    mock_element.fill.assert_called_once_with("test value")

def test_fill_element_unknown_type(form_filling, mock_element):
    mock_element.evaluate.return_value = "unknown-type"
    details = {"test_field": "test value"}
    form_filling.fill_element(mock_element, "test_field", details)
    mock_element.fill.assert_called_once_with("test value")

def test_fill_element_empty_details(form_filling, mock_element):
    with patch.object(form_filling.content_utils, 'generate_field_content', return_value="generated content"):
        form_filling.fill_element(mock_element, "test_field", {})
        mock_element.fill.assert_called_once_with("generated content")

def test_handle_file_upload(form_filling_with_path, form_page):
    # Create a mock for file_chooser to avoid actual file upload
    mock_file_chooser = MagicMock()
    file_element = form_page.locator("input[type='file']").element_handle()
    
    # Since we don't have a real file input in our example, this is more of a unit test
    with patch.object(form_page, 'expect_file_chooser') as mock_expect:
        mock_expect.return_value.__enter__.return_value.value = mock_file_chooser
        FormFilling.handle_file_upload(form_page, file_element, MOCK_RESUME_PATH)
        mock_file_chooser.set_files.assert_called_once_with(MOCK_RESUME_PATH)

def test_fill_form_non_existent_element(form_filling, form_page):
    with pytest.raises(Exception):
        non_existent = form_page.locator("#non-existent").element_handle()
        form_filling.fill_element(non_existent, "non-existent", {})