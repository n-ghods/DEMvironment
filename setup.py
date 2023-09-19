from setuptools import setup


NAME = "DEMvironment"
VERSION = "0.0.3"
AUTHOR = 'Nazanin Ghods'
AUTHOR_EMAIL = 'n_ghods@ymail.com'
DESCRIPTION = "Add-on containing widgets for the data management of DEM simulation files"
INSTALL_REQUIRES = [
    'Orange3',
]


setup(name=NAME,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      description=DESCRIPTION,
      packages=["orangedemvironment"],
      version=VERSION,
      package_data={"orangedemvironment": ["icons\*.png"]},
      classifiers=["Example :: Invalid"],
      # Declare orangedemo package to contain widgets for the "Demo" category
      entry_points={"orange.widgets": "DEMvironment = orangedemvironment"},
      )# -*- coding: utf-8 -*-

