# setup.py
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import setuptools
import os
import pybind11
import subprocess


class get_pybind_include:
    """Helper class to get pybind11 include path"""

    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)


# Вариант 1: Если pybind11 установлен через pip
def get_pybind11_include_path():
    return pybind11.get_include()


# Настройка расширения
ext_modules = [
    Extension(
        'cpp_module.motif_counter_cpp',  # Имя модуля
        [
            'cpp_module/pywrap.cpp',  # Файлы исходников
        ],
        include_dirs=[
            # Путь к pybind11
            get_pybind11_include_path() or get_pybind_include(),
            # Путь к Python.h
            sys.prefix + '/include/python' + sys.version[:3] + '/',
        ],
        library_dirs=[
            # Дополнительные библиотеки если нужны
        ],
        extra_compile_args=[
            '-std=c++11',  # или c++14, c++17
            '-O3',  # оптимизация
            '-Wall',  # предупреждения
            '-shared',
            '-fPIC',  # позиционно-независимый код
        ] if sys.platform != 'win32' else [
            '/std:c++14',
            '/O2',
        ],
        extra_link_args=[
            # Дополнительные флаги линковки если нужны
        ],
        language='c++'
    ),
]

# Для Windows может потребоваться другой подход
if sys.platform == 'win32':
    ext_modules[0].extra_compile_args = ['/std:c++14', '/O2', '/EHsc']

setup(
    name='motif_counter_cpp',
    version='0.1.0',
    author='Your Name',
    description='C++ module for motif counting',
    ext_modules=ext_modules,
    install_requires=[
        'pybind11>=2.6.0',
    ],
    setup_requires=[
        'pybind11>=2.6.0',
    ],
    cmdclass={
        'build_ext': build_ext
    },
    zip_safe=False,
)
