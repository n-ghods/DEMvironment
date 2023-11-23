# # -*- coding: utf-8 -*-
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
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QLineEdit, QVBoxLayout, QLabel, QPushButton, QRadioButton, QButtonGroup
from Orange.widgets import widget, gui, settings
from Orange.widgets.widget import Output
import os
import json
import shutil


class MetaDataRegistry(widget.OWWidget):
    name = "MetaData Registry"
    description = "Stores metadata JSON files in a warehouse directory."
    icon = "icons/MetaDataRegistry.png"
    priority = 6
    want_main_area = False

    class Inputs:
        directory_path = widget.Input("Directory Path", str)
        json_content = widget.Input("JSON Content", str)
    class Outputs:
        directory_path = Output("Metadata Warehouse Directory", str)
    
    # Settings
    metadata_warehouse_directory = settings.Setting("")
    selected_json_file = settings.Setting("")

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.received_directory_path = None
        self.received_json_content = None
    
        
    def setup_ui(self):
        # Metadata Warehouse Directory controls
        box = gui.widgetBox(self.controlArea, "Metadata Warehouse Directory")
        hbox = gui.hBox(box)  # Horizontal layout for inline elements
        self.metadata_dir_input = gui.lineEdit(hbox, self, "metadata_warehouse_directory")
        gui.button(hbox, self, "Browse", callback=self.browse_warehouse_directory)
        if self.metadata_warehouse_directory:
            self.send_directory_path()

        # Source Selection controls
        source_box = gui.widgetBox(self.controlArea, "Metadata Selection")
        
        self.radio_registry_from_dir = QRadioButton("Register from Directory Path")
        # Radio buttons for selecting the source
        self.radio_registry_from_dir.toggled.connect(self.on_source_selected_changed)
        source_box.layout().addWidget(self.radio_registry_from_dir)
        
        self.radio_registry_from_json = QRadioButton("Register from JSON Content")
        self.radio_registry_from_json.toggled.connect(self.on_source_selected_changed)
        source_box.layout().addWidget(self.radio_registry_from_json)
        
        self.radio_registry_browse_local = QRadioButton("Browse Local Directory")
        self.radio_registry_browse_local.toggled.connect(self.on_source_selected_changed)
        source_box.layout().addWidget(self.radio_registry_browse_local)

        self.json_file_input = gui.lineEdit(source_box, self, "selected_json_file", "JSON File Path:")
        self.browse_json_button = gui.button(source_box, self, "Browse to find JSON File", callback=self.browse_json_file)

        # Register Button
        self.register_button = gui.button(self.controlArea, self, "Register Metadata", callback=self.register_metadata)
        self.register_button.setEnabled(False)  # Initially disabled

        # Status labels
        self.status_label = gui.widgetLabel(self.controlArea, "")
        
        #initialize with the output directory if it is already filled
        self.send_directory_path()  
        
    def on_source_selected_changed(self):
        
        if self.radio_registry_from_dir.isChecked():
            self.handle_directory_path_source()
            self.json_file_input.setEnabled(True)
            self.browse_json_button.setEnabled(True)
        
        if self.radio_registry_browse_local.isChecked():
            self.json_file_input.clear()
            self.json_file_input.setEnabled(True)
            self.browse_json_button.setEnabled(True)
        
        if self.radio_registry_from_json.isChecked():
            self.handle_json_content_source()
            self.json_file_input.setEnabled(False)
            self.browse_json_button.setEnabled(False)

    def handle_directory_path_source(self):
        # Ensure that the correct input signal (directory path) is connected
        if not self.received_directory_path:
            QMessageBox.warning(self, "Warning", "No directory path received from the input signal.")
            self.radio_registry_from_dir.setChecked(False)  # Uncheck the radio button
            return
        else:
            self.json_file_input.setText(self.received_directory_path)
        
        
    def handle_json_content_source(self):
        # Ensure that the correct input signal (JSON content) is connected
        if not self.received_json_content:
            QMessageBox.warning(self, "Warning", "No JSON content received from the input signal.")
            self.radio_registry_from_json.setChecked(False)  # Uncheck the radio button
            return
        

    def browse_warehouse_directory(self):
        # Method to open a QFileDialog and select a directory
        dir_path = QFileDialog.getExistingDirectory(self, "Select Metadata Warehouse Directory", self.metadata_warehouse_directory)
        if dir_path:  # If a directory was selected
            self.metadata_warehouse_directory = dir_path
            self.metadata_dir_input.setText(dir_path)  # Update the line edit with the selected directory path
            self.send_directory_path()
    
    def send_directory_path(self):
        # Method to send the metadata warehouse directory path as an output signal
        self.Outputs.directory_path.send(self.metadata_warehouse_directory)
        
    def browse_json_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json);;All Files (*)")
        if file_name:
            self.selected_json_file = file_name
            self.json_file_input.setText(file_name)
            self.register_button.setEnabled(True)

    def register_metadata(self):
        if not self.metadata_warehouse_directory:
            QMessageBox.warning(self, "Warning", "Please choose the Metadata Warehouse Directory before registering.")
            return

        json_data = self.get_json_data()

        if not json_data:
            QMessageBox.warning(self, "Warning", "Metadata JSON file was not found!")
            return
        elif not self.is_valid_json_data(json_data):
            QMessageBox.warning(self, "warning", "Invalid JSON metadata.")
            return

        file_name = self.generate_file_name_from_json_data(json_data)
        file_path = os.path.join(self.metadata_warehouse_directory, file_name)

        if os.path.exists(file_path):
            self.handle_existing_file(file_path, json_data)
        else:
            self.save_json_data_to_file(json_data, file_path)
            QMessageBox.information(self, "Success", f"The metadata {file_name} was successfully registered.")

    
    
    def get_json_data(self):
        if self.radio_registry_from_dir.isChecked() or self.radio_registry_browse_local.isChecked():
            if self.selected_json_file and os.path.isfile(self.selected_json_file):
                with open(self.selected_json_file, 'r') as file:
                    return json.load(file)
        elif self.radio_registry_from_json.isChecked():
            return json.loads(self.received_json_content)
        return None

    def is_valid_json_data(self, json_data):
        return all(key in json_data.get("meta_info", {}) for key in ["version", "doi", "Archived time"])

    def handle_existing_file(self, existing_file_path, new_json_data):
        with open(existing_file_path, 'r') as file:
            existing_data = json.load(file)

        if new_json_data["meta_info"]["version"] > existing_data["meta_info"]["version"]:
            self.prompt_for_new_version_registration(existing_file_path, new_json_data)
        else:
            self.prompt_for_forced_overwrite(existing_file_path, new_json_data)

    def prompt_for_new_version_registration(self, existing_file_path, new_json_data):
        choice = QMessageBox.question(self, "New Version Found", 
                                      "A lower version of the metadata file exists. Would you like to register the new version?",
                                      QMessageBox.Yes | QMessageBox.No)

        if choice == QMessageBox.Yes:
            backup_file_path = existing_file_path + ".bak"
            if os.path.exists(backup_file_path):
                os.remove(backup_file_path)  # Remove existing backup if it exists
            os.rename(existing_file_path, backup_file_path)  # Rename existing file to backup
            self.save_json_data_to_file(new_json_data, existing_file_path)  # Save new version
            QMessageBox.information(self, "Success", "The new version of the metadata was successfully registered.")

    def prompt_for_forced_overwrite(self, existing_file_path, new_json_data):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Overwrite Warning")
        msg_box.setText("The same or higher version of the file exists in the metadata warehouse. Registry not recommended.")
        msg_box.setInformativeText("Do you want to overwrite it? (NOT recommended)")

        overwrite_button = msg_box.addButton("Overwrite", QMessageBox.AcceptRole)
        cancel_button = msg_box.addButton("Abort", QMessageBox.RejectRole)

        msg_box.exec_()

        if msg_box.clickedButton() == overwrite_button:
            # Overwrite the existing file
            self.save_json_data_to_file(new_json_data, existing_file_path)
            QMessageBox.information(self, "Success", "The file has been overwritten.")
        else:
            # Abort and do nothing
            QMessageBox.information(self, "Aborted", "File overwrite aborted.")


    def save_json_data_to_file(self, json_data, file_path):
        with open(file_path, 'w') as file:
            json.dump(json_data, file, indent=4)

    def generate_file_name_from_json_data(self, json_data):
        doi = json_data["meta_info"]["doi"]
        return f"{doi.split('-')[0]}-{doi.split('-')[1][:8]}.json"

    
    def show_message(self, message, error=False, success=False):
        # Generic method to show messages to the user
        if error:
            QMessageBox.critical(self, "Error", message)
        elif success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Warning", message)

    @Inputs.directory_path
    def set_input_directory_path(self, path):
        # Handle the input directory path signal
        if path:
            # self.selected_json_file = os.path.join(path, 'metadata.json')  # Assuming the file is named 'metadata.json'
            # self.json_file_input.setText(self.selected_json_file)
            self.received_directory_path = path
            self.radio_registry_from_dir.setChecked(True)
            self.register_button.setEnabled(True)


    @Inputs.json_content
    def set_input_json_content(self, content):
        # Handle the input JSON content signal
        if content:
            try:
                self.received_json_content = content
                self.radio_registry_from_json.setChecked(True)
                self.register_button.setEnabled(True)
            except json.JSONDecodeError:
                self.show_message("Invalid JSON format received.", error=True)