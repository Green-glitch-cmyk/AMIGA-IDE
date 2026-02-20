#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для компиляции AMIGA IDE в .exe
Запуск: python build_exe.py
"""

import os
import sys
import shutil
import subprocess

def main():
    print("=" * 60)
    print("Компиляция AMIGA IDE в .exe")
    print("=" * 60)
    
    # Проверяем наличие PyInstaller
    try:
        import PyInstaller
        print("✓ PyInstaller найден")
    except ImportError:
        print("✗ PyInstaller не установлен. Устанавливаем...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Проверяем наличие Pillow
    try:
        import PIL
        print("✓ Pillow найден")
    except ImportError:
        print("✗ Pillow не установлен. Устанавливаем...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    
    # Проверяем наличие ttkbootstrap
    try:
        import ttkbootstrap
        print("✓ ttkbootstrap найден")
    except ImportError:
        print("✗ ttkbootstrap не установлен. Устанавливаем...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "ttkbootstrap"])
    
    # Создаем папку для сборки, если её нет
    if not os.path.exists("build"):
        os.makedirs("build")
    
    if not os.path.exists("dist"):
        os.makedirs("dist")
    
    # Проверяем наличие файлов
    required_files = [
        "main.py",
        "core/interpreter.py",
        "core/modules.py",
        "editor/widget.py",
        "editor/syntax.py",
        "windows/about_window.py",
        "assets/icon.ico",
        "assets/amiga_logo.png",
    ]
    
    all_files_found = True
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"✗ Не найден файл: {file_path}")
            all_files_found = False
    
    if not all_files_found:
        print("\nОшибка: Не все необходимые файлы найдены!")
        return
    
    print("✓ Все необходимые файлы найдены")
    
    # Компилируем
    print("\nНачинаем компиляцию...")
    print("-" * 60)
    
    # Команда для PyInstaller
    cmd = [
        "pyinstaller",
        "--name=AMIGA_IDE",
        "--icon=assets/icon.ico",
        "--windowed",  # Без консоли
        "--onefile",   # Один файл
        "--add-data=assets/icon.ico;assets",
        "--add-data=assets/amiga_logo.png;assets",
        "--hidden-import=PIL",
        "--hidden-import=PIL._tkinter_finder",
        "--hidden-import=ttkbootstrap",
        "--hidden-import=core.interpreter",
        "--hidden-import=core.modules",
        "--hidden-import=editor.widget",
        "--hidden-import=editor.syntax",
        "--hidden-import=windows.about_window",
        "main.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("-" * 60)
        print("\n✓ Компиляция завершена успешно!")
        
        # Копируем .exe в корневую папку
        exe_source = os.path.join("dist", "AMIGA_IDE.exe")
        exe_dest = "AMIGA_IDE.exe"
        
        if os.path.exists(exe_source):
            shutil.copy2(exe_source, exe_dest)
            print(f"✓ Исполняемый файл создан: {exe_dest}")
            
            # Создаем папку с портативной версией
            portable_dir = "AMIGA_IDE_Portable"
            if not os.path.exists(portable_dir):
                os.makedirs(portable_dir)
            
            shutil.copy2(exe_dest, os.path.join(portable_dir, "AMIGA_IDE.exe"))
            
            # Создаем README для портативной версии
            readme_content = """AMIGA IDE - Портативная версия
================================

Инструкция по использованию:
1. Запустите AMIGA_IDE.exe
2. Для работы не требуется установка
3. Все настройки сохраняются в папке с программой

Системные требования:
- Windows 7/8/10/11
- 100 МБ свободного места
- 1 ГБ RAM

Файлы логотипов должны находиться в папке assets рядом с exe файлом.
"""
            
            with open(os.path.join(portable_dir, "README.txt"), "w", encoding="utf-8") as f:
                f.write(readme_content)
            
            # Копируем assets в портативную версию
            portable_assets = os.path.join(portable_dir, "assets")
            if not os.path.exists(portable_assets):
                os.makedirs(portable_assets)
            
            shutil.copy2("assets/icon.ico", portable_assets)
            shutil.copy2("assets/amiga_logo.png", portable_assets)
            
            print(f"✓ Портативная версия создана в папке: {portable_dir}")
            
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Ошибка при компиляции: {e}")
    except Exception as e:
        print(f"\n✗ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    main()