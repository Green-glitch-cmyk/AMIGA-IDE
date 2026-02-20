#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import tkinter.simpledialog as simpledialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter.font as tkfont
import os
import sys

# Добавляем пути для импортов
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from editor.widget import AMIGAEditor
from core.interpreter import AMIGAInterpreter
from windows.about_window import AboutWindow
from core.languages import lang_manager
from editor.themes import THEMES

class AMIGAIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("AMIGA IDE - Advanced Multi-purpose Interpreted General-purpose Architecture")
        self.root.geometry("1400x800")
        
        # Путь к папке assets
        self.assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        
        # Устанавливаем иконку
        self.set_program_icon()
        
        # Текущий файл
        self.current_file = None
        self.current_theme = "light"
        
        # Интерпретатор
        self.interpreter = AMIGAInterpreter()
        self.interpreter.output_callback = self.append_output
        self.interpreter.input_callback = self.get_input
        
        # Настройка стиля
        self.style = tb.Style(theme="cosmo")
        
        # Создание интерфейса
        self.setup_modern_ui()

        self.load_custom_fonts()
        
        # Привязка горячих клавиш
        self.setup_shortcuts()
        
    def set_program_icon(self):
        """Устанавливает иконку программы"""
        try:
            icon_path = os.path.join(self.assets_path, "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Не удалось загрузить иконку: {e}")
    
    def setup_modern_ui(self):
        """СОВРЕМЕННЫЙ ИНТЕРФЕЙС как в VS Code"""
        
        # === ГОЛОВНОЕ МЕНЮ ===
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новый (Ctrl+N)", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Открыть (Ctrl+O)", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Сохранить (Ctrl+S)", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Сохранить как...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Правка
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(label="Отменить (Ctrl+Z)", command=lambda: self.editor.text.edit_undo())
        edit_menu.add_command(label="Повторить (Ctrl+Y)", command=lambda: self.editor.text.edit_redo())
        edit_menu.add_separator()
        edit_menu.add_command(label="Вырезать (Ctrl+X)", command=lambda: self.root.focus_get().event_generate("<<Cut>>"))
        edit_menu.add_command(label="Копировать (Ctrl+C)", command=lambda: self.root.focus_get().event_generate("<<Copy>>"))
        edit_menu.add_command(label="Вставить (Ctrl+V)", command=lambda: self.root.focus_get().event_generate("<<Paste>>"))
        
        # Вид
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)
        
        self.theme_var = tk.StringVar(value="Светлая")
        view_menu.add_radiobutton(label="Светлая тема", variable=self.theme_var, value="Светлая", command=lambda: self.toggle_theme("light"))
        view_menu.add_radiobutton(label="Тёмная тема", variable=self.theme_var, value="Тёмная", command=lambda: self.toggle_theme("dark"))
        view_menu.add_separator()
        
        self.sidebar_var = tk.BooleanVar(value=True)
        view_menu.add_checkbutton(label="Боковая панель", variable=self.sidebar_var, command=self.toggle_sidebar)
        
        self.output_var = tk.BooleanVar(value=True)
        view_menu.add_checkbutton(label="Панель вывода", variable=self.output_var, command=self.toggle_output)
        
        # Язык
        lang_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Язык", menu=lang_menu)
        lang_menu.add_command(label="🇷🇺 Русский", command=lambda: self.switch_language("ru"))
        lang_menu.add_command(label="🇬🇧 English", command=lambda: self.switch_language("en"))
        lang_menu.add_command(label="🇩🇪 Deutsch", command=lambda: self.switch_language("de"))
        lang_menu.add_command(label="🇨🇳 中文", command=lambda: self.switch_language("zh"))
        
        # Помощь
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="Примеры кода", command=self.show_examples)
        help_menu.add_command(label="О программе", command=self.show_about)
        
        # === ПАНЕЛЬ ИНСТРУМЕНТОВ (С КНОПКАМИ) ===
        toolbar = tb.Frame(self.root, bootstyle="secondary")
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 1))
        
        # Кнопка запуска (ЗЕЛЁНАЯ!)
        self.run_button = tb.Button(
            toolbar,
            text="▶ ЗАПУСК (F5)",
            command=self.run_code,
            bootstyle="success",
            width=15
        )
        self.run_button.pack(side=LEFT, padx=2, pady=2)
        
        # Кнопка очистки
        self.clear_button = tb.Button(
            toolbar,
            text="Очистить вывод",
            command=self.clear_output,
            bootstyle="secondary",
            width=12
        )
        self.clear_button.pack(side=LEFT, padx=2, pady=2)
        
        # Кнопка новой вкладки
        self.new_tab_button = tb.Button(
            toolbar,
            text="+ Новая вкладка",
            command=self.new_file,
            bootstyle="info",
            width=12
        )
        self.new_tab_button.pack(side=LEFT, padx=2, pady=2)
        
        # Кнопка сохранения
        self.save_button = tb.Button(
            toolbar,
            text="💾 Сохранить",
            command=self.save_file,
            bootstyle="warning",
            width=10
        )
        self.save_button.pack(side=LEFT, padx=2, pady=2)
        
        # Кнопка темы
        self.theme_button = tb.Button(
            toolbar,
            text="🌓 Тема",
            command=lambda: self.toggle_theme("dark" if self.current_theme == "light" else "light"),
            bootstyle="primary",
            width=8
        )
        self.theme_button.pack(side=LEFT, padx=2, pady=2)
        
        # === ОСНОВНОЙ КОНТЕЙНЕР ===
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # === БОКОВАЯ ПАНЕЛЬ (как в VS Code) ===
        self.sidebar = tb.Frame(self.root, width=250, bootstyle="secondary")
        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=(0, 1))
        self.sidebar.grid_propagate(False)
        
        # Заголовок боковой панели
        sidebar_header = tb.Frame(self.sidebar, bootstyle="secondary")
        sidebar_header.pack(fill=X, pady=(0, 1))
        
        tb.Label(sidebar_header, text="ПРОВОДНИК", font=("Segoe UI", 9, "bold")).pack(side=LEFT, padx=5, pady=5)
        
        # Ноутбук для вкладок в боковой панели
        self.sidebar_notebook = tb.Notebook(self.sidebar, bootstyle="secondary")
        self.sidebar_notebook.pack(fill=BOTH, expand=True)
        
        # Вкладка "Файлы"
        files_frame = tb.Frame(self.sidebar_notebook)
        self.sidebar_notebook.add(files_frame, text="📁 Файлы")
        
        # Дерево файлов
        self.file_tree = ttk.Treeview(files_frame, selectmode="browse", show="tree")
        self.file_tree.pack(side=LEFT, fill=BOTH, expand=True)
        
        file_scroll = tb.Scrollbar(files_frame, orient=VERTICAL, command=self.file_tree.yview)
        file_scroll.pack(side=RIGHT, fill=Y)
        self.file_tree.config(yscrollcommand=file_scroll.set)
        
        # Вкладка "Примеры"
        examples_frame = tb.Frame(self.sidebar_notebook)
        self.sidebar_notebook.add(examples_frame, text="📚 Примеры")
        
        # Список примеров
        self.examples_listbox = tk.Listbox(examples_frame, bg="#f8f9fa", fg="#212529", font=("Consolas", 10))
        self.examples_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        self.examples_listbox.bind('<Double-Button-1>', self.load_example)
        
        examples_scroll = tb.Scrollbar(examples_frame, orient=VERTICAL, command=self.examples_listbox.yview)
        examples_scroll.pack(side=RIGHT, fill=Y)
        self.examples_listbox.config(yscrollcommand=examples_scroll.set)
        
        # Загружаем примеры
        self.load_examples_list()
        
        # === ЦЕНТРАЛЬНАЯ ПАНЕЛЬ (РЕДАКТОР) ===
        center_frame = tb.Frame(self.root)
        center_frame.grid(row=1, column=1, sticky="nsew")
        center_frame.grid_rowconfigure(1, weight=1)
        center_frame.grid_columnconfigure(0, weight=1)
        
        # Вкладки редактора
        self.tabs = tb.Notebook(center_frame, bootstyle="primary")
        self.tabs.grid(row=0, column=0, sticky="ew", padx=2, pady=(2, 0))
        
        # Кнопка "Новый файл" на вкладках
        tab_controls = tb.Frame(self.tabs)
        tb.Button(tab_controls, text="+", command=self.new_file, bootstyle="primary", width=3).pack(side=RIGHT)
        self.tabs.add(tab_controls, text="  +  ")
        
        # Создаём первую вкладку
        self.create_new_tab()
        
        # === ПАНЕЛЬ ВЫВОДА ===
        self.output_frame = tb.Frame(self.root, height=200)
        self.output_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(1, 0))
        self.output_frame.grid_propagate(False)
        
        # Заголовок панели вывода
        output_header = tb.Frame(self.output_frame)
        output_header.pack(fill=X)
        
        tb.Label(output_header, text="ВЫВОД", font=("Segoe UI", 9, "bold")).pack(side=LEFT, padx=5)
        
        tb.Button(output_header, text="Очистить", command=self.clear_output, bootstyle="secondary", width=10).pack(side=RIGHT, padx=5)
        
        # Текст вывода
        self.output_text = tk.Text(self.output_frame, wrap=WORD, bg="#f8f9fa", fg="#212529",
                                   font=("Consolas", 10), height=8)
        self.output_text.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # === СТАТУС БАР ===
        status_bar = tb.Frame(self.root, bootstyle="secondary")
        status_bar.grid(row=3, column=0, columnspan=2, sticky="ew")
        
        self.status_label = tb.Label(status_bar, text="Готов к работе", font=("Segoe UI", 9))
        self.status_label.pack(side=LEFT, padx=5)
        
        self.lang_status = tb.Label(status_bar, text="Русский", font=("Segoe UI", 9))
        self.lang_status.pack(side=LEFT, padx=15)
        
        self.theme_status = tb.Label(status_bar, text="Светлая", font=("Segoe UI", 9))
        self.theme_status.pack(side=LEFT, padx=15)
        
        self.cursor_pos_label = tb.Label(status_bar, text="Стр: 1, Стлб: 1", font=("Segoe UI", 9))
        self.cursor_pos_label.pack(side=RIGHT, padx=5)
        
        self.encoding_status = tb.Label(status_bar, text="UTF-8", font=("Segoe UI", 9))
        self.encoding_status.pack(side=RIGHT, padx=5)
    
    def create_new_tab(self):
        """Создаёт новую вкладку с редактором"""
        tab_frame = tb.Frame(self.tabs)
        
        # Редактор
        editor = AMIGAEditor(tab_frame, is_light_theme=(self.current_theme == "light"))
        editor.pack(fill=BOTH, expand=True)
        
        # Привязываем события
        editor.text.bind('<<CursorMove>>', self.update_cursor_position)
        editor.text.bind('<KeyRelease>', self.on_key_release)
        
        # Номер вкладки
        tab_num = len(self.tabs.tabs())
        self.tabs.insert(tab_num - 1, tab_frame, text=f"Новый {tab_num}.amiga1")
        self.tabs.select(tab_frame)
        
        self.editor = editor
        return editor
    
    def load_examples_list(self):
        """Загружает список примеров"""
        examples_dir = os.path.join(os.path.dirname(__file__), "examples")
        if os.path.exists(examples_dir):
            for file in sorted(os.listdir(examples_dir)):
                if file.endswith(('.amiga1', '.amiga')):
                    self.examples_listbox.insert(tk.END, file)
    
    def load_example(self, event):
        """Загружает выбранный пример"""
        selection = self.examples_listbox.curselection()
        if selection:
            filename = self.examples_listbox.get(selection[0])
            examples_dir = os.path.join(os.path.dirname(__file__), "examples")
            filepath = os.path.join(examples_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.editor.set_text(content)
                self.status_label.config(text=f"Загружен пример: {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить пример: {e}")
    
    def toggle_sidebar(self):
        """Показывает/скрывает боковую панель"""
        if self.sidebar_var.get():
            self.sidebar.grid()
        else:
            self.sidebar.grid_remove()
    
    def toggle_output(self):
        """Показывает/скрывает панель вывода"""
        if self.output_var.get():
            self.output_frame.grid()
        else:
            self.output_frame.grid_remove()
    
    def toggle_theme(self, theme_name):
        """Переключение темы"""
        self.current_theme = theme_name
        self.editor.apply_theme(theme_name)
        
        # Обновляем текст кнопки
        self.theme_button.config(text="🌓 Светлая" if theme_name == "dark" else "🌓 Тёмная")
        
        if theme_name == "dark":
            self.output_text.config(bg="#1e1e1e", fg="#d4d4d4")
            self.theme_status.config(text="Тёмная")
        else:
            self.output_text.config(bg="#f8f9fa", fg="#212529")
            self.theme_status.config(text="Светлая")
    
    def switch_language(self, lang_code):
        """Переключение языка"""
        lang_names = {"ru": "Русский", "en": "English", "de": "Deutsch", "zh": "中文"}
        self.lang_status.config(text=lang_names.get(lang_code, "Русский"))
        # TODO: полная локализация интерфейса
    
    def update_cursor_position(self, event=None):
        """Обновляет позицию курсора"""
        try:
            cursor_pos = self.editor.text.index(tk.INSERT)
            line, col = cursor_pos.split('.')
            self.cursor_pos_label.config(text=f"Стр: {line}, Стлб: {int(col) + 1}")
        except:
            pass
    
    def on_key_release(self, event=None):
        """Обработка отпускания клавиш"""
        self.update_cursor_position()
    
    def new_file(self):
        """Новый файл"""
        self.create_new_tab()
        self.status_label.config(text="Новый файл создан")
    
    def open_file(self):
        """Открыть файл"""
        filename = filedialog.askopenfilename(
            title="Открыть файл AMIGA",
            filetypes=[("AMIGA files", "*.amiga1 *.amiga"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Создаём новую вкладку
                editor = self.create_new_tab()
                editor.set_text(content)
                self.current_file = filename
                
                # Обновляем название вкладки
                current_tab = self.tabs.select()
                self.tabs.tab(current_tab, text=os.path.basename(filename))
                
                self.status_label.config(text=f"Открыт: {filename}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл: {str(e)}")
    
    def save_file(self):
        """Сохранить файл"""
        if self.current_file:
            try:
                content = self.editor.get_all_text()
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.status_label.config(text=f"Сохранено: {self.current_file}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")
        else:
            self.save_as_file()
    
    def save_as_file(self):
        """Сохранить как"""
        filename = filedialog.asksaveasfilename(
            title="Сохранить файл AMIGA",
            defaultextension=".amiga1",
            filetypes=[("AMIGA files", "*.amiga1"), ("All files", "*.*")]
        )
        
        if filename:
            self.current_file = filename
            self.save_file()
            
            # Обновляем название вкладки
            current_tab = self.tabs.select()
            self.tabs.tab(current_tab, text=os.path.basename(filename))
    
    def load_custom_fonts(self):
        """Загружает пользовательские шрифты"""
        import tkinter.font as tkfont
        
        fonts_dir = os.path.join(os.path.dirname(__file__), "fonts")
        
        # Шрифт по умолчанию
        self.editor_font = ("Consolas", 11)
        self.ui_font = ("Segoe UI", 9)
        
        # Проверяем системные шрифты
        available_fonts = list(tkfont.families())
        
        # Ищем JetBrains Mono в системе
        jetbrains_variants = ["JetBrains Mono", "JetBrainsMono", "JetBrains Mono Regular"]
        for font_name in jetbrains_variants:
            if font_name in available_fonts:
                self.editor_font = (font_name, 11)
                print(f"✓ Найден системный шрифт: {font_name}")
                return
        
        # В Tkinter нельзя загрузить .ttf напрямую,
        # поэтому используем системные шрифты или стандартные
        print("✓ Используется системный шрифт: Consolas")
    
    def run_code(self):
        """Запустить код"""
        code = self.editor.get_all_text()
        if not code.strip():
            messagebox.showwarning("Предупреждение", "Нет кода для выполнения")
            return
        
        self.clear_output()
        
        try:
            self.interpreter.run(code)
            self.status_label.config(text="Программа выполнена")
        except Exception as e:
            self.output_text.insert(tk.END, f"Ошибка: {str(e)}\n")
            self.status_label.config(text="Ошибка выполнения")
    
    def append_output(self, text):
        """Добавить в вывод"""
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.root.update()
    
    def clear_output(self):
        """Очистить вывод"""
        self.output_text.delete(1.0, tk.END)
    
    def get_input(self, prompt=""):
        """Получить ввод"""
        return simpledialog.askstring("Ввод", prompt, parent=self.root)
    
    def show_examples(self):
        """Показать примеры"""
        self.sidebar_notebook.select(1)  # Переключаем на вкладку с примерами
    
    def show_about(self):
        """О программе"""
        AboutWindow(self.root, self.assets_path)
    
    def setup_shortcuts(self):
        """Горячие клавиши"""
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<F5>', lambda e: self.run_code())

def main():
    root = tb.Window(themename="cosmo")
    app = AMIGAIDE(root)
    root.mainloop()

if __name__ == "__main__":
    main()