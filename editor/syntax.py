# -*- coding: utf-8 -*-
import re
import tkinter as tk

class AMIGASyntaxHighlighter:
    """Подсветка синтаксиса для языка AMIGA"""
    
    def __init__(self, text_widget, is_light_theme=False):
        self.text = text_widget
        self.is_light_theme = is_light_theme
        self.setup_tags()
        
    def setup_tags(self):
        """Настройка тегов для подсветки"""
        
        if self.is_light_theme:
            # Светлая тема
            # Классы/Библиотеки: Зелёный (темнее для читаемости)
            self.text.tag_configure("class", foreground="#267507")
            
            # @декораторы: Красный, жирный
            self.text.tag_configure("decorator", foreground="#c00000", font=("Consolas", 10, "bold"))
            
            # Ключевые слова: Синий, жирный
            self.text.tag_configure("keyword", foreground="#0000c0", font=("Consolas", 10, "bold"))
            
            # Комментарии: Серый, курсив
            self.text.tag_configure("comment", foreground="#808080", font=("Consolas", 10, "italic"))
            
            # Строки: Коричневый
            self.text.tag_configure("string", foreground="#a31515")
            
            # Числа: Тёмно-зелёный
            self.text.tag_configure("number", foreground="#098658")
            
            # Операторы: Чёрный
            self.text.tag_configure("operator", foreground="#000000")
        else:
            # Тёмная тема (как было)
            # Классы/Библиотеки: Зелёный
            self.text.tag_configure("class", foreground="#6A9955")
            
            # @декораторы: Красный, жирный
            self.text.tag_configure("decorator", foreground="#CE9178", font=("Consolas", 10, "bold"))
            
            # Ключевые слова: Синий, жирный
            self.text.tag_configure("keyword", foreground="#569CD6", font=("Consolas", 10, "bold"))
            
            # Комментарии: Серый, курсив
            self.text.tag_configure("comment", foreground="#6A9955", font=("Consolas", 10, "italic"))
            
            # Строки: Оранжевый
            self.text.tag_configure("string", foreground="#CE9178")
            
            # Числа: Светло-зелёный
            self.text.tag_configure("number", foreground="#B5CEA8")
            
            # Операторы: Белый
            self.text.tag_configure("operator", foreground="#D4D4D4")
        
    def highlight(self, start="1.0", end=None):
        """Подсветка синтаксиса в указанном диапазоне"""
        if end is None:
            end = self.text.index(tk.END)
            
        # Снимаем все теги в диапазоне
        for tag in self.text.tag_names():
            self.text.tag_remove(tag, start, end)
        
        # Получаем текст
        text_content = self.text.get(start, end)
        
        # Подсветка комментариев
        self.highlight_comments(start, text_content)
        
        # Подсветка строк
        self.highlight_strings(start, text_content)
        
        # Подсветка ключевых слов
        self.highlight_keywords(start, text_content)
        
        # Подсветка декораторов (@use, @in)
        self.highlight_decorators(start, text_content)
        
        # Подсветка классов
        self.highlight_classes(start, text_content)
        
        # Подсветка чисел
        self.highlight_numbers(start, text_content)
        
        # Подсветка операторов
        self.highlight_operators(start, text_content)
    
    def _get_pos(self, start_line, text, match_start, match_end):
        """Вспомогательная функция для вычисления позиций"""
        text_before = text[:match_start]
        line_num = text_before.count('\n')
        
        # Находим последний перевод строки перед match_start
        last_newline = text_before.rfind('\n')
        if last_newline == -1:
            col_num = match_start
        else:
            col_num = match_start - last_newline - 1
        
        start_pos = f"{int(start_line) + line_num}.{col_num}"
        
        # Для конца
        text_before_end = text[:match_end]
        last_newline_end = text_before_end.rfind('\n')
        if last_newline_end == -1:
            col_num_end = match_end
        else:
            col_num_end = match_end - last_newline_end - 1
        
        end_pos = f"{int(start_line) + line_num}.{col_num_end}"
        
        return start_pos, end_pos
    
    def highlight_comments(self, start, text):
        """Подсветка комментариев // ..."""
        pattern = r'//.*$'
        start_line = start.split('.')[0]
        
        for match in re.finditer(pattern, text, re.MULTILINE):
            start_pos, end_pos = self._get_pos(start_line, text, match.start(), match.end())
            self.text.tag_add("comment", start_pos, end_pos)
    
    def highlight_strings(self, start, text):
        """Подсветка строк в кавычках"""
        pattern = r'"[^"\\]*(\\.[^"\\]*)*"'
        start_line = start.split('.')[0]
        
        for match in re.finditer(pattern, text):
            start_pos, end_pos = self._get_pos(start_line, text, match.start(), match.end())
            self.text.tag_add("string", start_pos, end_pos)
    
    def highlight_keywords(self, start, text):
        """Подсветка ключевых слов"""
        keywords = [
            'if', 'then', 'elsif', 'else', 'while', 'for', 'each',
            'break', 'continue', 'return', 'global', 'local', 'private',
            'public', 'class', 'define', 'true', 'false', 'in'
        ]
        
        # Создаём паттерн для поиска целых слов
        pattern = r'\b(' + '|'.join(keywords) + r')\b'
        start_line = start.split('.')[0]
        
        for match in re.finditer(pattern, text):
            start_pos, end_pos = self._get_pos(start_line, text, match.start(), match.end())
            self.text.tag_add("keyword", start_pos, end_pos)
    
    def highlight_decorators(self, start, text):
        """Подсветка декораторов (@use, @in)"""
        pattern = r'@\w+'
        start_line = start.split('.')[0]
        
        for match in re.finditer(pattern, text):
            start_pos, end_pos = self._get_pos(start_line, text, match.start(), match.end())
            self.text.tag_add("decorator", start_pos, end_pos)
    
    def highlight_classes(self, start, text):
        """Подсветка классов и библиотек"""
        start_line = start.split('.')[0]
        
        # Ищем названия классов после "class"
        pattern = r'class\s+(\w+)'
        
        for match in re.finditer(pattern, text):
            if match.group(1):
                start_pos, end_pos = self._get_pos(start_line, text, match.start(1), match.end(1))
                self.text.tag_add("class", start_pos, end_pos)
        
        # Ищем названия модулей (Console, Times)
        modules = ['Console', 'Times']
        pattern = r'\b(' + '|'.join(modules) + r')\b'
        
        for match in re.finditer(pattern, text):
            start_pos, end_pos = self._get_pos(start_line, text, match.start(), match.end())
            self.text.tag_add("class", start_pos, end_pos)
    
    def highlight_numbers(self, start, text):
        """Подсветка чисел"""
        pattern = r'\b\d+(\.\d+)?\b'
        start_line = start.split('.')[0]
        
        for match in re.finditer(pattern, text):
            start_pos, end_pos = self._get_pos(start_line, text, match.start(), match.end())
            self.text.tag_add("number", start_pos, end_pos)
    
    def highlight_operators(self, start, text):
        """Подсветка операторов"""
        operators = ['+', '-', '*', '/', '=', '==', '!=', '<', '>', '<=', '>=', '>>', '=>', ':', '.']
        start_line = start.split('.')[0]
        
        for op in operators:
            pattern = re.escape(op)
            for match in re.finditer(pattern, text):
                # Пропускаем операторы внутри строк
                if self.is_in_string(text, match.start()):
                    continue
                
                start_pos, end_pos = self._get_pos(start_line, text, match.start(), match.end())
                self.text.tag_add("operator", start_pos, end_pos)
    
    def is_in_string(self, text, pos):
        """Проверяет, находится ли позиция внутри строки"""
        # Простая проверка: считаем кавычки до позиции
        quotes = text[:pos].count('"')
        return quotes % 2 == 1

    def update_theme(self, theme):
        """Обновить цвета подсветки"""
        syntax_theme = theme["syntax"]
        
        self.text.tag_configure("class", foreground=syntax_theme["class"])
        self.text.tag_configure("decorator", foreground=syntax_theme["decorator"], 
                            font=("Consolas", 10, "bold"))
        self.text.tag_configure("keyword", foreground=syntax_theme["keyword"], 
                            font=("Consolas", 10, "bold"))
        self.text.tag_configure("comment", foreground=syntax_theme["comment"], 
                            font=("Consolas", 10, "italic"))
        self.text.tag_configure("string", foreground=syntax_theme["string"])
        self.text.tag_configure("number", foreground=syntax_theme["number"])
        self.text.tag_configure("operator", foreground=syntax_theme["operator"])
        
        # Переподсвечиваем текст
        self.highlight()