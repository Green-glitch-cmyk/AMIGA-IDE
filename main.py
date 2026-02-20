#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from editor.themes import THEMES
from core.languages import lang_manager
import os
import sys

# Добавляем пути для импортов
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from editor.widget import AMIGAEditor
from core.interpreter import AMIGAInterpreter
from windows.about_window import AboutWindow

class AMIGAIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("AMIGA IDE - Язык программирования AMIGA")
        self.root.geometry("1200x800")
        
        # Путь к папке assets
        self.assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        
        # Устанавливаем иконку программы (icon.ico)
        self.set_program_icon()

        self.current_theme = "light"  # по умолчанию светлая
        
        # Текущий файл
        self.current_file = None
        
        # Интерпретатор
        self.interpreter = AMIGAInterpreter()
        self.interpreter.output_callback = self.append_output
        self.interpreter.input_callback = self.get_input
        
        # Настройка темы ttkbootstrap (светлая)
        self.style = tb.Style(theme="cosmo")
        
        # Создание интерфейса
        self.setup_ui()
        
        # Привязка горячих клавиш
        self.setup_shortcuts()
        
        # Флаг ожидания ввода
        self.waiting_for_input = False
        self.input_value = None
        
    def set_program_icon(self):
        """Устанавливает иконку программы из icon.ico"""
        try:
            icon_path = os.path.join(self.assets_path, "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Не удалось загрузить иконку: {e}")
        
    def setup_ui(self):
        """Создание интерфейса"""
        # Главное меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню File
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новый (Ctrl+N)", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Открыть (Ctrl+O)", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Сохранить (Ctrl+S)", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Сохранить как...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню Run
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Запуск", menu=run_menu)
        run_menu.add_command(label="Запустить (F5)", command=self.run_code, accelerator="F5")
        run_menu.add_command(label="Очистить вывод", command=self.clear_output)
        # Меню View
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)
        
        self.theme_var = tk.StringVar(value="Светлая")
        view_menu.add_radiobutton(
            label="Светлая тема",
            variable=self.theme_var,
            value="Светлая",
            command=lambda: self.toggle_theme("light")
        )
        view_menu.add_radiobutton(
            label="Тёмная тема (бета)",
            variable=self.theme_var,
            value="Тёмная",
            command=lambda: self.toggle_theme("dark")
        )
        
        # Меню Help
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
        
        # Основной контейнер
        main_panel = tb.PanedWindow(self.root, orient=HORIZONTAL)
        main_panel.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Левая панель - редактор
        editor_frame = tb.Frame(main_panel)
        main_panel.add(editor_frame, weight=3)
        
        # Заголовок редактора
        editor_header = tb.Frame(editor_frame)
        editor_header.pack(fill=X, pady=(0, 2))
        
        tb.Label(editor_header, text="Редактор кода", 
                font=("Segoe UI", 10, "bold")).pack(side=LEFT)
        
        # Статистика файла
        self.file_stats_label = tb.Label(editor_header, text="", font=("Segoe UI", 9))
        self.file_stats_label.pack(side=RIGHT, padx=5)
        
        # Редактор с подсветкой
        self.editor = AMIGAEditor(editor_frame, is_light_theme=True)
        self.editor.pack(fill=BOTH, expand=True)
        
        # Правая панель - вывод и консоль
        right_frame = tb.Frame(main_panel)
        main_panel.add(right_frame, weight=1)
        
        # Консоль вывода
        output_header = tb.Frame(right_frame)
        output_header.pack(fill=X, pady=(0, 2))
        
        tb.Label(output_header, text="Вывод программы", 
                font=("Segoe UI", 10, "bold")).pack(side=LEFT)
        
        # Кнопка очистки вывода
        tb.Button(output_header, text="Очистить", 
                 command=self.clear_output,
                 bootstyle="secondary").pack(side=RIGHT, padx=2)
        
        # Создаем фрейм для вывода
        output_frame = tb.Frame(right_frame, bootstyle="default")
        output_frame.pack(fill=BOTH, expand=True)
        
        # Текстовое поле для вывода
        self.output_text = tk.Text(output_frame, wrap=WORD, 
                                   bg="#f8f9fa", fg="#212529",
                                   font=("Consolas", 10), 
                                   insertbackground="#000000",
                                   selectbackground="#add6ff",
                                   selectforeground="#000000",
                                   padx=5, pady=5,
                                   relief=FLAT,
                                   borderwidth=0)
        self.output_text.pack(fill=BOTH, expand=True)
        
        # Скроллбар для вывода
        output_scroll = tb.Scrollbar(output_frame, orient=VERTICAL, 
                                    command=self.output_text.yview)
        output_scroll.pack(side=RIGHT, fill=Y)
        self.output_text.config(yscrollcommand=output_scroll.set)
        
        # Информационная панель
        info_frame = tb.Frame(self.root, bootstyle="secondary")
        info_frame.pack(fill=X, side=BOTTOM, padx=5, pady=(0, 5))
        
        self.status_label = tb.Label(info_frame, text="Готов к работе", 
                                     font=("Segoe UI", 9))
        self.status_label.pack(side=LEFT, padx=5)
        
        self.cursor_pos_label = tb.Label(info_frame, text="Стр: 1, Стлб: 1",
                                        font=("Segoe UI", 9))
        self.cursor_pos_label.pack(side=RIGHT, padx=5)
        
        # Привязка событий
        self.editor.text.bind('<<CursorMove>>', self.update_cursor_position)
        self.editor.text.bind('<KeyRelease>', self.on_key_release)
        self.editor.text.bind('<KeyRelease>', self.update_file_stats, add=True)
        
    def setup_shortcuts(self):
        """Настройка горячих клавиш"""
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<F5>', lambda e: self.run_code())
    
    def switch_language(self, lang_code):
        """Переключение языка интерфейса"""
        # Устанавливаем язык
        if lang_manager.set_language(lang_code):
            # Обновляем интерфейс
            self.update_ui_language()
            
            # Показываем сообщение
            self.status_label.config(
                text=f"Язык: {lang_manager.get_language_name()}"
            )
        
    
    def update_ui_language(self):
        """Обновляет текст в интерфейсе при смене языка"""
        # Обновляем заголовок окна
        self.root.title(f"AMIGA IDE - {lang_manager.get_text('language')}")
        
        # Обновляем статус
        self.status_label.config(text=lang_manager.get_text("status.ready"))
        
        # Обновляем заголовки в консоли
        # (тут можно добавить больше обновлений)


    def new_file(self):
        """Создать новый файл"""
        if self.editor.get_all_text() and messagebox.askyesno("Сохранение", 
                                                              "Сохранить текущий файл?"):
            self.save_file()
        
        self.editor.clear()
        self.current_file = None
        self.root.title("AMIGA IDE - Новый файл")
        self.status_label.config(text="Новый файл создан")
        self.update_file_stats()
        
    def open_file(self):
        """Открыть файл"""
        filename = filedialog.askopenfilename(
            title="Открыть файл AMIGA 1",
            filetypes=[
                ("AMIGA 1 files", "*.amiga1"),
                ("Legacy AMIGA files", "*.amiga"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                # Проверяем расширение
                ext = os.path.splitext(filename)[1].lower()
                
                if ext == '.amiga2' or ext == '.amiga3':
                    messagebox.showwarning(
                        "Предупреждение",
                        f"Файл {ext} предназначен для более новой версии AMIGA.\n"
                        "Возможны ошибки совместимости!"
                    )
                
                with open(filename, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                self.editor.set_text(content)
                self.current_file = filename
                self.root.title(f"AMIGA IDE - {os.path.basename(filename)}")
                self.status_label.config(text=f"Открыт файл: {filename}")
                self.update_file_stats()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл: {str(e)}")

    def save_file(self):
        """Сохранить файл"""
        if self.current_file:
            # Сохраняем в исходном формате
            try:
                content = self.editor.get_all_text()
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.status_label.config(text=f"Сохранено: {self.current_file}")
                self.update_file_stats()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")
        else:
            self.save_as_file()

    def save_as_file(self):
        """Сохранить как"""
        filename = filedialog.asksaveasfilename(
            title="Сохранить файл AMIGA 1",
            defaultextension=".amiga1",
            filetypes=[
                ("AMIGA 1 files", "*.amiga1"),
                ("Legacy AMIGA files", "*.amiga"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            self.current_file = filename
            self.save_file()
            self.root.title(f"AMIGA IDE - {os.path.basename(filename)}")
    
    def toggle_theme(self, theme_name):
        """Переключение темы"""
        self.current_theme = theme_name
        
        # Применяем тему к редактору
        self.editor.apply_theme(theme_name)
        
        # Применяем тему к输出
        theme = THEMES[theme_name]
        self.output_text.config(
            bg=theme["output"]["bg"],
            fg=theme["output"]["fg"]
        )
        
        # Обновляем статус
        self.status_label.config(
            text=f"Тема: {theme['name']}"
        )
    
    def run_code(self):
        """Запустить код на AMIGA"""
        code = self.editor.get_all_text()
        if not code.strip():
            messagebox.showwarning("Предупреждение", "Нет кода для выполнения")
            return
        
        self.clear_output()
        
        # Настраиваем теги для цветного вывода
        self.output_text.tag_configure("output", foreground="#212529")
        self.output_text.tag_configure("error", foreground="#dc3545", font=("Consolas", 10, "bold"))
        
        try:
            # Запуск интерпретатора
            self.interpreter.run(code)
            self.status_label.config(text="Программа выполнена успешно")
            
        except Exception as e:
            self.output_text.insert(END, f"Ошибка: {str(e)}\n", "error")
            self.status_label.config(text=f"Ошибка: {str(e)}")
    
    def append_output(self, text, end="\n"):
        """Добавить текст в вывод"""
        self.output_text.insert(END, text + end, "output")
        self.output_text.see(END)
        self.root.update()
    
    def get_input(self, prompt=""):
        """Получить ввод от пользователя"""
        # Показываем диалог ввода
        self.root.focus_force()
        result = simpledialog.askstring("Ввод", prompt, parent=self.root)
        return result if result else ""
    
    def clear_output(self):
        """Очистить вывод"""
        self.output_text.delete(1.0, END)
    
    def update_cursor_position(self, event=None):
        """Обновить информацию о позиции курсора"""
        try:
            cursor_pos = self.editor.text.index(tk.INSERT)
            line, col = cursor_pos.split('.')
            self.cursor_pos_label.config(text=f"Стр: {line}, Стлб: {int(col) + 1}")
        except:
            pass
    
    def update_file_stats(self, event=None):
        """Обновить статистику файла"""
        try:
            content = self.editor.get_all_text()
            lines = len(content.split('\n'))
            chars = len(content)
            
            if self.current_file:
                filename = os.path.basename(self.current_file)
                self.file_stats_label.config(text=f"{filename} | {lines} строк | {chars} символов")
            else:
                self.file_stats_label.config(text=f"{lines} строк | {chars} символов")
        except:
            pass
    
    def on_key_release(self, event=None):
        """Обработка отпускания клавиш"""
        self.update_cursor_position()
    
    def show_about(self):
        """Показать информацию о программе"""
        AboutWindow(self.root, self.assets_path)

def main():
    root = tb.Window(themename="cyborg")
    app = AMIGAIDE(root)
    root.mainloop()

if __name__ == "__main__":
    main()