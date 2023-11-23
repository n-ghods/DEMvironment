# -*- coding: utf-8 -*-
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

# -*- coding: utf-8 -*-
import numpy

import Orange.data
from orangewidget.widget import OWBaseWidget, Input, Output
from orangewidget.utils.widgetpreview import WidgetPreview
from orangewidget import gui

class OWRun(OWBaseWidget):
    name = "Run Calibration"
    description = "Run a calibration workflow"
    icon = "icons/run.png"
    priority = 10

    class Inputs:
        data = Input("Data", Orange.data.Table)

    class Outputs:
        sample = Output("Sampled Data", Orange.data.Table)

    want_main_area = False

    def __init__(self):
        super().__init__()

        # GUI
        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(box, 'No data on input yet, waiting to get something.')
        self.infob = gui.widgetLabel(box, '')

    @Inputs.data
    def set_data(self, dataset):
        if dataset is not None:
            self.infoa.setText('%d instances in input dataset' % len(dataset))
            indices = numpy.random.permutation(len(dataset))
            indices = indices[:int(numpy.ceil(len(dataset) * 0.1))]
            sample = dataset[indices]
            self.infob.setText('%d sampled instances' % len(sample))
            self.Outputs.sample.send(sample)
        else:
            self.infoa.setText('No data on input yet, waiting to get something.')
            self.infob.setText('')
            self.Outputs.sample.send("Sampled Data")