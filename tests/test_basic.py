# tests/test_basic.py

from unittest.mock import patch, MagicMock
from form_filling.form_filling import FormFilling
from form_filling.content_utils import GenerateContentUtils


def test_initialization(form_filling: FormFilling):
    # No content_utils attribute in FormFilling anymore; check ValueEvaluator
    assert hasattr(form_filling.value_evaluator, "content_utils")
    assert isinstance(form_filling.value_evaluator.content_utils, GenerateContentUtils)


def test_get_value_from_details():
    details = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone number": "123-456-7890",
    }

    # Exact match
    assert (
        FormFilling.get_value_from_details("email", details) == "john.doe@example.com"
    )

    # Fuzzy match
    assert FormFilling.get_value_from_details("phone", details) == "123-456-7890"

    # No match
    assert FormFilling.get_value_from_details("address", details) is None


def test_fill_text_element(form_filling: FormFilling, mock_element: MagicMock):
    details = {"test_field": "test value"}
    dummy_page = MagicMock()
    form_filling.fill_element(mock_element, dummy_page, "test_field", details)
    mock_element.fill.assert_called_once_with("test value")


def test_fill_element_no_value_in_details(
    form_filling: FormFilling, mock_element: MagicMock
):
    mock_element.return_value = "generated content"
    dummy_page = MagicMock()
    # Patch ValueEvaluator's content_utils.generate_field_content
    with patch.object(
        form_filling.value_evaluator.content_utils,
        "generate_field_content",
        return_value="generated content",
    ) as mock_generate:
        form_filling.fill_element(mock_element, dummy_page, "test_field", {})
        mock_generate.assert_called_once_with(field_label="test_field")
        mock_element.fill.assert_called_once_with("generated content")
