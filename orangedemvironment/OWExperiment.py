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
from PyQt5.QtWidgets import QLineEdit, QTextEdit, QFormLayout, QVBoxLayout, QFileDialog, QComboBox, QSpinBox
from PyQt5.QtWidgets import QCalendarWidget, QDateEdit
from PyQt5.QtCore import QDate
from Orange.widgets import widget, gui, settings
from Orange.data import Table, Domain, StringVariable
from shared.dictHandler import dict_to_orange_table, format_dict_as_text
import json
import os
import re


class OWExperiment(widget.OWWidget):
    name = "Experiment"
    description = "Creates required information (metadata) for experimental files."
    icon = "icons/Experiment.png"
    priority = 2
    want_main_area = True

    # Define the settings for each input field
    exp_name = settings.Setting("")
    quantities = settings.Setting("")
    device = settings.Setting("")
    data_collection_method = settings.Setting("")
    data_processing = settings.Setting("")
    calibration = settings.Setting("")
    conditions = settings.Setting("")
    people_involved = settings.Setting("")
    unit_system = settings.Setting("")
    
    particle_material = settings.Setting("")
    particle_diameter = settings.Setting("")
    particle_shape = settings.Setting("")
    particle_density = settings.Setting("")
    particle_media = settings.Setting("")
    particle_link = settings.Setting("")
    particle_preprocessing = settings.Setting("")
    
    file_location = settings.Setting("")
    num_variables_combo_value = settings.Setting("Multi")
    num_variables_spin_value = settings.Setting(2)
    date_collection = settings.Setting(QDate.currentDate())
    place_collection = settings.Setting("")
    license_info = settings.Setting("")
    
    # Input signal from User widget
    class Inputs:
        user_data = widget.Input("User Data", Table)
        
    class Outputs:
        user_data_table = widget.Output("User Data Table", Table)
        experiment_data_table = widget.Output("Experiment Data Table", Table)
        particle_data_table = widget.Output("Particle Data Table", Table)
        data_info_table = widget.Output("Data Info Table", Table)
        full_data = widget.Output("Full Data (JSON)", str)

    def __init__(self):
        super().__init__()

        # Attributes to hold the data
        self.user_info = {}
        self.auto_send = True


        # Control Area
        # User Info Box
        user_box = gui.widgetBox(self.controlArea, "User Info", orientation="vertical")
        self.info_label = gui.widgetLabel(user_box, "Please connect the user data from the User widget.")
        self.info_label.setStyleSheet('color: red')

        # Experiment Info Box
        exp_box = gui.widgetBox(self.controlArea, "Experiment Info", orientation="vertical")
        form_layout_exp = QFormLayout()
        self.create_exp_info_fields(form_layout_exp)
        exp_box.layout().addLayout(form_layout_exp)
        
        # Particle Info box
        particle_info_box = gui.widgetBox(self.controlArea, "Particle Info", orientation="vertical")
        # Initialize input fields with the saved settings
        self.particle_material_edit = QLineEdit(self.particle_material,self)
        self.particle_diameter_edit = QLineEdit(self.particle_diameter,self)
        self.particle_shape_edit = QLineEdit(self.particle_shape,self)
        self.particle_density_edit = QLineEdit(self.particle_density,self)
        self.particle_media_edit = QLineEdit(self.particle_media,self)
        self.particle_link_edit = QLineEdit(self.particle_link,self)
        self.particle_preprocessing_edit = QLineEdit(self.particle_preprocessing, self)
        
        particle_info_layout = QFormLayout()
        particle_info_layout.addRow("Particle's Material:", self.particle_material_edit)
        particle_info_layout.addRow("Particle's Diameter (m):", self.particle_diameter_edit)
        particle_info_layout.addRow("Particle's Shape:", self.particle_shape_edit)
        particle_info_layout.addRow("Particle's Density (kg/m3):", self.particle_density_edit)
        particle_info_layout.addRow("Media (air, water,...):", self.particle_media_edit)
        particle_info_layout.addRow("Link to MSDS or more details:", self.particle_link_edit)
        particle_info_layout.addRow("Material Preprocessing (if applied):", self.particle_preprocessing_edit)
        particle_info_box.layout().addLayout(particle_info_layout)
        
        # Connect signals for real-time updates
        self.particle_material_edit.textChanged.connect(self.update_preview)
        self.particle_diameter_edit.textChanged.connect(self.update_preview)
        self.particle_shape_edit.textChanged.connect(self.update_preview)
        self.particle_density_edit.textChanged.connect(self.update_preview)
        self.particle_media_edit.textChanged.connect(self.update_preview)
        self.particle_link_edit.textChanged.connect(self.update_preview)
        self.particle_preprocessing_edit.textChanged.connect(self.update_preview)
        
        # Data Info Box
        data_box = gui.widgetBox(self.controlArea, "Data Info", orientation="vertical")
        form_layout_data = QFormLayout()
        self.create_data_info_fields(form_layout_data)
        data_box.layout().addLayout(form_layout_data)

        # Main Area for preview
        self.preview_text = QTextEdit(self)
        self.preview_text.setReadOnly(True)  # Make the preview read-only
        self.mainArea.layout().addWidget(self.preview_text)
        
        # Add a validation button
        self.validation_button = gui.button(self.controlArea, self, "Validate and Send Data", callback=self.validate_and_send_data)
        
        # Connect signals for real-time updates
        
        self.update_preview()
        
    def validate_data(self):
    # Check if user data is received
        if not self.user_info:
            return "User data not received. Please connect the User widget."

        # Check experiment info fields
        for field, w in [("Name of the Experiment", self.exp_name_edit),
                              ("Measured Quantities", self.quantities_edit),
                              ("Measurement Device", self.device_edit)]:
            if not w.text().strip():
                return f"'{field}' is empty. Please provide the required information."

        # Check particle info fields
        for field, w in [("Particle's Material", self.particle_material_edit),
                              ("Particle's Diameter", self.particle_diameter_edit),
                              ("Particle's Shape", self.particle_shape_edit)]:
            if not w.text().strip():
                return f"'{field}' is empty. Please provide the required information."

        # Check data info fields
        for field, w in [("File location/Links", self.file_location_edit),
                              ("Place of data collection", self.place_collection_edit)]:
            if field == "Date of data collection":
                value = w.date().toString("yyyy-MM-dd")
            else:
                value = w.text().strip()
            if not value:
                return f"'{field}' is empty. Please provide the required information."
            
        # Check Particle's Diameter and Particle's Density are floating numbers
        for field, w in [("Particle's Diameter (m)", self.particle_diameter_edit),
                              ("Particle's Density", self.particle_density_edit)]:
            try:
                float(w.text())
            except ValueError:
                return f"'{field}' must be a floating number."

        # Check "Links to MSDS or more details" is a valid link, "None", or empty
        link = self.particle_link_edit.text().strip()
        if link and link.lower() != "none" and not re.match(r'https?://\S+', link):
            return "'Links to MSDS or more details' is not a valid link. You can also enter 'None' if there's no link."

        # Check "File location/link" is a valid location or link
        file_location = self.file_location_edit.text().strip()
        if file_location and not (re.match(r'https?://\S+', file_location) or os.path.exists(file_location)):
            return "'File location/Links' is not a valid location or link."

        return None  # No errors
    
    def validate_and_send_data(self):
        error_message = self.validate_data()
        if error_message:
            self.preview_text.setHtml(f"<span style='color: red;'>{error_message}</span>")
            # Clear the outputs
            self.Outputs.user_data_table.send(None)
            self.Outputs.experiment_data_table.send(None)
            self.Outputs.particle_data_table.send(None)
            self.Outputs.data_info_table.send(None)
            self.Outputs.full_data.send(None)
        else:
            self.preview_text.clear()  # Clear the error message
            self.update_preview()  # Refresh the preview
            
    def create_exp_info_fields(self, form_layout):
        # Initialize input fields with the saved settings
        self.exp_name_edit = QLineEdit(self.exp_name,self)
        self.quantities_edit = QLineEdit(self.quantities, self)
        self.device_edit = QLineEdit(self.device, self)
        self.data_collection_method_edit = QLineEdit(self.data_collection_method,self)
        self.data_processing_edit = QLineEdit(self.data_processing, self)
        self.calibration_edit = QLineEdit(self.calibration, self)
        self.conditions_edit = QLineEdit(self.conditions, self)
        self.people_involved_edit = QLineEdit(self.people_involved, self)
        self.unit_system_edit = QLineEdit(self.unit_system, self)

        form_layout.addRow("Name of the Experiment:", self.exp_name_edit)
        form_layout.addRow("Measured Quantities:", self.quantities_edit)
        form_layout.addRow("Measurement Device:", self.device_edit)
        form_layout.addRow("Methods/Software for Data Collection:", self.data_collection_method_edit)
        form_layout.addRow("Method for Processing Data:", self.data_processing_edit)
        form_layout.addRow("Standards and Calibration Information:", self.calibration_edit)
        form_layout.addRow("Environmental/Experimental Conditions:", self.conditions_edit)
        form_layout.addRow("People Involved:", self.people_involved_edit)
        form_layout.addRow("Unit System:", self.unit_system_edit)

        for w in [self.exp_name_edit, self.quantities_edit, self.device_edit, self.data_collection_method_edit, 
                        self.data_processing_edit, self.calibration_edit, self.conditions_edit,
                        self.people_involved_edit, self.unit_system_edit]:
            w.textChanged.connect(self.update_preview)

    def create_data_info_fields(self, form_layout):
        self.file_location_edit = QLineEdit(self.file_location,self)
        self.browse_button = gui.button(None, self, "Browse", callback=self.browse_file)
        self.num_variables_combo = QComboBox(self)
        comboList = ["Single", "Multi"]
        self.num_variables_combo.addItems(comboList)
        self.num_variables_combo.setCurrentIndex(comboList.index(self.num_variables_combo_value))
        self.num_variables_spin = QSpinBox(self, value =self.num_variables_spin_value )
        self.num_variables_spin.setMinimum(2)
        self.num_variables_spin.setMaximum(9999)
        self.num_variables_spin.setVisible(False)
        self.date_collection_edit = QDateEdit( self)
        self.date_collection_edit.setCalendarPopup(True)
        self.date_collection_edit.setDisplayFormat("yyyy-MM-dd")
        # Set default date to today
        self.date_collection_edit.setDate(QDate.fromString(self.date_collection, "yyyy-MM-dd"))
        # Set maximum date to today
        self.date_collection_edit.setMaximumDate(QDate.currentDate())
        self.date_collection_edit.dateChanged.connect(self.update_preview)  # Connect dateChanged signal
        self.place_collection_edit = QLineEdit(self.place_collection, self)
        self.license_edit = QLineEdit(self.license_info, self)

        form_layout.addRow("File location/Links:", self.file_location_edit)
        form_layout.addWidget(self.browse_button)
        form_layout.addRow("Number of variables:", self.num_variables_combo)
        form_layout.addRow("Specify number:", self.num_variables_spin)
        form_layout.addRow("Date of data collection:", self.date_collection_edit)
        form_layout.addRow("Place of data collection:", self.place_collection_edit)
        form_layout.addRow("Licenses/restrictions:", self.license_edit)

        self.num_variables_combo.currentTextChanged.connect(self.toggle_num_variables)
        
        for w in [self.file_location_edit, self.num_variables_combo, self.num_variables_spin, 
                        self.place_collection_edit, self.license_edit]:
            if isinstance(w, QComboBox):
                w.currentIndexChanged.connect(self.update_preview)
            else:
                w.textChanged.connect(self.update_preview)

    def toggle_num_variables(self):
        if self.num_variables_combo.currentText() == "Multi":
            self.num_variables_spin.setVisible(True)
        else:
            self.num_variables_spin.setVisible(False)
            self.num_variables_spin.setValue(1)
        self.update_preview()

    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File")
        if file_name:
            self.file_location_edit.setText(file_name)
            self.update_preview()
            
    @Inputs.user_data
    def set_input_data(self, data):
        if data:
            self.user_info = {var.name: str(data[0][var]) for var in data.domain.metas}
            self.info_label.setText("User data received!")
            self.info_label.setStyleSheet('color: green')
            self.update_preview()
        else:
            self.user_info = {}
            self.info_label.setText("Please connect the user data from the User widget.")
            self.info_label.setStyleSheet('color: red')
            self.update_preview()

    def update_preview(self):
        # Extract User Info
        user_info_text = format_dict_as_text(self.user_info, "User Info")

        # Extract Experiment Info
        experiment_info = {
            "Name of the Experiment": self.exp_name_edit.text(),
            "Measured Quantities": self.quantities_edit.text(),
            "Measurement Device": self.device_edit.text(),
            "Methods/Software for Data Collection": self.data_collection_method_edit.text(),
            "Method for Processing Data": self.data_processing_edit.text(),
            "Standards and Calibration Information": self.calibration_edit.text(),
            "Environmental/Experimental Conditions": self.conditions_edit.text(),
            "People Involved": self.people_involved_edit.text(),
            "Unit System": self.unit_system_edit.text()
        }
        experiment_info_text = format_dict_as_text(experiment_info, "Experiment Info")
        
        #update setting
        [self.exp_name, self.quantities, self.device, self.data_collection_method, 
         self.data_processing, self.calibration, self.conditions,self.people_involved,
         self.unit_system] = [w.text() for w in [self.exp_name_edit,
                                                 self.quantities_edit,
                                                 self.device_edit,
                                                 self.data_collection_method_edit,
                                                 self.data_processing_edit,
                                                 self.calibration_edit,
                                                 self.conditions_edit,
                                                 self.people_involved_edit,
                                                 self.unit_system_edit]]
        
        # Extract Particle Info
        particle_info = {
            "Particle's Material": self.particle_material_edit.text(),
            "Particle's Diameter (m)": self.particle_diameter_edit.text(),
            "Particle's Shape": self.particle_shape_edit.text(),
            "Particle's Density": self.particle_density_edit.text(),
            "Media": self.particle_media_edit.text(),
            "Link to MSDS or more details": self.particle_link_edit.text(),
            "Material preprocessing (if applied)": self.particle_preprocessing_edit.text()
        }
        particle_info_text = format_dict_as_text(particle_info, "Particle Info")
        
        #update setting
        [self.particle_material, 
        self.particle_diameter,
        self.particle_shape,
        self.particle_density,
        self.particle_media,
        self.particle_link,
        self.particle_preprocessing] = [w.text() for w in [self.particle_material_edit,
                                                           self.particle_diameter_edit,
                                                           self.particle_shape_edit,
                                                           self.particle_density_edit,
                                                           self.particle_media_edit,
                                                           self.particle_link_edit,
                                                           self.particle_preprocessing_edit]]
        
        # Extract Data Info
        num_vars_text = self.num_variables_combo.currentText()
        if num_vars_text == "Multi":
            num_vars_text + f" ({self.num_variables_spin.value()})"
        data_info = {
            "File location/Links": self.file_location_edit.text(),
            "Number of variables": num_vars_text,
            "Date of data collection": self.date_collection_edit.text(),
            "Place of data collection": self.place_collection_edit.text(),
            "Licenses/restrictions": self.license_edit.text()
        }
        data_info_text = format_dict_as_text(data_info, "Data Info")
        
        #update setting
        if self.num_variables_combo.currentText() == "Multi": self.num_variables_spin.setVisible(True)
        [self.file_location,
        self.num_variables_combo_value,
        self.num_variables_spin_value,
        self.date_collection ,
        self.place_collection ,
        self.license_info] = [self.file_location_edit.text(),
                              self.num_variables_combo.currentText(),
                              self.num_variables_spin.value(),
                              self.date_collection_edit.date().toString("yyyy-MM-dd"),
                              self.place_collection_edit.text(),
                              self.license_edit.text()]
    
        # Combine the texts for the preview
        combined_text = "<br/><br/>".join([user_info_text, experiment_info_text, particle_info_text, data_info_text])
        self.preview_text.setHtml(combined_text)
        
        # Emit the data as Orange data tables
        self.Outputs.user_data_table.send(dict_to_orange_table(self.user_info))
        self.Outputs.experiment_data_table.send(dict_to_orange_table(experiment_info))
        self.Outputs.particle_data_table.send(dict_to_orange_table(particle_info))
        self.Outputs.data_info_table.send(dict_to_orange_table(data_info))

        # Emit the full nested dictionary as JSON
        full_data = {
            "User Info": self.user_info,
            "Experiment Info": experiment_info,
            "Particle Info": particle_info,
            "Data Info": data_info
        }
        self.Outputs.full_data.send(json.dumps(full_data, indent=4))
