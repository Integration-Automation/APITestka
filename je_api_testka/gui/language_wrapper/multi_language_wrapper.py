from je_api_testka.gui.language_wrapper.english import english_word_dict
from je_api_testka.gui.language_wrapper.japanese import japanese_word_dict
from je_api_testka.gui.language_wrapper.simplified_chinese import simplified_chinese_word_dict
from je_api_testka.gui.language_wrapper.traditional_chinese import traditional_chinese_word_dict
from je_api_testka.utils.logging.loggin_instance import apitestka_logger


class LanguageWrapper:

    def __init__(
            self
    ):
        apitestka_logger.info("Init LanguageWrapper")
        self.language: str = "English"
        self.choose_language_dict = {
            "English": english_word_dict,
            "Traditional_Chinese": traditional_chinese_word_dict,
            "Japanese": japanese_word_dict,
            "Simplified_Chinese": simplified_chinese_word_dict,
        }
        self.language_word_dict: dict = self.choose_language_dict.get(self.language)

    def reset_language(self, language) -> None:
        apitestka_logger.info(f"LanguageWrapper reset_language language: {language}")
        if language in self.choose_language_dict:
            self.language = language
            self.language_word_dict = self.choose_language_dict.get(self.language)


language_wrapper = LanguageWrapper()
