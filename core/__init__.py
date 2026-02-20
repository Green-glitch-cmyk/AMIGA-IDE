# Инициализация пакета core
from .interpreter import AMIGAInterpreter
from .modules import ConsoleModule, TimesModule

__all__ = ['AMIGAInterpreter', 'ConsoleModule', 'TimesModule']