from je_api_testka.gui.language_wrapper.english import english_word_dict
from je_api_testka.gui.language_wrapper.traditional_chinese import traditional_chinese_word_dict
from je_api_testka.utils.logging.loggin_instance import apitestka_logger



class LanguageWrapper(object):

    def __init__(
            self
    ):
        apitestka_logger.info("Init LanguageWrapper")
        self.language: str = "English"
        self.choose_language_dict = {
            "English": english_word_dict,
            "Traditional_Chinese": traditional_chinese_word_dict
        }
        self.language_word_dict: dict = self.choose_language_dict.get(self.language)

    def reset_language(self, language) -> None:
        apitestka_logger.info(f"LanguageWrapper reset_language language: {language}")
        if language in [
            "English",
            "Traditional_Chinese"
        ]:
            self.language = language
            self.language_word_dict = self.choose_language_dict.get(self.language)


language_wrapper = LanguageWrapper()
