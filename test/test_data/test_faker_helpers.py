"""Tests for the lightweight fake-data helpers."""
from __future__ import annotations

import re
import uuid

from je_api_testka.data.faker_helpers import fake_email, fake_uuid, fake_word


def test_fake_uuid_is_valid():
    value = fake_uuid()
    parsed = uuid.UUID(value)
    assert str(parsed) == value


def test_fake_word_length_and_charset():
    word = fake_word(length=12)
    assert len(word) == 12
    assert re.fullmatch(r"[a-z]+", word)


def test_fake_word_minimum_one_char():
    assert len(fake_word(length=0)) == 1


def test_fake_email_format():
    email = fake_email(domain="acme.invalid")
    assert email.endswith("@acme.invalid")
    assert "@" in email
