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
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QGroupBox, QPushButton,QRadioButton, QHBoxLayout, QComboBox
from PyQt5.QtCore import Qt
from Orange.widgets import widget, gui, settings
from Orange.widgets.widget import Msg
import os
import json
import glob
import uuid  # for generating unique DOI
from datetime import datetime

class OWDOIJson(widget.OWWidget):
    name = "DOI.json"
    description = "Assigns DOI and save the metadata file."
    icon = "icons/DOIJson.png"
    priority = 5
    want_main_area = False  
    
    
    # Input signals
    class Inputs:
        json_data = widget.Input("JSON Output", str)
        
    class Outputs:
        directory_path = widget.Output("Directory Path", str)
        json_content = widget.Output("JSON Content", str)  # New output signal for JSON content
    # Settings
    extracted_directory = settings.Setting("")
    input_json_data = None  # Store the input JSON data
    
    def __init__(self):
        super().__init__()
        
        self.meta_info = {}
        
        # Flag to distinguish between generate DOI and submit new version actions
        self.is_new_version = False

        
        # Create a QGroupBox in the main area
        self.info_box = QGroupBox("Connected Widget Info", self.controlArea)
        self.controlArea.layout().addWidget(self.info_box)
        
        # Radio buttons for selecting new version or new data
        self.radio_new_version = QRadioButton("New Version of Data", self.info_box)
        self.radio_new_data = QRadioButton("New Data", self.info_box)
        self.radio_new_version.toggled.connect(self.on_radio_changed)
        self.radio_new_data.toggled.connect(self.on_radio_changed)

        # ComboBox for selecting which JSON file to create a new version for
        self.json_file_combobox = QComboBox(self.info_box)
        self.json_file_combobox.hide()  # Initially hide the ComboBox
        # Label for the ComboBox
        self.json_file_combobox_label = QLabel("Please select the metadata file for which you want to submit a New Version", self.info_box)
        self.json_file_combobox_label.hide()  # Initially hide the label

        # Initially, both radio buttons are not visible
        self.radio_new_version.hide()
        self.radio_new_data.hide()
        
        # Create a label for warnings
        self.warning_label = QLabel("", self.info_box)
        self.warning_label.setStyleSheet("QLabel { color : red; }")
        self.warning_label.setAlignment(Qt.AlignCenter)
        self.warning_label.setWordWrap(True)
        self.warning_label.hide()  # Initially hide the warning label
        
        # Create a label for success messages
        self.success_label = QLabel("", self.info_box)
        self.success_label.setStyleSheet("QLabel { color : green; }")
        self.success_label.setAlignment(Qt.AlignCenter)
        self.success_label.setWordWrap(True)
        self.success_label.hide()  # Initially hide the success label
        
        # Create labels to display the connected widget, the presence of .json files, and the directory path
        self.connected_widget_label = QLabel("Connected Widget: None", self.info_box)
        self.json_files_label = QLabel("Contains .json files: No", self.info_box)
        self.directory_path_label = QLabel("Directory Path: None", self.info_box)  # New label for directory path
        self.doi_label = QLabel("DOI: None", self.info_box)
        
        # Button to generate DOI
        self.generate_doi_button = QPushButton("Assign DOI and Create the Metadata File", self.info_box)
        self.generate_doi_button.setText("Assign DOI and Create the Metadata File")
        self.generate_doi_button.clicked.connect(self.generate_doi)
        # Initially disable the "Generate DOI" button
        self.generate_doi_button.setEnabled(False)
        
        # Layout for the QGroupBox
        layout = QVBoxLayout()
        layout.addWidget(self.connected_widget_label)
        layout.addWidget(self.directory_path_label)  # Add the new label to the layout
        layout.addWidget(self.json_files_label)
        
        # Add the warning label to the layout
        layout.addWidget(self.warning_label)
        
        # Add radio buttons to the layout
        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.radio_new_version)
        radio_layout.addWidget(self.radio_new_data)
        
        layout.addLayout(radio_layout)

        layout.addWidget(self.generate_doi_button)
        self.info_box.setLayout(layout)
        # Add ComboBox to the layout
        # Add the label and ComboBox to the layout
        layout.addWidget(self.json_file_combobox_label)
        layout.addWidget(self.json_file_combobox)
        # Add a "Submit New Version" button
        self.submit_new_version_button = QPushButton("Submit New Version", self.info_box)
        self.submit_new_version_button.hide()  # Initially hide the button
        self.submit_new_version_button.clicked.connect(self.submit_new_version)
        
        layout.addWidget(self.submit_new_version_button)
        # Add the success label to the layout
        layout.addWidget(self.success_label)
        layout.addWidget(self.doi_label)
        
        #---------------------------------------
        # Create a new QGroupBox for output controls
        self.output_box = QGroupBox("Output", self.controlArea)
        self.controlArea.layout().addWidget(self.output_box)
        
        # Create a button for submitting to the metadata registry
        self.submit_to_registry_button = QPushButton("Submit to Metadata Registry", self.output_box)
        self.submit_to_registry_button.clicked.connect(self.submit_to_registry)
        
        # Initially disable the button until there is content to send
        self.submit_to_registry_button.setEnabled(False)
        
        # Layout for the output QGroupBox
        output_layout = QVBoxLayout()
        output_layout.addWidget(self.submit_to_registry_button)
        self.output_box.setLayout(output_layout)
       

    def generate_doi(self):
        widget_indicator = self.get_widget_indicator()
        # Get the current date and time
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if not self.is_new_version:
            # Reset the version to 0 for a new DOI
            self.meta_info["version"] = 0
            
            # Generate a custom DOI
            unique_doi = str(uuid.uuid4())  # Generate a unique UUID
            custom_doi = f"{widget_indicator}-{unique_doi[:8]}"  # Using the first 8 characters of the UUID
            
        else:
            # Keep the old UUID and increment the version
            unique_doi = self.meta_info["doi"].replace(f"{self.widget_indicator}-", "", 1)
            custom_doi = f"{widget_indicator}-{unique_doi[:8]}"  # Using the first 8 characters of the UUID
        # Show the DOI label after generating the DOI
        self.doi_label.setText(f"DOI: {custom_doi}")
        self.doi_label.show()
        
        # Create or update the meta-information dictionary
        self.meta_info.update({
            "Archived time": current_datetime,
            "doi": f"{widget_indicator}-{unique_doi}",
            "version": self.meta_info.get("version", 0)  # Default to 0 if version is not set
            })
    

        # Append the meta-information dictionary to the beginning of the input JSON data
        combined_data = {"meta_info": self.meta_info, **self.input_json_data}

        # Save the combined data to a .json file in the directory path
        if combined_data:
            file_path = os.path.join(self.extracted_directory, f"{widget_indicator}-{unique_doi[:8]}.json")
            with open(file_path, 'w') as json_file:
                json.dump(combined_data, json_file, indent=4) 
                
                # Store the combined data in an instance variable for later use
                self.combined_data_json = json.dumps(combined_data, indent=4)
    
                # Enable the "Submit to Metadata Registry" button
                self.submit_to_registry_button.setEnabled(True)

            # Refresh the directory information after creating the .json file
            self.refresh_directory_info()
            
      
        # After generating the DOI, reset the flag
        self.is_new_version = False
        # Enable the button after generating the DOI or submitting a new version
        self.submit_to_registry_button.setEnabled(True)
        
    def on_radio_changed(self):
        # Enable the appropriate button based on the radio button selection
        if self.radio_new_version.isChecked():
            self.submit_new_version_button.setEnabled(True)
            self.generate_doi_button.setEnabled(False)
            # Show the ComboBox and its label
            self.json_file_combobox_label.show()
            self.json_file_combobox.show()  # Show the ComboBox when 'New Version of Data' is selected
        elif self.radio_new_data.isChecked():
            self.submit_new_version_button.setEnabled(False)
            self.generate_doi_button.setEnabled(True)
            # Hide the ComboBox and its label
            self.json_file_combobox_label.hide()
            self.json_file_combobox.hide()  # Hide the ComboB
            
    def refresh_directory_info(self):
        json_files = self.check_existing_json_files()

        if json_files:
            self.json_files_label.setText("Contains .json files: Yes")
            # Show the radio buttons
            self.radio_new_version.show()
            self.radio_new_data.show()
            # Populate the ComboBox with the JSON files
            self.json_file_combobox.clear()
            for file in json_files:
                self.json_file_combobox.addItem(file)
            # Disable both buttons until a choice is made
            self.generate_doi_button.setEnabled(False)
            self.submit_new_version_button.setEnabled(False)
            
            self.submit_new_version_button.show()  # Show the "Submit New Version" button
            self.warning_label.setText("A metadata file is present in this directory.\n"
                                       "If it is not related to the data in the directory, please remove it and try again.\n"
                                       "If you want so submit metadata for another data in the directory, please select 'New Data'.\n"
                                       "If you want to add a new version, select 'New Version of Data'.")
            self.warning_label.setAlignment(Qt.AlignLeft)
            self.warning_label.show()  # Display the warning message
        else:
            self.json_files_label.setText("Contains .json files: No")
            # Hide the radio buttons
            self.radio_new_version.hide()
            self.radio_new_data.hide()

            self.submit_new_version_button.hide()
            self.generate_doi_button.setEnabled(True)  # Enable the "Generate DOI" button
            self.warning_label.hide()  # Hide the warning message
    
    def get_widget_indicator(self):
        # Helper function to get the widget indicator based on the connected widget label
        if "Connected Widget: Experiment" in self.connected_widget_label.text():
            return "exp"
        elif "Connected Widget: Relational" in self.connected_widget_label.text():
            return "rel"
        elif "Connected Widget: Read Aspherix" in self.connected_widget_label.text():
            return "calib"
        else:
            return ""
    
    def extract_directory(self, data_str):
        data_dict = json.loads(data_str)
        widget_indicator = ""
        
        # Check the source widget and extract the directory accordingly
        if "Data Info" in data_dict:
            file_path = data_dict["Data Info"].get("File location/Links", "")
            directory = os.path.dirname(file_path)
            widget_indicator = "exp"
            self.connected_widget_label.setText("Connected Widget: Experiment")
        elif "Correlation Info" in data_dict:
            file_path = data_dict["Correlation Info"].get("Python file path", "")
            directory = os.path.dirname(file_path)
            widget_indicator = "rel"
            self.connected_widget_label.setText("Connected Widget: Relational")
        elif "Calibration Case" in data_dict:
            directory = data_dict["Calibration Case"].get("Local Directory", "")
            widget_indicator = "calib"
            self.connected_widget_label.setText("Connected Widget: Read Aspherix")
        else:
            directory = ""
            self.connected_widget_label.setText("Connected Widget: None")
        
        self.extracted_directory = directory
        self.widget_indicator = widget_indicator  # Set as an instance variable
        

        return self.extracted_directory
    
    def submit_new_version(self):
        self.is_new_version = True
        
        self.is_new_version = True
        selected_file = self.json_file_combobox.currentText()  # Get the selected file from the ComboBox
        existing_file_path = os.path.join(self.extracted_directory, selected_file)
        
        if os.path.isfile(existing_file_path):
            with open(existing_file_path, 'r') as file:
                data = json.load(file)
                old_version = data["meta_info"]["version"]
                old_uuid = data["meta_info"]["doi"].replace(f"{self.widget_indicator}-", "", 1)  # Extract the old UUID
            
            # Rename the existing file to backup with the old version number
            backup_file_path = existing_file_path + f".v{old_version}.bak"
            os.rename(existing_file_path, backup_file_path)
                
            # Update the version in meta_info without changing the UUID
            new_version = old_version + 1
            self.meta_info["version"] = new_version
            self.meta_info["doi"] = f"{self.widget_indicator}-{old_uuid}"  # Keep the old UUID
            
            # Refresh directory info and save the new version
            self.refresh_directory_info()
            self.generate_doi()

            # Display the success message
            self.success_label.setText(f"The metadata for the new version (v{new_version}) has been created and saved.")
            self.success_label.show()  # Show the success message

    def check_existing_json_files(self):
        """Check for existing JSON files and return their paths."""
        json_file_pattern = os.path.join(self.extracted_directory, f"{self.widget_indicator}-*.json")
        json_files = glob.glob(json_file_pattern)
        return json_files if json_files else []

    @Inputs.json_data
    def set_input_data(self, data):
       if data:
           self.input_json_data = json.loads(data)
           
           # Extract the directory from the input data
           self.extract_directory(data)
           self.refresh_directory_info()
           # Send the directory as an output signal
           self.Outputs.directory_path.send(self.extracted_directory)
           self.directory_path_label.setText(f"Directory Path: {self.extracted_directory}")
           
           # Reset the warning and success messages when new data is connected
           #self.warning_label.hide()
           self.success_label.hide()
       else:
            self.Outputs.directory_path.send(None)
            self.connected_widget_label.setText("Connected Widget: None")
            self.json_files_label.setText("Contains .json files: No")
            self.doi_label.setText("DOI: None")
            self.warning_label.hide()
            self.success_label.hide()
            # No data is connected, hide the ComboBox and its label, and reset labels
            self.json_file_combobox_label.hide()
            self.json_file_combobox.hide()
            # Hide the radio buttons if they exist
            if hasattr(self, 'radio_new_version'):
                self.radio_new_version.hide()
            if hasattr(self, 'radio_new_data'):
                self.radio_new_data.hide()
    
    def submit_to_registry(self):
        # This method will be called when the "Submit to Metadata Registry" button is clicked
        if hasattr(self, 'combined_data_json'):
            # Send the JSON content as an output signal
            self.Outputs.json_content.send(self.combined_data_json)

            # Display a success message or log the event
            self.success_label.setText("Metadata submitted to registry successfully.")
            self.success_label.show()
        else:
            # Handle the case where there is no data to submit
            self.warning_label.setText("No metadata to submit. Please generate DOI first.")
            self.warning_label.show()