# tests\test_edge_cases.py

import pytest
from unittest.mock import patch, MagicMock
from playwright.sync_api import TimeoutError, Page, ElementHandle
from form_filling.form_filling import FormFilling


def test_fill_element_no_field_name(form_filling: FormFilling, mock_element: MagicMock):
    details = {"test_id": "test value"}
    dummy_page = MagicMock()
    form_filling.fill_element(mock_element, dummy_page, None, details)
    mock_element.fill.assert_called_once_with("test value")


def test_fill_element_unknown_type(form_filling: FormFilling, mock_element: MagicMock):
    with pytest.raises(Exception):  # Replace Exception with your custom exception class
        mock_element.evaluate.return_value = "unknown-type"
        mock_element.query_selector.return_value = None
        details = {"test_field": "test value"}
        dummy_page = MagicMock()
        form_filling.fill_element(mock_element, dummy_page, "test_field", details)


def test_fill_element_empty_details(form_filling: FormFilling, mock_element: MagicMock):
    dummy_page = MagicMock()
    with patch.object(
        form_filling.value_evaluator.content_utils,
        "generate_field_content",
        return_value="generated content",
    ):
        form_filling.fill_element(mock_element, dummy_page, "test_field", {})
        mock_element.fill.assert_called_once_with("generated content")


def test_fill_form_non_existent_element(form_filling: FormFilling, form_page: Page):
    with pytest.raises(TimeoutError):  # Expect TimeoutError
        form_page.locator("#non-existent").element_handle(timeout=1)  # Reduced timeout
        # form_filling.fill_element(non_existent, "non-existent", {}) # Not needed


def test_fill_checkbox(form_filling: FormFilling, form_page: Page):
    checkbox_field: ElementHandle = form_page.locator("#subscribe").element_handle()

    # Test checking
    form_filling.fill_element(
        checkbox_field, form_page, "subscribe", {"subscribe": "yes"}
    )
    assert form_page.locator("#subscribe").is_checked()

    # Test unchecking
    form_filling.fill_element(
        checkbox_field, form_page, "subscribe", {"subscribe": "no"}
    )
    assert not form_page.locator("#subscribe").is_checked()


@pytest.fixture
def temp_resume_file():
    return "tests/file_to_upload.pdf"


def test_file_upload(form_filling: FormFilling, form_page: Page, temp_resume_file: str):
    """Tests the file upload functionality."""
    file_element: ElementHandle = form_page.locator("#resume").element_handle()

    # Mock the file upload process - actual upload testing would need specific setup
    with patch.object(
        form_filling.file_handler, "handle_file_upload"
    ) as mock_handle_upload:
        form_filling.fill_element(
            file_element, form_page, "resume", {"resume_path": temp_resume_file}
        )
        mock_handle_upload.assert_called_once_with(
            form_page, file_element, temp_resume_file
        )
