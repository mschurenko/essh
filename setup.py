from setuptools import setup

setup(
    name='essh',
    version='0.1.0',
    author='Matt Schurenko',
    author_email='matt.schurenko@gmail.com',
    packages=['essh'],
    entry_points='''
        [console_scripts]
        essh=essh.cli:cli
    ''',
    install_requires=[
        'boto3>=1.7.27',
        'click>=6.7',
    ],
)
