# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import PhotoImage
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import os
from PIL import Image, ImageTk

class AboutWindow:
    """Окно 'О программе' с логотипом AMIGA"""
    
    def __init__(self, parent, assets_path):
        self.parent = parent
        self.assets_path = assets_path
        self.logo_image = None  # Для хранения ссылки на изображение
        
        # Создаем окно с ttkbootstrap
        self.window = tb.Toplevel(parent)
        self.window.title("О программе AMIGA IDE")
        self.window.geometry("550x650")
        self.window.resizable(False, False)
        
        # Делаем окно модальным
        self.window.transient(parent)
        self.window.grab_set()
        
        # Центрируем окно относительно родителя
        self.center_window()
        
        self.setup_ui()
        
    def center_window(self):
        """Центрирует окно относительно родительского"""
        self.window.update_idletasks()
        
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        window_width = 550
        window_height = 650
        
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def setup_ui(self):
        """Создание интерфейса окна"""
        
        # Основной контейнер
        main_frame = tb.Frame(self.window, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Логотип (сверху)
        self.add_logo(main_frame)
        
        # Разделитель
        tb.Separator(main_frame).pack(fill=X, pady=(15, 10))
        
        # Версия
        version_label = tb.Label(
            main_frame,
            text="Версия 1.0.0",
            font=("Segoe UI", 12),
            bootstyle="secondary"
        )
        version_label.pack()
        
        # Разделитель
        tb.Separator(main_frame).pack(fill=X, pady=15)
        
        # Текстовая информация
        self.add_info_text(main_frame)
        
        # Разделитель
        tb.Separator(main_frame).pack(fill=X, pady=15)
        
        # Кнопка закрытия
        button_frame = tb.Frame(main_frame)
        button_frame.pack(fill=X)
        
        close_button = tb.Button(
            button_frame,
            text="Закрыть",
            command=self.window.destroy,
            bootstyle="success",
            width=20
        )
        close_button.pack()
        
        # Копирайт
        copyright_label = tb.Label(
            main_frame,
            text="© 2026 xCore Team. Все права защищены.",
            font=("Segoe UI", 8),
            bootstyle="secondary"
        )
        copyright_label.pack(pady=(10, 0))
    
    def add_logo(self, parent):
        """Добавляет логотип AMIGA используя PIL"""
        
        # Создаем фрейм для логотипа с фиксированным размером
        logo_frame = tb.Frame(parent, width=300, height=120)
        logo_frame.pack(pady=(0, 10))
        logo_frame.pack_propagate(False)
        
        # Путь к файлу логотипа
        logo_path = os.path.join(self.assets_path, "amiga_logo.png")
        
        try:
            if os.path.exists(logo_path):
                # Загружаем изображение через PIL
                pil_image = Image.open(logo_path)
                
                # Изменяем размер до 300x120 (если нужно)
                pil_image = pil_image.resize((300, 120), Image.Resampling.LANCZOS)
                
                # Конвертируем для Tkinter
                self.logo_image = ImageTk.PhotoImage(pil_image)
                
                # Создаем метку с изображением
                logo_label = tb.Label(
                    logo_frame,
                    image=self.logo_image,
                    bootstyle="default"
                )
                logo_label.pack(expand=True)
                
                print(f"Логотип загружен: {logo_path}")  # Отладка
            else:
                print(f"Файл логотипа не найден: {logo_path}")
                self.create_text_logo(logo_frame)
        except Exception as e:
            print(f"Ошибка загрузки логотипа: {e}")
            import traceback
            traceback.print_exc()
            self.create_text_logo(logo_frame)
    
    def create_text_logo(self, parent):
        """Создает текстовый логотип если изображение не найдено"""
        
        # Рамка для текстового логотипа
        logo_box = tb.Frame(
            parent,
            bootstyle="danger",
            width=280,
            height=100
        )
        logo_box.pack(expand=True)
        logo_box.pack_propagate(False)
        
        # Текст логотипа
        logo_text = tb.Label(
            logo_box,
            text="AMIGA",
            font=("Times New Roman", 36),
            bootstyle="inverse-danger"
        )
        logo_text.pack(expand=True)
        
        # Подпись
        subtitle = tb.Label(
            logo_box,
            text="Язык программирования",
            font=("Times New Roman", 10, "italic"),
            bootstyle="inverse-danger"
        )
        subtitle.pack()
    
    def add_info_text(self, parent):
        """Добавляет текстовую информацию о программе"""
        
        # Создаем фрейм для текста
        text_frame = tb.Frame(parent)
        text_frame.pack(fill=BOTH, expand=True)
        
        # Текстовое поле с информацией
        info_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg="#f8f9fa",
            fg="#212529",
            relief=tk.FLAT,
            borderwidth=0,
            height=15,
            cursor="arrow"
        )
        info_text.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Скроллбар
        scrollbar = tb.Scrollbar(
            text_frame,
            orient=VERTICAL,
            command=info_text.yview
        )
        scrollbar.pack(side=RIGHT, fill=Y)
        info_text.config(yscrollcommand=scrollbar.set)
        
        # Делаем текст нередактируемым
        info_text.config(state=tk.NORMAL)
        
        # Настраиваем теги для форматирования
        info_text.tag_configure("title", font=("Segoe UI", 11, "bold"), foreground="#28a745")
        info_text.tag_configure("bullet", font=("Segoe UI", 10), foreground="#212529")
        info_text.tag_configure("keyword", font=("Segoe UI", 10, "bold"), foreground="#0066cc")
        info_text.tag_configure("comment", font=("Segoe UI", 10, "italic"), foreground="#6c757d")
        info_text.tag_configure("decorator", font=("Segoe UI", 10, "bold"), foreground="#dc3545")
        info_text.tag_configure("center", justify="center")
        
        # Вставляем информацию
        self.insert_info_text(info_text)
        
        # Запрещаем редактирование
        info_text.config(state=tk.DISABLED)
    
    def insert_info_text(self, text_widget):
        """Вставляет информацию с форматированием"""
        
        # Заголовок
        text_widget.insert(tk.END, "О языке AMIGA\n", ("title", "center"))
        text_widget.insert(tk.END, "\n")
        
        # Описание
        text_widget.insert(tk.END, "AMIGA - это современный язык программирования, ")
        text_widget.insert(tk.END, "разработанный для обучения и профессиональной разработки. ")
        text_widget.insert(tk.END, "Он сочетает простоту синтаксиса с мощью объектно-ориентированного подхода.\n\n")
        
        # Особенности
        text_widget.insert(tk.END, "✨ Особенности языка:\n", ("title"))
        text_widget.insert(tk.END, "   • Поддержка классов и объектов\n")
        text_widget.insert(tk.END, "   • Области видимости (local/global, private/public)\n")
        text_widget.insert(tk.END, "   • Различные типы циклов (each, for, while)\n")
        text_widget.insert(tk.END, "   • Условные операторы\n")
        text_widget.insert(tk.END, "   • Модульная система\n")
        text_widget.insert(tk.END, "   • Простой и понятный синтаксис\n\n")
        
        # Пример кода
        text_widget.insert(tk.END, "📝 Пример кода на AMIGA:\n", ("title"))
        text_widget.insert(tk.END, "\n")
        text_widget.insert(tk.END, "@use ", ("decorator"))
        text_widget.insert(tk.END, "Console;\n")
        text_widget.insert(tk.END, "\n")
        text_widget.insert(tk.END, "private local class ", ("keyword"))
        text_widget.insert(tk.END, "App ")
        text_widget.insert(tk.END, "{\n")
        text_widget.insert(tk.END, "    global define ", ("keyword"))
        text_widget.insert(tk.END, "OnRun() ")
        text_widget.insert(tk.END, "{\n")
        text_widget.insert(tk.END, "        ", ("comment"))
        text_widget.insert(tk.END, "// Это комментарий\n", ("comment"))
        text_widget.insert(tk.END, "        ", ("keyword"))
        text_widget.insert(tk.END, "Console")
        text_widget.insert(tk.END, ".", ("operator"))
        text_widget.insert(tk.END, "Print", ("keyword"))
        text_widget.insert(tk.END, "(\"Hello World!\");\n")
        text_widget.insert(tk.END, "    }\n")
        text_widget.insert(tk.END, "}\n")
        text_widget.insert(tk.END, "\n")
        
        # Информация о среде
        text_widget.insert(tk.END, "🛠 AMIGA IDE:\n", ("title"))
        text_widget.insert(tk.END, "   • Подсветка синтаксиса\n")
        text_widget.insert(tk.END, "   • Автодополнение скобок\n")
        text_widget.insert(tk.END, "   • Номера строк\n")
        text_widget.insert(tk.END, "   • Встроенный интерпретатор\n")
        text_widget.insert(tk.END, "   • Консоль вывода\n\n")
        
        # Горячие клавиши
        text_widget.insert(tk.END, "⌨ Горячие клавиши:\n", ("title"))
        text_widget.insert(tk.END, "   • ", ("bullet"))
        text_widget.insert(tk.END, "Ctrl+N", ("keyword"))
        text_widget.insert(tk.END, " - Новый файл\n")
        text_widget.insert(tk.END, "   • ", ("bullet"))
        text_widget.insert(tk.END, "Ctrl+O", ("keyword"))
        text_widget.insert(tk.END, " - Открыть файл\n")
        text_widget.insert(tk.END, "   • ", ("bullet"))
        text_widget.insert(tk.END, "Ctrl+S", ("keyword"))
        text_widget.insert(tk.END, " - Сохранить файл\n")
        text_widget.insert(tk.END, "   • ", ("bullet"))
        text_widget.insert(tk.END, "F5", ("keyword"))
        text_widget.insert(tk.END, " - Запустить программу\n")