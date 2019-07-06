from os.path import dirname, join
from setuptools import setup, find_packages


with open(join(dirname(__file__), "README.md"), mode="r") as f:
    long_description = f.read()

setup(
    name="scry",
    version="0.1.0",
    description="CLI for MTG set and card info",
    long_description=long_description,
    author="Kian Mehrabani",
    author_email="kianmehrabani@gmail.com",
    packages=find_packages(),
    entry_points={"console_scripts": ["scry = scry.scry:main"]},
)
