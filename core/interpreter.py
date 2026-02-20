# -*- coding: utf-8 -*-
import re
import time
from .modules import ConsoleModule, TimesModule

class AMIGAInterpreter:
    """Интерпретатор языка AMIGA"""
    
    def __init__(self):
        self.variables = {}  # локальные переменные
        self.global_vars = {}  # глобальные переменные
        self.classes = {}
        self.current_class = None
        self.current_method = None
        self.output_callback = print
        self.input_callback = input
        
        # Модули
        self.modules = {
            "Console": ConsoleModule(self.output, self.input),
            "Times": TimesModule(self.output)
        }
        self.imported_modules = set()
        
        # Управление циклами
        self.loop_break = False
        self.loop_continue = False
        
    def output(self, text, end="\n"):
        """Вывод текста"""
        if self.output_callback:
            self.output_callback(text + end)
    
    def input(self, prompt=""):
        """Ввод текста"""
        if self.input_callback:
            return self.input_callback(prompt)
        return ""
    
    def run(self, code: str):
        """Запускает программу на AMIGA"""
        lines = code.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Пропускаем пустые строки
            if not line:
                i += 1
                continue
            
            try:
                i = self.execute_line(lines, i)
            except Exception as e:
                self.output("Ошибка в строке {}: {}".format(i + 1, str(e)))
                raise e
    
    def execute_line(self, lines, index):
        """Выполняет одну строку кода"""
        line = lines[index].strip()
        
        # Комментарии
        if line.startswith('//'):
            return index + 1
        
        # @use
        if line.startswith('@use'):
            return self.handle_use(lines, index)
        
        # @in
        if line.startswith('@in'):
            return self.handle_in(lines, index)
        
        # class
        if 'class' in line and not line.startswith('//'):
            return self.handle_class(lines, index)
        
        # define
        if 'define' in line and not line.startswith('//'):
            return self.handle_method(lines, index)
        
        # Объявление переменных с типом (local string name)
        if line.startswith(('local ', 'global ')):
            self.handle_typed_variable(line)
            return index + 1
        
        # Объявление переменных с >>
        if '>>' in line and not line.startswith('//'):
            self.handle_variable_declaration(line)
            return index + 1
        
        # each цикл
        if line.startswith('each '):
            return self.handle_each_loop(lines, index)
        
        # for цикл
        if line.startswith('for '):
            return self.handle_for_loop(lines, index)
        
        # while цикл
        if line.startswith('while '):
            return self.handle_while_loop(lines, index)
        
        # if условие (многострочное)
        if line.startswith('if '):
            return self.handle_if_statement(lines, index)
        
        # else
        if line.startswith('else'):
            return self.handle_else(lines, index)
        
        # break
        if line.startswith('break'):
            self.loop_break = True
            return index + 1
        
        # continue
        if line.startswith('continue'):
            self.loop_continue = True
            return index + 1
        
        # Вызов методов
        if '.Print' in line or '.Input' in line:
            self.handle_method_call(line)
        
        return index + 1
    
    def handle_typed_variable(self, line):
        """Обрабатывает объявление типизированной переменной"""
        # local string name = Console.Input("Введите своё имя: ");
        parts = line.split('=', 1)
        declaration = parts[0].strip()
        value_expr = parts[1].strip().rstrip(';') if len(parts) > 1 else None
        
        # Разбираем объявление
        decl_parts = declaration.split()
        if len(decl_parts) >= 3:
            scope = decl_parts[0]  # local или global
            var_type = decl_parts[1]  # string, int, float
            var_name = decl_parts[2]  # имя переменной
            
            # Вычисляем значение
            if value_expr:
                value = self.evaluate_expression(value_expr)
                
                # Преобразуем к нужному типу
                if var_type == "int":
                    try:
                        value = int(float(value))
                    except:
                        value = 0
                elif var_type == "float":
                    try:
                        value = float(value)
                    except:
                        value = 0.0
                elif var_type == "string":
                    value = str(value)
            else:
                # Значение по умолчанию
                if var_type == "int":
                    value = 0
                elif var_type == "float":
                    value = 0.0
                else:
                    value = ""
            
            # Сохраняем переменную
            if scope == "global":
                self.global_vars[var_name] = value
            else:
                self.variables[var_name] = value
    
    def handle_use(self, lines, index):
        """Обрабатывает @use module;"""
        line = lines[index].strip()
        parts = line.split()
        if len(parts) >= 2:
            module_name = parts[1].rstrip(';')
            if module_name in self.modules:
                self.imported_modules.add(module_name)
        return index + 1
    
    def handle_in(self, lines, index):
        """Обрабатывает @in Times.Loops @use _all;"""
        line = lines[index].strip()
        parts = line.split()
        if len(parts) >= 3:
            module_path = parts[1]  # Times.Loops
            module_name = module_path.split('.')[0]
            if module_name in self.modules:
                self.imported_modules.add(module_name)
        return index + 1
    
    def handle_class(self, lines, index):
        """Обрабатывает объявление класса"""
        line = lines[index].strip()
        parts = line.split()
        if len(parts) >= 4:
            class_name = parts[3].rstrip('{').strip()
            self.current_class = class_name
            self.classes[class_name] = {
                'methods': {},
                'variables': {}
            }
        return index + 1
    
    def handle_method(self, lines, index):
        """Обрабатывает объявление метода"""
        line = lines[index].strip()
        
        # global define OnRun() {
        method_name = line.split()[2].split('(')[0]
        self.current_method = method_name
        
        # Ищем тело метода до закрывающей скобки
        i = index + 1
        body_lines = []
        brace_count = 1
        
        while i < len(lines) and brace_count > 0:
            current_line = lines[i]
            brace_count += current_line.count('{')
            brace_count -= current_line.count('}')
            
            if brace_count > 0 or current_line.strip():
                if not (current_line.strip() == '}' and brace_count == 0):
                    body_lines.append(current_line)
            
            i += 1
        
        # Сохраняем метод
        if self.current_class:
            self.classes[self.current_class]['methods'][method_name] = {
                'body': body_lines,
                'params': []
            }
            
            # Если это метод OnRun, выполняем его сразу
            if method_name == "OnRun":
                self.execute_method_body(body_lines)
        
        return i
    
    def execute_method_body(self, body_lines):
        """Выполняет тело метода"""
        j = 0
        while j < len(body_lines):
            j = self.execute_line(body_lines, j)
    
    def handle_variable_declaration(self, line):
        """Обрабатывает объявление переменной с >>"""
        parts = line.split('>>')
        if len(parts) == 2:
            var_part = parts[1].strip()
            if '=' in var_part:
                var_name = var_part.split('=')[0].strip()
                value_part = var_part.split('=')[1].strip().rstrip(';')
                
                # Вычисляем значение
                value = self.evaluate_expression(value_part)
                
                # Сохраняем переменную
                self.variables[var_name] = value
    
    def handle_method_call(self, line):
        """Обрабатывает вызов метода"""
        line = line.rstrip(';').strip()
        
        # Обработка интерполяции строк
        if line.startswith('$"'):
            return self.evaluate_string_interpolation(line)
        
        # Обработка Console.Print с конкатенацией
        if '.Print' in line:
            # Разбираем Console.Print("Возраст: " .= age.toString())
            match = re.match(r'Console\.Print\((.*)\)', line)
            if match:
                args_str = match.group(1)
                # Вычисляем аргументы
                result = self.evaluate_expression(args_str)
                # Вызываем Print
                if "Console" in self.modules:
                    self.modules["Console"].Print(result)
                return result
        
        # Обработка Console.Input
        elif '.Input' in line:
            match = re.match(r'Console\.Input\((.*)\)', line)
            if match:
                prompt = match.group(1)
                if prompt.startswith('"') and prompt.endswith('"'):
                    prompt = prompt[1:-1]
                return self.modules["Console"].Input(prompt)
    
    def evaluate_string_interpolation(self, expr):
        """Вычисляет интерполяцию строки $"Имя: {name}" """
        # Убираем $" в начале и " в конце
        content = expr[2:-1]
        
        # Ищем все {выражения}
        result = ""
        last_pos = 0
        in_brace = False
        brace_content = ""
        
        i = 0
        while i < len(content):
            if content[i] == '{' and not in_brace:
                # Добавляем текст до {
                result += content[last_pos:i]
                in_brace = True
                brace_content = ""
            elif content[i] == '}' and in_brace:
                # Вычисляем выражение в скобках
                value = self.evaluate_expression(brace_content)
                result += str(value)
                in_brace = False
                last_pos = i + 1
            elif in_brace:
                brace_content += content[i]
            i += 1
        
        # Добавляем остаток текста
        if last_pos < len(content):
            result += content[last_pos:]
        
        return result
    
    def evaluate_expression(self, expr):
        """Вычисляет выражение"""
        expr = expr.strip()
        
        # Проверяем, является ли выражение вызовом метода
        if '.Print' in expr or '.Input' in expr:
            return self.handle_method_call(expr)
        
        # Проверяем, является ли выражение интерполяцией
        if expr.startswith('$"') and expr.endswith('"'):
            return self.evaluate_string_interpolation(expr)
        
        # Проверяем, является ли выражение числом
        if expr.isdigit():
            return int(expr)
        if expr.replace('.', '').isdigit():
            return float(expr)
        
        # Проверяем, является ли выражение строкой
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]
        
        # Проверяем, является ли выражение переменной
        if expr in self.variables:
            return self.variables[expr]
        if expr in self.global_vars:
            return self.global_vars[expr]
        
        # Проверяем, является ли выражение конкатенацией (.=)
        if '.=' in expr:
            parts = expr.split('.=', 1)
            left = self.evaluate_expression(parts[0].strip())
            right = self.evaluate_expression(parts[1].strip())
            return str(left) + str(right)
        
        # Проверяем, является ли выражение вызовом toString()
        if '.toString()' in expr:
            var_name = expr.replace('.toString()', '').strip()
            if var_name in self.variables:
                return str(self.variables[var_name])
            if var_name in self.global_vars:
                return str(self.global_vars[var_name])
            return var_name
        
        return expr
    
    def handle_if_statement(self, lines, index):
        """Обрабатывает if условие (многострочное)"""
        line = lines[index].strip()
        
        # Извлекаем условие
        condition = line[3:line.find('{')].strip()
        
        # Ищем тело if
        i = index + 1
        if_body = []
        brace_count = 1
        
        while i < len(lines) and brace_count > 0:
            current_line = lines[i]
            brace_count += current_line.count('{')
            brace_count -= current_line.count('}')
            
            if brace_count > 0 or current_line.strip():
                if not (current_line.strip() == '}' and brace_count == 0):
                    if_body.append(current_line)
            
            i += 1
        
        # Вычисляем условие
        condition_value = self.evaluate_expression(condition)
        
        # Приводим к bool
        if isinstance(condition_value, str):
            condition_value = bool(condition_value)
        elif isinstance(condition_value, (int, float)):
            condition_value = condition_value != 0
        
        if condition_value:
            # Выполняем тело if
            j = 0
            while j < len(if_body):
                j = self.execute_line(if_body, j)
            return i
        else:
            # Пропускаем if и ищем else
            return self.skip_to_else(lines, i)
    
    def skip_to_else(self, lines, index):
        """Пропускает блок if и ищет else"""
        i = index
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('else'):
                return self.handle_else(lines, i)
            i += 1
        return i
    
    def handle_else(self, lines, index):
        """Обрабатывает else"""
        line = lines[index].strip()
        
        # Ищем тело else
        i = index + 1
        else_body = []
        brace_count = 1 if '{' in line else 0
        
        while i < len(lines) and brace_count > 0:
            current_line = lines[i]
            brace_count += current_line.count('{')
            brace_count -= current_line.count('}')
            
            if brace_count > 0 or current_line.strip():
                if not (current_line.strip() == '}' and brace_count == 0):
                    else_body.append(current_line)
            
            i += 1
        
        # Выполняем тело else
        j = 0
        while j < len(else_body):
            j = self.execute_line(else_body, j)
        
        return i
    
    def handle_each_loop(self, lines, index):
        """Обрабатывает each цикл"""
        line = lines[index].strip()
        
        try:
            condition = line[5:line.find('{')].strip(' (')
        except:
            condition = ""
        
        # Ищем тело цикла
        i = index + 1
        body_lines = []
        brace_count = 1
        
        while i < len(lines) and brace_count > 0:
            current_line = lines[i]
            brace_count += current_line.count('{')
            brace_count -= current_line.count('}')
            
            if brace_count > 0 or current_line.strip():
                if not (current_line.strip() == '}' and brace_count == 0):
                    body_lines.append(current_line)
            
            i += 1
        
        # Выполняем цикл
        self.loop_break = False
        
        while not self.loop_break:
            try:
                condition_result = self.evaluate_expression(condition)
                
                if isinstance(condition_result, bool) and not condition_result:
                    break
                
                if hasattr(condition_result, 'Delay') and callable(condition_result.Delay):
                    if not condition_result.Delay():
                        time.sleep(0.1)
                        continue
                
                self.loop_continue = False
                j = 0
                while j < len(body_lines):
                    if self.loop_break or self.loop_continue:
                        break
                    j = self.execute_line(body_lines, j)
                
                if self.loop_break:
                    break
            except:
                break
        
        return i
    
    def handle_for_loop(self, lines, index):
        """Обрабатывает for цикл"""
        line = lines[index].strip()
        
        try:
            for_content = line[4:line.find('{')].strip(' (')
            
            if 'in' in for_content:
                var_name, iterable_expr = for_content.split(' in ', 1)
                
                iterable = self.evaluate_expression(iterable_expr)
                
                i = index + 1
                body_lines = []
                brace_count = 1
                
                while i < len(lines) and brace_count > 0:
                    current_line = lines[i]
                    brace_count += current_line.count('{')
                    brace_count -= current_line.count('}')
                    
                    if brace_count > 0 or current_line.strip():
                        if not (current_line.strip() == '}' and brace_count == 0):
                            body_lines.append(current_line)
                    
                    i += 1
                
                self.loop_break = False
                
                if hasattr(iterable, '__iter__'):
                    for item in iterable:
                        if self.loop_break:
                            break
                        
                        self.variables[var_name.strip()] = item
                        
                        self.loop_continue = False
                        j = 0
                        while j < len(body_lines):
                            if self.loop_break or self.loop_continue:
                                break
                            j = self.execute_line(body_lines, j)
                
                return i
        except:
            pass
        
        return index + 1
    
    def handle_while_loop(self, lines, index):
        """Обрабатывает while цикл"""
        line = lines[index].strip()
        
        try:
            condition = line[6:line.find('{')].strip(' (')
        except:
            condition = "true"
        
        i = index + 1
        body_lines = []
        brace_count = 1
        
        while i < len(lines) and brace_count > 0:
            current_line = lines[i]
            brace_count += current_line.count('{')
            brace_count -= current_line.count('}')
            
            if brace_count > 0 or current_line.strip():
                if not (current_line.strip() == '}' and brace_count == 0):
                    body_lines.append(current_line)
            
            i += 1
        
        self.loop_break = False
        
        while True:
            try:
                condition_value = self.evaluate_expression(condition)
                
                if isinstance(condition_value, str):
                    condition_value = bool(condition_value)
                elif isinstance(condition_value, (int, float)):
                    condition_value = condition_value != 0
                
                if not condition_value or self.loop_break:
                    break
                
                self.loop_continue = False
                j = 0
                while j < len(body_lines):
                    if self.loop_break or self.loop_continue:
                        break
                    j = self.execute_line(body_lines, j)
            except:
                break
        
        return i