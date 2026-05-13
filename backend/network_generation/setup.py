from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import setuptools
import os
import pybind11
import subprocess


# Настройка расширения
ext_modules = [
    Extension(
        'cpp_module.motif_counter_cpp',  # имя модуля
        [
            'cpp_module/pywrap.cpp',  # файл-исходник
        ],
        include_dirs=[
            pybind11.get_include(),  # путь к pybind11
            sys.prefix + '/include/python' + sys.version[:3] + '/',  # путь к Python.h
        ],
        library_dirs=[],
        extra_compile_args=[
            '-std=c++11',  # версия c++
            '-O3',  # оптимизация
            '-Wall',  # предупреждения
            '-shared',
            '-fPIC',  # позиционно-независимый код
            '-fopenmp',  # поддержка OpenMP
        ] if sys.platform != 'win32' else [
            '/std:c++14',
            '/O2',
            '/openmp',  # для Windows MSVC
        ],
        extra_link_args=[
            '-fopenmp',  # линковка OpenMP
        ] if sys.platform != 'win32' else [],
        language='c++'
    ),
]

# Для Windows может потребоваться другой подход
if sys.platform == 'win32':
    ext_modules[0].extra_compile_args = ['/std:c++14', '/O2', '/EHsc', '/openmp']

setup(
    name='motif_counter_cpp',
    version='0.1.0',
    author='Galina Gromova',
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
