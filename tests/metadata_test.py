import pytest
from services.metadata_check import check_sender_domain

def test_valid_domain():
    result = check_sender_domain("gmail.com")
    assert "Valid domain" in result

def test_invalid_domain():
    result = check_sender_domain("fake-domain.example")
    assert "Invalid domain" in result
