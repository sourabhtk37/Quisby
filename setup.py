from setuptools import setup, find_packages

setup(
    name='quisby',
    version='0.0.1',
    description='',
    packages=find_packages(),
    install_requires=[
        "google-auth",
        "google-auth-oauthlib",
        "google-api-python-client",
        "google-auth-httplib2",
        "boto3",
    ],
    long_description=open('README.md').read(),
    entry_points={
        "console_scripts": [
            "quisby = quisby.quisby:main",
        ]
    },
)
