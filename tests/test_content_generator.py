# tests\test_content_generator.py

from unittest.mock import MagicMock
from form_filling.content_utils import GenerateContentUtils


class TestUtils:
    def test_generate_field_content(
        self, content_utils_fixture: GenerateContentUtils, load_env
    ) -> None:
        field_label = "How many years of work experience do you have?"
        mock_response = MagicMock()
        mock_response.content = "5"
        content_utils_fixture.llm = MagicMock()
        content_utils_fixture.llm.invoke = MagicMock(return_value=mock_response)
        result = content_utils_fixture.generate_field_content(field_label)
        print(result)
        assert result is not None
        assert str(result).isdigit()

    def test_generate_radio_content(
        self, content_utils_fixture: GenerateContentUtils, load_env
    ) -> None:
        option_labels = ["Yes", "No"]
        resume_content = (
            "Have you completed the following level of education: Bachelor's Degree?"
        )
        mock_response = MagicMock()
        mock_response.content = "Yes"
        content_utils_fixture.llm = MagicMock()
        content_utils_fixture.llm.invoke = MagicMock(return_value=mock_response)
        result = content_utils_fixture.generate_radio_content(
            option_labels, resume_content
        )
        print(result)
        assert result in option_labels

    def test_generate_select_content(
        self, content_utils_fixture: GenerateContentUtils, load_env
    ) -> None:
        options = ["None", "Conversational", "Professional", "Native or Bilingual"]
        resume_content = "What is your level of proficiency in English?"
        mock_response = MagicMock()
        mock_response.content = "Professional"
        content_utils_fixture.llm = MagicMock()
        content_utils_fixture.llm.invoke = MagicMock(return_value=mock_response)
        result = content_utils_fixture.generate_select_content(options, resume_content)
        print(result)
        assert result in options
