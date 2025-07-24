from setuptools import setup, find_packages

setup(
    name="ccai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "spacy",
        "pydantic",
        "rich",
    ],
)