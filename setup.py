# Setuptools configuration for ABAC utilities
# Copyright (C) 2021 Hariyala Omakara Naga Sai Varshith

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="abac",
    version="0.0.1",
    author="H.O Sai Varshith",
    author_email="hosvarshith@gmail.com",
    description="Command-Line tool to manage the ABAC Linux Security Module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/saivarshith2000/mtp",
    project_urls={
        "Bug Tracker": "https://github.com/saivarshith2000/mtp",
    },
    packages=setuptools.find_packages(),
    entry_points ={
            'console_scripts': [
                'abac = src.main:main'
            ]
    },
    install_requires = ["click", "watchdog", "apscheduler"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.6",
        "Operating System :: POSIX",
    ],
    python_requires=">=3.6",
)
