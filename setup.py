from setuptools import setup, find_packages

setup(name='pywdl',
      version='0.0.1',
      packages=find_packages('.'),
      install_requires=[
          "antlr4-python3-runtime==4.8",
      ])
