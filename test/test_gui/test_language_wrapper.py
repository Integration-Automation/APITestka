"""Tests for the multi-language wrapper."""
from __future__ import annotations

from je_api_testka.gui.language_wrapper.english import english_word_dict
from je_api_testka.gui.language_wrapper.japanese import japanese_word_dict
from je_api_testka.gui.language_wrapper.multi_language_wrapper import LanguageWrapper
from je_api_testka.gui.language_wrapper.simplified_chinese import simplified_chinese_word_dict
from je_api_testka.gui.language_wrapper.traditional_chinese import traditional_chinese_word_dict


def test_all_locale_dicts_share_keys():
    """Every locale must cover all English keys to avoid runtime KeyErrors."""
    base_keys = set(english_word_dict)
    for locale in (japanese_word_dict, simplified_chinese_word_dict, traditional_chinese_word_dict):
        missing = base_keys - set(locale)
        assert not missing, f"locale missing keys: {missing}"


def test_default_language_is_english():
    wrapper = LanguageWrapper()
    assert wrapper.language == "English"
    assert wrapper.language_word_dict["application_name"] == "APITestka"


def test_reset_language_switches_dict():
    wrapper = LanguageWrapper()
    wrapper.reset_language("Japanese")
    assert wrapper.language == "Japanese"
    assert wrapper.language_word_dict is japanese_word_dict
    wrapper.reset_language("Simplified_Chinese")
    assert wrapper.language_word_dict is simplified_chinese_word_dict


def test_reset_language_ignores_unknown():
    wrapper = LanguageWrapper()
    wrapper.reset_language("Klingon")
    assert wrapper.language == "English"
