# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from .syntax import AMIGASyntaxHighlighter

class LineNumbers(tk.Canvas):
    """Виджет для отображения номеров строк"""
    
    def __init__(self, parent, text_widget, is_light_theme=False, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.text_widget = text_widget
        self.is_light_theme = is_light_theme
        
        # Цвета в зависимости от темы
        if is_light_theme:
            self.bg_color = "#f0f0f0"
            self.fg_color = "#666666"
        else:
            self.bg_color = "#252526"
            self.fg_color = "#858585"
            
        self.configure(bg=self.bg_color, width=50, highlightthickness=0)
        
        # Привязка событий
        self.text_widget.bind('<KeyPress>', self.on_text_change)
        self.text_widget.bind('<MouseWheel>', self.on_text_change)
        self.text_widget.bind('<Button-1>', self.on_text_change)
        self.text_widget.bind('<Configure>', self.on_text_change)
        
        self.redraw()
    
    def on_text_change(self, event=None):
        """Обновление номеров строк при изменении текста"""
        self.redraw()
    
    def redraw(self):
        """Перерисовка номеров строк"""
        self.delete("all")
        
        try:
            # Получаем видимые строки
            first_line = int(self.text_widget.index("@0,0").split('.')[0])
            last_line = int(self.text_widget.index("@0,{}".format(self.winfo_height())).split('.')[0])
            
            # Вычисляем высоту строки
            dline_info = self.text_widget.dlineinfo("1.0")
            line_height = dline_info[3] if dline_info else 15
            
            y = 5  # Начальная позиция
            
            for line_num in range(first_line, last_line + 1):
                # Координаты строки
                dline = self.text_widget.dlineinfo("{}.0".format(line_num))
                if dline:
                    y = dline[1]
                
                # Рисуем номер строки
                self.create_text(
                    40, y + line_height//2,
                    text=str(line_num),
                    fill=self.fg_color,
                    font=("Consolas", 9),
                    anchor="e"
                )
        except:
            pass

class AMIGAEditor(ttk.Frame):
    """Текстовый редактор с подсветкой синтаксиса для AMIGA"""
    
    def __init__(self, parent, is_light_theme=False, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.is_light_theme = is_light_theme
        
        # Настройка цветов в зависимости от темы
        if is_light_theme:
            self.bg_color = "#ffffff"
            self.fg_color = "#000000"
            self.insert_bg = "#000000"
            self.select_bg = "#add6ff"
            self.select_fg = "#000000"
        else:
            self.bg_color = "#1e1e1e"
            self.fg_color = "#d4d4d4"
            self.insert_bg = "#ffffff"
            self.select_bg = "#264f78"
            self.select_fg = "#ffffff"
        
        self.setup_ui()
        self.setup_bindings()
        
        # Подсветка синтаксиса
        self.highlighter = AMIGASyntaxHighlighter(self.text, is_light_theme)
        
    def setup_ui(self):
        """Создание интерфейса редактора"""
        # Создаем фрейм для редактора с рамкой
        editor_frame = tk.Frame(self, bg="#cccccc" if self.is_light_theme else "#333333", 
                                bd=1, relief=tk.SUNKEN)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем текстовое поле
        self.text = tk.Text(
            editor_frame,
            wrap=tk.WORD,
            bg=self.bg_color,
            fg=self.fg_color,
            insertbackground=self.insert_bg,
            font=("Consolas", 11),
            undo=True,
            autoseparators=True,
            maxundo=-1,
            selectbackground=self.select_bg,
            selectforeground=self.select_fg,
            padx=5,
            pady=5,
            relief=tk.FLAT,
            borderwidth=0
        )
        
        # Номера строк
        self.line_numbers = LineNumbers(editor_frame, self.text, self.is_light_theme)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        
        # Размещение элементов
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 1), pady=1)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def setup_bindings(self):
        """Настройка привязок событий"""
        # Подсветка в реальном времени при любых изменениях
        self.text.bind('<KeyRelease>', self.on_text_changed)
        self.text.bind('<<Paste>>', self.on_text_changed)
        self.text.bind('<Return>', self.on_text_changed)
        self.text.bind('<BackSpace>', self.on_text_changed)
        self.text.bind('<Delete>', self.on_text_changed)
        
        # Табуляция
        self.text.bind('<Tab>', self.handle_tab)
        self.text.bind('<Shift-Tab>', self.handle_shift_tab)
        
        # Автодополнение скобок и кавычек
        self.text.bind('"', self.auto_quote)
        self.text.bind("'", self.auto_quote)
        self.text.bind('(', self.auto_paren)
        self.text.bind('[', self.auto_bracket)
        self.text.bind('{', self.auto_brace)
        
    def on_text_changed(self, event=None):
        """Обработка изменений текста в реальном времени"""
        # Обновляем подсветку синтаксиса
        self.highlight_syntax()
        # Обновляем номера строк
        self.line_numbers.redraw()
        # Продолжаем обработку события
        return None
    
    def highlight_syntax(self):
        """Подсветка синтаксиса всего текста"""
        if self.highlighter:
            self.highlighter.highlight()
    
    def handle_tab(self, event):
        """Обработка табуляции"""
        self.text.insert(tk.INSERT, "    ")
        self.on_text_changed()  # Обновляем подсветку
        return "break"
    
    def handle_shift_tab(self, event):
        """Обработка Shift+Tab (удаление отступа)"""
        try:
            # Получаем текущую позицию курсора
            line_start = self.text.index(tk.INSERT + " linestart")
            line_end = self.text.index(tk.INSERT + " lineend")
            
            # Проверяем, есть ли отступ в начале строки
            text_before_cursor = self.text.get(line_start, tk.INSERT)
            if text_before_cursor.startswith("    "):
                self.text.delete(line_start, line_start + " + 4 chars")
                self.on_text_changed()  # Обновляем подсветку
            elif text_before_cursor.startswith("\t"):
                self.text.delete(line_start, line_start + " + 1 chars")
                self.on_text_changed()  # Обновляем подсветку
        except:
            pass
        
        return "break"
    
    def auto_quote(self, event):
        """Автоматическое закрытие кавычек"""
        char = event.char
        self.text.insert(tk.INSERT, char)
        
        try:
            # Проверяем, не внутри ли мы уже строки
            pos = self.text.index(tk.INSERT)
            prev_char = self.text.get("{} - 2 chars".format(pos), "{} - 1 chars".format(pos))
            
            if prev_char != '\\':  # Не экранировано
                self.text.insert(tk.INSERT, char)
        except:
            self.text.insert(tk.INSERT, char)
        
        self.on_text_changed()  # Обновляем подсветку
        return "break"
    
    def auto_paren(self, event):
        """Автоматическое закрытие скобок"""
        self.text.insert(tk.INSERT, "()")
        self.text.mark_set(tk.INSERT, "{} - 1 chars".format(tk.INSERT))
        self.on_text_changed()  # Обновляем подсветку
        return "break"
    
    def auto_bracket(self, event):
        """Автоматическое закрытие квадратных скобок"""
        self.text.insert(tk.INSERT, "[]")
        self.text.mark_set(tk.INSERT, "{} - 1 chars".format(tk.INSERT))
        self.on_text_changed()  # Обновляем подсветку
        return "break"
    
    def auto_brace(self, event):
        """Автоматическое закрытие фигурных скобок"""
        self.text.insert(tk.INSERT, "{}")
        self.text.mark_set(tk.INSERT, "{} - 1 chars".format(tk.INSERT))
        
        # Автоматический перенос строки внутри {}
        self.text.insert(tk.INSERT, "\n    \n}")
        self.text.mark_set(tk.INSERT, "{} - 3 lines + 4 chars".format(tk.INSERT))
        self.on_text_changed()  # Обновляем подсветку
        return "break"
    
    def get_all_text(self):
        """Получить весь текст из редактора"""
        return self.text.get(1.0, tk.END).rstrip()
    
    def set_text(self, text):
        """Установить текст в редактор"""
        self.text.delete(1.0, tk.END)
        self.text.insert(1.0, text)
        self.highlight_syntax()
        self.line_numbers.redraw()
    
    def clear(self):
        """Очистить редактор"""
        self.text.delete(1.0, tk.END)
        self.highlight_syntax()
        self.line_numbers.redraw()