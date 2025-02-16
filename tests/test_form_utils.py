# tests/test_form_utils.py

import pytest
from src.utils.form_utils import get_value_from_details

def test_get_value_from_details_exact_match(form_page):
    details = {
        "name": "John Doe",
        "email": "john.doe@example.com"
    }
    field_name = "name"
    result = get_value_from_details(field_name, details)
    assert result == "John Doe"

def test_get_value_from_details_partial_match(form_page):
    details = {
        "full name": "John Doe",
        "email address": "john.doe@example.com"
    }
    field_name = "name"
    result = get_value_from_details(field_name, details)
    assert result == "John Doe"

def test_get_value_from_details_no_match(form_page):
    details = {
        "email": "john.doe@example.com",
        "phone": "123-456-7890"
    }
    field_name = "name"
    result = get_value_from_details(field_name, details)
    assert result is None

def test_get_value_from_details_case_insensitive(form_page):
    details = {
        "Name": "John Doe",
        "Email": "john.doe@example.com"
    }
    field_name = "name"
    result = get_value_from_details(field_name, details)
    assert result == "John Doe"

def test_get_value_from_details_high_similarity(form_page):
    details = {
        "full name": "John Doe",
        "email address": "john.doe@example.com"
    }
    field_name = "fullname"
    result = get_value_from_details(field_name, details)
    assert result == "John Doe"