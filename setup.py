from setuptools import setup, find_namespace_packages

setup(
    name="quisby",
    version="0.0.1",
    description="",
    packages=find_namespace_packages(),
    long_description=open("README.md").read(),
    install_requires=[
        "boto3",
        "botocore",
        "google-api-core",
        "google-api-python-client",
        "google-auth",
        "google-auth-httplib2",
        "google-auth-oauthlib",
        "googleapis-common-protos",
    ],
    entry_points={
        "console_scripts": [
            "quisby = quisby.quisby:main",
        ]
    },
)
