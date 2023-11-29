from setuptools import setup
from scripts import params

setup(
    name=params.name,
    version=params.version,
    description=params.description,
    long_description="README.md",
    long_description_content_type="text/markdown",
    url="",
    author="Willy LUTZ",
    author_email="willy.lutz@irim.cnrs.fr",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=["scripts", "data", "venv"],
    include_package_data=True,
    install_requires=[
        "fiiireflyyy", "customtkinter", "pillow"
    ],
    entry_points={"console_scripts": ["firelearnGUI=scripts.firelearnGUI.__main__:main"]},
)
