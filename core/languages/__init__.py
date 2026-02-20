import json
import os

class LanguageManager:
    def __init__(self):
        self.languages = {}
        self.current_lang = "ru"
        self.load_languages()
    
    def load_languages(self):
        """Загружает все языки из JSON файлов"""
        lang_dir = os.path.dirname(__file__)
        for lang_file in ["ru.json", "en.json", "de.json", "zh.json"]:
            try:
                with open(os.path.join(lang_dir, lang_file), 'r', encoding='utf-8') as f:
                    lang_data = json.load(f)
                    lang_code = lang_file.replace('.json', '')
                    self.languages[lang_code] = lang_data
            except Exception as e:
                print(f"Ошибка загрузки {lang_file}: {e}")
    
    def get_text(self, key, default=None):
        """Получает текст на текущем языке по ключу"""
        keys = key.split('.')
        value = self.languages.get(self.current_lang, {})
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default or key
        
        return value or default or key
    
    def set_language(self, lang_code):
        """Устанавливает текущий язык"""
        if lang_code in self.languages:
            self.current_lang = lang_code
            return True
        return False
    
    def get_language_name(self, lang_code=None):
        """Возвращает название языка на самом языке"""
        if lang_code is None:
            lang_code = self.current_lang
        return self.languages.get(lang_code, {}).get("language", lang_code)

# СОЗДАЁМ ГЛОБАЛЬНЫЙ ЭКЗЕМПЛЯР
lang_manager = LanguageManager()  # <--- Вот он!