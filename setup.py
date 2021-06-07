"""Main setup script."""

import setuptools  # type: ignore
import pathlib
import subprocess
import enebootools


with open("requirements.txt") as f:
    required = f.read().splitlines()

version_ = enebootools.__VERSION__

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="enebootools",
    version=version_,
    author="David Martínez Martí, José A. Fernández Fernández",
    author_email="deavidsedice@gmail.com, aullasistemas@gmail.com",
    description="ERP tools for Eneboo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aulla/eneboo-tools",
    packages=setuptools.find_packages(),
    package_data={
    	"enebootools": ["*"],
    },
    install_requires=required,
    keywords="erp pineboo eneboo tools",
    python_requires=">=3.6.9",
    entry_points={
        "console_scripts": [
            "eneboo-assembler=enebootools.entry_points:main_assembler",
            "eneboo-crypto=enebootools.entry_points:main_crypto",
            "eneboo-mergetool=enebootools.entry_points:main_mergetool",
            "eneboo-packager=enebootools.entry_points:main_packages",

        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Environment :: X11 Applications :: Qt",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Typing :: Typed",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Natural Language :: Spanish",
        "Operating System :: OS Independent",
    ],
)
