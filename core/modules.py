# -*- coding: utf-8 -*-
import time

class ConsoleModule:
    """Модуль Console для ввода/вывода"""
    
    def __init__(self, output_callback=None, input_callback=None):
        self.output_callback = output_callback
        self.input_callback = input_callback or input
    
    def Print(self, *args):
        """Выводит текст в консоль"""
        texts = []
        for arg in args:
            if isinstance(arg, str):
                texts.append(arg)
            else:
                texts.append(str(arg))
        
        output = " ".join(texts)
        if self.output_callback:
            self.output_callback(output)
        return output
    
    def Input(self, prompt=""):
        """Вводит текст из консоли"""
        if self.output_callback:
            self.output_callback(prompt, end="")
        
        if self.input_callback:
            value = self.input_callback()
            return value
        return ""

class TimesModule:
    """Модуль Times для работы со временем и циклами"""
    
    def __init__(self, output_callback=None):
        self.output_callback = output_callback
    
    class Seconds:
        """Класс для работы с секундами"""
        def __init__(self, value):
            self.value = float(value)
        
        def __str__(self):
            return f"{self.value}с"
        
        def __float__(self):
            return self.value
    
    class Range:
        """Класс для диапазонов"""
        def __init__(self, end):
            self.start = 0
            self.end = int(end)
            self.current = self.start
        
        def __iter__(self):
            return self
        
        def __next__(self):
            if self.current < self.end:
                value = self.current
                self.current += 1
                return value
            raise StopIteration
        
        def reset(self):
            """Сброс итератора"""
            self.current = self.start
    
    class Timer:
        """Таймер для each цикла"""
        def __init__(self, delay):
            self.delay = float(delay)
            self.last_time = time.time()
        
        def Delay(self):
            """Проверяет, прошло ли достаточно времени"""
            current_time = time.time()
            if current_time - self.last_time >= self.delay:
                self.last_time = current_time
                return True
            return False
    
    def Range(self, value):
        """Создает диапазон"""
        return self.Range(value)
    
    def Seconds(self, value):
        """Создает объект секунд"""
        return self.Seconds(value)
    
    def Timer(self, delay):
        """Создает таймер"""
        return self.Timer(delay)