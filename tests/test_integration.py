# tests\test_integration.py

import pytest
from unittest.mock import MagicMock, patch
from form_filling.form_filling import FormFilling
from playwright.sync_api import Page, ElementHandle

def test_fill_form_email_field(form_filling: FormFilling, form_page: Page):
    email_element: ElementHandle = form_page.locator("#email").element_handle()
    form_filling.fill_element(email_element, "email", {"email": "john.doe@example.com"})
    assert form_page.locator("#email").input_value() == "john.doe@example.com"

def test_fill_form_phone_field(form_filling: FormFilling, form_page: Page):
    phone_element: ElementHandle = form_page.locator("#phone").element_handle()
    form_filling.fill_element(phone_element, "phone", {"phone": "123-456-7890"})
    assert form_page.locator("#phone").input_value() == "123-456-7890"

def test_fill_form_textarea(form_filling: FormFilling, form_page: Page):
    bio_element: ElementHandle = form_page.locator("#bio").element_handle()
    bio_text = "Software engineer with 5 years experience in Python development."
    form_filling.fill_element(bio_element, "bio", {"bio": bio_text})
    assert form_page.locator("#bio").input_value() == bio_text

def test_fill_form_select(form_filling: FormFilling, form_page: Page):
    select_element: ElementHandle = form_page.locator("#country").element_handle()
    form_filling.fill_element(select_element, "country", {"country": "Canada"})
    assert form_page.locator("#country").evaluate("el => el.options[el.selectedIndex].text") == "Canada"

def test_fill_form_radio(form_filling: FormFilling, form_page: Page):
    gender_field: ElementHandle = form_page.locator("[role='radiogroup']").element_handle()
    form_filling.fill_element(gender_field, "gender", {"gender": "Female"})
    assert form_page.locator("#gender_female").is_checked()

def test_fill_form_checkbox(form_filling: FormFilling, form_page: Page):
    checkbox_element: ElementHandle = form_page.locator("#subscribe").element_handle()
    form_filling.fill_element(checkbox_element, "subscribe", {"subscribe": "true"})
    assert form_page.locator("#subscribe").is_checked()

def test_handle_file_upload(form_filling: FormFilling, form_page: Page):
    # Create a mock for file_chooser to avoid actual file upload
    mock_file_chooser = MagicMock()
    file_element: ElementHandle = form_page.locator("input[type='file']").element_handle()
    MOCK_RESUME_PATH = "data/personal/resume.pdf"

    # Since we don't have a real file input in our example, this is more of a unit test
    with patch.object(form_page, 'expect_file_chooser') as mock_expect:
        mock_expect.return_value.__enter__.return_value.value = mock_file_chooser
        form_filling.file_handler.handle_file_upload(form_page, file_element, MOCK_RESUME_PATH)
        mock_file_chooser.set_files.assert_called_once_with(MOCK_RESUME_PATH)