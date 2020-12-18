from setuptools import setup, find_packages

setup(name='pywdl',
      version='0.0.1',
      package_dir={'': 'src'},
      packages=find_packages(where='src'),
      install_requires=[
          "antlr4-python3-runtime==4.8",
          "toil"  # TODO: temporarily
      ])
