"""Setup for AiiDA registry."""

from __future__ import absolute_import
from setuptools import setup, find_packages

if __name__ == '__main__':
    setup(
        name='aiida-registry',
        packages=find_packages(),
        long_description=open('README.md').read(),
        long_description_content_type='text/markdown',
        version='0.2.0',
        description='Registry of AiiDA plugins.',
        author='AiiDA Team',
        author_email='aiidateam@gmail.com',
        url='https://aiidateam.github.io/aiida-registry/',
        scripts=['bin/aiida-registry'],
        install_requires=[
            "jinja2",
            "pipenv",
            "requests",
            "requests-cache",
            "requirements-parser",
            "tomlkit",
            "poetry",
            "click",
        ],
        license='MIT',
        extras_require={
            'pre-commit': [
                "astroid==1.6.6; python_version<'3.0'",
                "astroid==2.2.5; python_version>='3.0'",
                "pre-commit==1.17.0",
                "yapf==0.28.0",
                "prospector==1.1.7",
                "pylint==1.9.4; python_version<'3.0'",
                "pylint==2.3.1; python_version>='3.0'",
            ]
        },
    )
