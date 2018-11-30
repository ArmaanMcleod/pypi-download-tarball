from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="download-tarball",
    version="0.0.6", 
    description="Automates manual installation of Python modules.",
    long_description=long_description, 
    long_description_content_type="text/markdown",
    url="https://github.com/OpticGenius/download-tarball",
    author="Armaan McLeod",
    author_email="opticgenius@hotmail.com", 
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="python tarball download",
    py_modules=["download"],
    packages=find_packages(exclude=[]),
    install_requires=["tqdm", "requests", "beautifulsoup4"],
    extras_require={}, 
    package_data={},
    data_files=[],  
    entry_points={"console_scripts": ["download=download:main"]}, 
    project_urls={  
        "Bug Reports": "https://github.com/OpticGenius/download-tarball/issues",
        "Source": "https://github.com/OpticGenius/download-tarball",
    },
)
