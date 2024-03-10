#!/usr/bin/env python3

from setuptools import setup
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

with open("requirements.txt") as f:
    required_packages = f.read().splitlines()

setup(
    name="gerrit-utils",
    version="1.0",
    description="A simple tool to interact with gerrit using SSH.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="SamarV-121",
    author_email="samar@samarv121.dev",
    python_requires=">=3.10",
    install_requires=required_packages,
    url="https://github.com/SamarV-121/gerrit-utils",
    packages=["gerrit", "gerrit.utils"],
    scripts=["gerrit-utils"],
)
