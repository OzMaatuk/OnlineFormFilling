import pytest
from unittest.mock import patch

def test_fill_element_no_field_name(form_filling, mock_element):
    details = {"test_id": "test value"}
    form_filling.fill_element(mock_element, None, details)
    mock_element.fill.assert_called_once_with("test value")

def test_fill_element_unknown_type(form_filling, mock_element):
    with pytest.raises(Exception):
        mock_element.evaluate.return_value = "unknown-type"
        mock_element.query_selector.return_value = None
        details = {"test_field": "test value"}
        form_filling.fill_element(mock_element, "test_field", details)
        
def test_fill_element_empty_details(form_filling, mock_element):
    with patch.object(form_filling.content_utils, 'generate_field_content', return_value="generated content"):
        form_filling.fill_element(mock_element, "test_field", {})
        mock_element.fill.assert_called_once_with("generated content")

def test_fill_form_non_existent_element(form_filling, form_page):
    with pytest.raises(Exception):
        non_existent = form_page.locator("#non-existent").element_handle()
        form_filling.fill_element(non_existent, "non-existent", {})

def test_fill_checkbox(form_filling, form_page):
    checkbox_field = form_page.locator("#subscribe").element_handle()
    
    # Test checking
    form_filling.fill_element(checkbox_field, "subscribe", {"subscribe": "yes"})
    assert form_page.locator("#subscribe").is_checked()
    
    # Test unchecking
    form_filling.fill_element(checkbox_field, "subscribe", {"subscribe": "no"})
    assert not form_page.locator("#subscribe").is_checked()

# Commented out as it requires specific setup - you can uncomment and adjust as needed
# def test_file_upload(form_filling, form_page, tmp_path):
#     # Create a temporary file for testing
#     test_file = tmp_path / "test_resume.pdf"
#     test_file.write_bytes(b"Test PDF content")
#     
#     file_field = form_page.locator("#resume").element_handle()
#     # Mock the file upload process - actual upload testing would need specific setup
#     with pytest.monkeypatch.context() as m:
#         # Mock the file_chooser to avoid actual file dialog
#         m.setattr(form_filling, "handle_file_upload", lambda page, element, path: None)
#         form_filling.fill_element(file_field, "resume", {"resume": str(test_file)})
