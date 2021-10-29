from setuptools import setup, find_packages


VERSION = '0.0.1'
DESCRIPTION = 'Lambda layer for authentication'
LONG_DESCRIPTION = 'Lambda layer for authentication'

setup(
    name='lambda_utils',
    version=VERSION,
    author='Mark de Blaauw',
    author_email='mdeblaauw@mobiquity.com',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(include=['lambda_utils', 'lambda_utils.*']),
    install_requires=[],
    keywords=['AWS', 'AWS Lambda', 'Authentication']
)
