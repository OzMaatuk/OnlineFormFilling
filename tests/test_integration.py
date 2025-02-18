import pytest
from unittest.mock import MagicMock, patch

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

def test_handle_file_upload(form_filling, form_page):
    MOCK_RESUME_PATH = "data/personal/resume.pdf"
    # Create a mock for file_chooser to avoid actual file upload
    mock_file_chooser = MagicMock()
    file_element = form_page.locator("input[type='file']").element_handle()
    
    # Since we don't have a real file input in our example, this is more of a unit test
    with patch.object(form_page, 'expect_file_chooser') as mock_expect:
        mock_expect.return_value.__enter__.return_value.value = mock_file_chooser
        form_filling.file_handler.handle_file_upload(form_page, file_element, MOCK_RESUME_PATH)
        mock_file_chooser.set_files.assert_called_once_with(MOCK_RESUME_PATH)
