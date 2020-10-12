from setuptools import setup, find_namespace_packages

setup(
    name="quisby",
    version="0.0.1",
    description="",
    packages=find_namespace_packages(),
    long_description=open("README.md").read(),
    entry_points={
        "console_scripts": [
            "quisby = quisby.quisby:main",
        ]
    },
)
