# tests\test_content_generator.py

import pytest
from form_filling.content_utils import GenerateContentUtils

class TestUtils:
    def test_generate_field_content(self, content_utils_fixture: GenerateContentUtils, load_env) -> None:
        field_label = "How many years of work experience do you have?"
        result = content_utils_fixture.generate_field_content(None, field_label)
        print(result)
        assert result is not None
        assert result.isdigit()

    def test_generate_radio_content(self, content_utils_fixture: GenerateContentUtils, load_env) -> None:
        option_labels = ["Yes", "No"]
        resume_content = "Have you completed the following level of education: Bachelor's Degree?"
        result = content_utils_fixture.generate_radio_content(None, option_labels, resume_content)
        print(result)
        assert result in option_labels

    def test_generate_select_content(self, content_utils_fixture: GenerateContentUtils, load_env) -> None:
        options = ["None", "Conversational", "Professional", "Native or Bilingual"]
        resume_content = "What is your level of proficiency in English?"
        result = content_utils_fixture.generate_select_content(None, options, resume_content)
        print(result)
        assert result in options