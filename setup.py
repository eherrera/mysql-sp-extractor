from setuptools import setup, find_packages
from pathlib import Path

# Leer el README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='mysql-sp-extractor',
    version='0.1.0',
    author='Ernesto Herrera Morales',
    author_email='ernesthmdev@gmail.com',
    description='Extrae procedimientos almacenados de MemSQL/SingleStore/Mysql a archivos individuales',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/eherrera/mysql-sp-extractor',
    project_urls={
        'Bug Tracker': 'https://github.com/eherrera/mysql-sp-extractor/issues',
        'Documentation': 'https://github.com/eherrera/mysql-sp-extractor/#readme',
    },
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'mysql-connector-python>=8.0.0',
        'python-dotenv>=0.19.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
            'mypy>=0.950',
        ],
    },
    entry_points={
        'console_scripts': [
            'mysql-sp-extractor=memsql_sp_extractor.cli:main',
        ],
    },
    keywords='memsql singlestore mysql stored-procedures database backup',
)