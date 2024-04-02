from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
with open('requirements.txt') as f:
    requirements = f.read().splitlines()
setup(
    name="icugpt",
    version="1.0.0",
    author="baicai",
    author_email="",
    description="A gpt agent for icu databases analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ICU-GPT/icu-gpt",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)