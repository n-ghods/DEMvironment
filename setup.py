"""
This file is part of the "DEMvironment" Add-on package for Orange3, that 
facilitates the data management of the DEM parameter calibration, Mainly using
Aspherix(c) as a DEM calibration tool.
DEMvironment add-on is a free software: you can redistribute it
and/or modify it under the  terms of the GNU General Public License as 
published by the Free Software  Foundation, either version 3 of the License,
or (at your option) any later version.

DEMvironment add-on is distributed in the hope that it will be useful, but WITHOUT ANY
 WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
 A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
 PP-SBSC. If not, see <https://www.gnu.org/licenses/>.
 
 -------------------------------------------------------------------------
    Contributing author and copyright for this file:
        
        Copyright (c) 2023    Nazanin Ghods (TU Graz)
        Copyright (c) 2023    Richard Amering (TU Graz)
        Copyright (c) 2023    Stefan Radl (TU Graz)
 -------------------------------------------------------------------------
"""
from setuptools import setup


NAME = "DEMvironment"
VERSION = "1.0.0"
AUTHOR = 'Nazanin Ghods'
AUTHOR_EMAIL = 'n_ghods@ymail.com'
DESCRIPTION = "Add-on containing widgets for the data management of DEM parameter calibration files"
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

