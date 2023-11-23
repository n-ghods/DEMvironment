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
import os
from PyQt5.QtWidgets import QMessageBox, QTreeWidgetItem, QTreeWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QLineEdit, QHBoxLayout, QComboBox, QDoubleSpinBox, QTextEdit
from PyQt5.QtWidgets import QSizePolicy
from Orange.widgets import widget, gui, settings
from Orange.data import Table, Domain, StringVariable
from shared.dictHandler import dict_to_orange_table
import re
import json

class OWReadAspherix(widget.OWWidget):
    name = "Read Aspherix"
    description = "Load data from Aspherix."
    icon = "icons/ReadAspherix.png"
    priority = 4
    want_main_area = True
    
    selected_directory = settings.Setting("")
    # Add settings for Calibration Case
    Case_Name = settings.Setting("")
    Cohesivity = settings.Setting(0)
    Target_Flow_State = settings.Setting(0)
    Consolidation_level = settings.Setting(0)
    Consolidation_Pressure = settings.Setting(0.0)
    templates_dict = {}
    templates_meta_info = {}  # Dictionary to store meta_info for each template
    extracted_data = []
    # Input signals
    class Inputs:
        user_data = widget.Input("User Data", Table)
        
    class Outputs:
        aspherix_info = widget.Output("Aspherix Data", Table)
        templates_info = widget.Output("Templates and Target Calibration Parameters", Table)
        models_info = widget.Output("Models Info", Table)
        input_parameters = widget.Output("Input Parameters", Table)
        psd = widget.Output("PSD", Table)
        calibrated_parameter_properties = widget.Output("Calibrated Parameter Properties", Table)
        convergence = widget.Output("Convergence", Table)
        calibrated_parameters = widget.Output("Calibrated Parameters", Table)
        user_data = widget.Output("User Data", Table)
        calibration_case = widget.Output("Calibration Case", Table)
        template_meta_info = widget.Output("Template Meta Info", Table)
        json_output = widget.Output("JSON Output", str)

    def __init__(self):
        super().__init__()
        
        self.user_info = {}
    
        # Control Area
        # Set the size policy for the control area to resize properly
        self.controlArea.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        # User Info Box
        user_box = gui.widgetBox(self.controlArea, "User Info", orientation="vertical")
        self.info_label = gui.widgetLabel(user_box, "Please connect the user data from the User widget.")
        self.info_label.setStyleSheet('color: red')
        
        # Calibration Case Box
        calibration_case_box = gui.widgetBox(self.controlArea, "Calibration Case", orientation="vertical")
        gui.lineEdit(calibration_case_box, self, "Case_Name", label="Case Name:")
        gui.comboBox(calibration_case_box, self, "Cohesivity", label="Cohesivity:", items=["cohesionless", "cohesive"])
        gui.comboBox(calibration_case_box, self, "Target_Flow_State", label="Target Flow State:", items=["Quasi-static", "Intermediate", "Rapid"])
        gui.comboBox(calibration_case_box, self, "Consolidation_level", label="Consolidation level:", items=["low", "high"])
        self.consolidation_pressure_spinbox = QDoubleSpinBox(self, value =self.Consolidation_Pressure)
        self.consolidation_pressure_spinbox.setRange(0, 1e9)
        self.consolidation_pressure_spinbox.setSuffix(" Pa")
        self.consolidation_pressure_spinbox.setValue(self.Consolidation_Pressure)
        self.consolidation_pressure_spinbox.valueChanged.connect(self.update_consolidation_pressure)
        calibration_case_box.layout().addWidget(QLabel("Consolidation Pressure:"))
        calibration_case_box.layout().addWidget(self.consolidation_pressure_spinbox)

        # Simulation Details Box
        simulation_details_box = gui.widgetBox(self.controlArea, "Simulation Details", orientation="vertical")
        
        
        # Directory input layout
        dir_layout = QHBoxLayout()
        self.directory_input = QLineEdit(self)
        self.directory_input.setText(self.selected_directory)
        self.directory_input.editingFinished.connect(self.check_files)
        self.directory_input.textChanged.connect(self.check_files)
        dir_layout.addWidget(self.directory_input)
        
        self.load_directory_btn = QPushButton("Browse", self)
        self.load_directory_btn.clicked.connect(self.load_directory)
        dir_layout.addWidget(self.load_directory_btn)
        
        simulation_details_box.layout().addLayout(dir_layout)
        
        # File check labels
        self.log_file_label = gui.widgetLabel(simulation_details_box, "")
        self.params_file_label = gui.widgetLabel(simulation_details_box, "")
        
        # Add a button to extract data
        self.extract_data_btn = QPushButton("Extract Data", self)
        self.extract_data_btn.clicked.connect(self.extract_data)
        simulation_details_box.layout().addWidget(self.extract_data_btn)
        
        # Calibration Reference (Exp./Rel) Metadata Box
        self.calibration_reference_box = gui.widgetBox(self.controlArea, "Calibration Reference (Exp./Rel) Metadata", orientation="vertical")
        self.calibration_reference_entries = {}

        
        # Add a button to transmit data
        self.validate_and_send_data_btn = QPushButton("Validate and Send Data", self)
        self.validate_and_send_data_btn.clicked.connect(self.transmit_data)
        self.validate_and_send_data_btn.setEnabled(False)  # Initially disable the button
        self.controlArea.layout().addWidget(self.validate_and_send_data_btn)
        # self.transmit_data_btn = QPushButton("Validate and Send Data", self)
        # self.transmit_data_btn.clicked.connect(self.transmit_data)
        # self.controlArea.layout().addWidget(self.transmit_data_btn)
        
        # Main Area
        self.data_tree = QTreeWidget(self.mainArea)
        self.data_tree.setHeaderLabels(["Key", "Value"])
        self.mainArea.layout().addWidget(self.data_tree)
        self.adjustSize()

    def update_consolidation_pressure(self, value):
        self.Consolidation_Pressure = value
        
    def load_directory(self):
        """Load a directory and update the control area."""
        directory_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory_path:
            self.selected_directory = directory_path
            self.directory_input.setText(directory_path)
            self.check_files()
            
            # Reset and repopulate the control area
            self.reset_control_area()
            self.repopulate_control_area_based_on_directory(directory_path)
            
    def check_files(self):
        """Check for the presence of specified files in the directory."""
        directory = self.directory_input.text().strip()
        
        if not directory:
            return
        
        # Check for log_aspherix-calibration.txt
        if os.path.exists(os.path.join(directory, "log_aspherix-calibration.txt")):
            self.log_file_label.setText("The Log File was found.")
            self.log_file_label.setStyleSheet('color: green')
        else:
            self.log_file_label.setText("The Log File was not found.")
            self.log_file_label.setStyleSheet('color: red')
        
        # Check for calibrated_params.txt
        if os.path.exists(os.path.join(directory, "calibrated_params.txt")):
            self.params_file_label.setText("The calibrated_params.txt file was found.")
            self.params_file_label.setStyleSheet('color: green')
        else:
            self.params_file_label.setText("The calibrated_params.txt file was not found.")
            self.params_file_label.setStyleSheet('color: red')

    @Inputs.user_data
    def set_input_data(self, data):
        if data:
            self.user_info = {var.name: str(data[0][var]) for var in data.domain.metas}
            self.info_label.setText("User data received!")
            self.info_label.setStyleSheet('color: green')
        else:
            self.user_info = {}
            self.info_label.setText("Please connect the user data from the User widget.")
            self.info_label.setStyleSheet('color: red')
    
    def extract_calibration_data(self, logfile_path):
        self.extracted_data = []
        # Define regular expressions to extract relevant lines
        variable_pattern = re.compile(r'variable (\w+) string ([\d.e+-]+)')
        param_calibration_pattern = re.compile(r'param_calibration (\w+) type (\w+) init ([\d.e+-]+) min ([\d.e+-]+) max ([\d.e+-]+)')

        # Initialize dictionaries to store extracted data
        Aspherix_calibration_software_info = {
            "version": "",
            "git commit": "",
            "attempting to": "",
            "run mode": ""
        }
        calibration_templates = {}
        models = {
            "normal_contact_model": "",
            "tangential_contact_model": "",
            "cohesion_model": "",
            "rolling_friction_model": "",
            "surface_model": "",
            "coarsegraining_val": 0
        }
        input_parameters = {}
        PSD = {
            "radii_list": [],
            "mass_fractions_list": [],
            "dispersity": 0
        }
        calibrated_parameters_property = {}

        # Function to parse values with scientific notation
        def parse_value(value_str):
            try:
                return int(value_str)
            except ValueError:
                try:
                    return float(value_str)
                except ValueError:
                    return value_str

        # Open and read the log file in reverse order
        with open(logfile_path, 'r') as log_file:
            lines = log_file.readlines()

            # Check the final line for "ERROR" or anything other than "calibration ended successfully"
            final_line = lines[-1].strip()
            if ("ERROR" in final_line) or ("calibration ended successfully" not in final_line):
                converged = "No"
            else:
                converged = "Yes"

            for line in reversed(lines):
                # Extract values for models using re
                run_mode_match = re.search(r'run mode (single|sequential)', line)
                if run_mode_match:
                    run_mode = run_mode_match.group(1)
                    Aspherix_calibration_software_info["run mode"] = run_mode
                    continue
                
                if 'calibration_case' in line:
                    # Extract the template name
                    template_match = re.search(r'template (\w+)', line)
                    if template_match:
                        template_name = template_match.group(1)
                        # Initialize the list of target parameters for this template
                        if template_name not in calibration_templates:
                            calibration_templates[template_name] = []
    
                        # Find the section of the line between 'target_param' and 'measfile'
                        target_params_section = re.search(r'target_param(.*?)measfile', line)
                        if target_params_section:
                            # Extract all words in the section
                            target_params = re.findall(r'(\w+)', target_params_section.group(1))
                            # Add the target parameters to the template entry
                            calibration_templates[template_name].extend(target_params)
                
                
                model_match = re.search(r'variable (\w+) string (\S+)', line)
                if model_match:
                    name, value = model_match.groups()
                    if name == "coarsegraining_val":
                        models[name] = parse_value(value)
                    elif name in models:
                        models[name] = value
                        continue

                variable_match = variable_pattern.search(line)
                if variable_match:
                    name, value = variable_match.groups()
                    if name.startswith("rp"):
                        PSD["radii_list"].append(parse_value(value))
                    elif name.startswith("mf"):
                        PSD["mass_fractions_list"].append(parse_value(value))
                    PSD["dispersity"] = len(PSD["radii_list"])
                    input_parameters[name] = parse_value(value)
                    continue

                param_calibration_match = param_calibration_pattern.search(line)
                if param_calibration_match:
                    name, param_type, param_init, param_min, param_max = param_calibration_match.groups()

                    # Create a dictionary to store parameter details
                    param_details = {
                        'type': param_type,
                        'init': parse_value(param_init),
                        'min': parse_value(param_min),
                        'max': parse_value(param_max)
                    }

                    # Add the parameter details to the calibrated_parameters dictionary
                    calibrated_parameters_property[name] = param_details
                    continue

                attempting_match = re.search(r'attempting to (run|restart) ', line)
                if attempting_match:
                    latest_attempting_to = attempting_match.group(1)
                    Aspherix_calibration_software_info["attempting to"] = latest_attempting_to

                git_commit_match = re.search(r'git commit (.+)', line)
                if git_commit_match:
                    latest_git_commit = git_commit_match.group(1)
                    Aspherix_calibration_software_info["git commit"] = latest_git_commit

                version_match = re.search(r'This is Aspherix\(R\)calibration version (.+)', line)
                if version_match:
                    latest_version = version_match.group(1)
                    Aspherix_calibration_software_info["version"] = latest_version

            desired_parameters = {
                "density_p", "young_w", "young_p", "poisson_p", "poisson_w",
                "rest_coef_pw", "rest_coef_pp", "fric_coef_pp", "fric_coef_pw",
                "roll_fric_pp", "roll_fric_pw"
            }
            if models["normal_contact_model"] == "hooke":
                desired_parameters.add("char_vel")

            if models["rolling_friction_model"] == "epsd":
                desired_parameters.update({
                    "roll_damp_pw", "roll_damp_pp"
                })

            if models["cohesion_model"] in {"sjkr", "sjkr2"}:
                desired_parameters.update({
                    "cohesion_energy_pp", "cohesion_energy_pw"
                })

            if models["cohesion_model"] == "adaptive":
                desired_parameters.update({
                    "init_coh_stress_pw", "init_coh_stress_pp",
                    "max_coh_stress_pp_0", "max_coh_stress_pp_min", "max_coh_stress_pp_max",
                    "coh_strength_pp_0", "coh_strength_pp_min", "coh_strength_pp_max"
                })

            # Create a new dictionary with only the desired parameters
            filtered_input_parameters = {
                key: value for key, value in input_parameters.items() if key in desired_parameters
            }

            # Update the input_parameters dictionary
            input_parameters = filtered_input_parameters
            
        convergence = {"isconverged": converged}
        
        self.templates_dict = calibration_templates
        # After extracting data, populate the reference fields
        self.populate_calibration_reference_fields(self.templates_dict)
        self.validate_and_send_data_btn.setEnabled(True)
        self.extracted_data = [Aspherix_calibration_software_info,calibration_templates, models, input_parameters, PSD, calibrated_parameters_property, convergence]
        return 
    
            
    def read_calibrated_params(self,file_path):
        calibrated_parameters = {}
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines[1:]:  # Skip the header line
                parts = line.strip().split()
                if len(parts) >= 2:
                    param_name = parts[0]
                    param_value = float(parts[1])
                    calibrated_parameters[param_name] = param_value
        return calibrated_parameters
    
    def extract_data(self):
        """Extract data from the user info, log and calibrated_params files."""
        log_file_path = os.path.join(self.selected_directory, "log_aspherix-calibration.txt")
        calibrated_params_path = os.path.join(self.selected_directory, "calibrated_params.txt")
        dict_names =["User Info","Calibration Case","Aspherix_Info", "Templates and Target Calibrated Parameters","Models_info", "Input_parameters", "PSD", "Calibrated_parameter_properties", "Convergence","Calibrated_parameters"]
        
        data_list = []
    
        
        # Include the user data
        if self.user_info:
            data_list.append(self.user_info)
        else:
            # Validation: Ensure user data is connected
            self.warning("Please first connect the user data from the User widget.")
            return
        # Clear previous warnings
        self.warning()
        
        # Check if the Case Name is empty
        if not self.Case_Name.strip():
            self.warning("Case Name cannot be empty.")
            return
        # Clear previous warnings
        self.warning()
        # Include the Calibration Case data
        calibration_case_data = {
            "Case Name": self.Case_Name,
            "Cohesivity": ["cohesionless", "cohesive"][self.Cohesivity],
            "Target Flow State": ["Quasi-static", "Intermediate", "Rapid"][self.Target_Flow_State],
            "Consolidation level": ["low", "high"][self.Consolidation_level],
            "Consolidation Pressure": self.consolidation_pressure_spinbox.value(),
            "Local Directory": self.selected_directory
        }
        data_list.append(calibration_case_data)
        
        if os.path.exists(log_file_path):
            self.extract_calibration_data(log_file_path)
            data_list.extend(self.extracted_data)
        else:
            self.warning("The log_aspherix-calibration.txt file was not found in the selected directory.")
            return
        # Clear previous warnings
        self.warning()
        
        if os.path.exists(calibrated_params_path):
            calibrated_params_data = self.read_calibrated_params(calibrated_params_path)
            data_list.append(calibrated_params_data)
        else:
            self.warning("The calibrated_params.txt file was not found in the selected directory.")
            return

        
        # Display the extracted data in the QTreeWidget
        self.data_tree.clear()
        for idx, data_dict in enumerate(data_list):
            top_item = QTreeWidgetItem(self.data_tree)
            top_item.setText(0, dict_names[idx])
            for key, value in data_dict.items():
                child_item = QTreeWidgetItem(top_item)
                child_item.setText(0, key)
                child_item.setText(1, str(value))
            self.data_tree.addTopLevelItem(top_item)
        
        # Update the main area display
        self.update_main_area()
        #self.validate_and_send_data_btn.setEnabled(True)
        
    def validate_data(self):
        """Check the required data before transmitting."""
        errors = []

        # Validate user info data
        if not self.user_info:
            errors.append("User data is required.")
        else:
            # Assuming user_info is a dictionary with expected keys
            required_user_info_keys = ['First Name', 'Last Name', 'Email', 'Affiliation']
            missing_keys = [key for key in required_user_info_keys if not self.user_info.get(key)]
            if missing_keys:
                missing_fields = ", ".join(missing_keys)
                errors.append(f"Missing user information for the following fields: {missing_fields}")

        # Validate the Case Name
        if not self.Case_Name.strip():
            errors.append("Case Name cannot be empty.")

        # Validate directory and files
        if not os.path.isdir(self.selected_directory):
            errors.append(f"The selected directory '{self.selected_directory}' does not exist.")
        else:
            # Check for log file
            log_file_path = os.path.join(self.selected_directory, "log_aspherix-calibration.txt")
            if not os.path.isfile(log_file_path):
                errors.append("The log_aspherix-calibration.txt file was not found in the selected directory.")

        # Check for calibrated parameters file
        calibrated_params_path = os.path.join(self.selected_directory, "calibrated_params.txt")
        if not os.path.isfile(calibrated_params_path):
            errors.append("The calibrated_params.txt file was not found in the selected directory.")
        # Check if JSON file path fields are filled correctly
        for key, (label, line_edit, button) in self.calibration_reference_entries.items():
            if not line_edit.text() or not os.path.isfile(line_edit.text()):
                errors.append(f"The JSON file path for '{key}' is not filled correctly.")
                
        return errors
    
    def populate_calibration_reference_fields(self, templates_dict):
        # Clear any existing fields
        for w in self.calibration_reference_entries.values():
            self.calibration_reference_box.layout().removeWidget(w)
            w.deleteLater()
        self.calibration_reference_entries.clear()

        # Create new fields for each key in templates_dict
        for key in templates_dict:
            hbox = QHBoxLayout()
            label = QLabel(f"{key}:")
            line_edit = QLineEdit()
            load_button = QPushButton("Load JSON")
            load_button.clicked.connect(lambda checked, key=key, line_edit=line_edit: self.load_json_for_key(key, line_edit))

            hbox.addWidget(label)
            hbox.addWidget(line_edit)
            hbox.addWidget(load_button)

            self.calibration_reference_box.layout().addLayout(hbox)
            self.calibration_reference_entries[key] = (label, line_edit, load_button)
    
    def on_template_info_changed(self):
        # This method should be called whenever template_info is updated outside of extract_data
        self.populate_calibration_reference_fields(self.templates_dict)
    
    def load_json_for_key(self, key, line_edit):
        # Open a file dialog to select a JSON file
        file_path, _ = QFileDialog.getOpenFileName(self, f"Select JSON File for {key}", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    
                    # Validate the JSON structure
                    if not self.validate_json_structure(data):
                        QMessageBox.warning(self, "Invalid JSON Format", 
                                            "The selected JSON does not have the required format or missing 'meta_info'.")
                        return

                    # Extract and store the meta_info
                    self.templates_meta_info[key] = data.get('meta_info', {})
                    
                    line_edit.setText(file_path)  # Update the QLineEdit with the file path
                    # If the JSON file is valid, update the QTreeWidget
                    self.update_templates_meta_info_view()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while reading the file: {e}")
    
    def reset_control_area(self):
        """Reset the dynamic part of the control area."""
        # Clear existing metadata entries in the control area
        # Assuming you have a method or a way to clear the entries, such as:
        self.clear_calibration_reference_fields()
    
    def repopulate_control_area_based_on_directory(self, directory_path):
        """Repopulate control area based on the new directory."""
        # Clear any existing data related to metadata JSON files
        self.templates_meta_info.clear()

        # Scan the directory and populate the templates_meta_info dictionary
        self.populate_templates_meta_info_from_directory(directory_path)

        # Update the UI elements that show the metadata files
        self.populate_calibration_reference_fields(self.templates_meta_info)
        
    def update_templates_meta_info_view(self):
        # Find or create the top-level item for templates_meta_info
        found = False
        for i in range(self.data_tree.topLevelItemCount()):
            top_item = self.data_tree.topLevelItem(i)
            if top_item.text(0) == "Templates Meta Info":
                found = True
                break
        if not found:
            top_item = QTreeWidgetItem(self.data_tree, ["Templates Meta Info"])
        
        # Clear the previous entries
        top_item.takeChildren()

        # Add sub-items for each template's meta_info
        for template, meta_info in self.templates_meta_info.items():
            template_item = QTreeWidgetItem(top_item, [template])
            for key, value in meta_info.items():
                QTreeWidgetItem(template_item, [key, str(value)])
        
        # Expand the tree to show the new data
        top_item.setExpanded(True)
    def clear_calibration_reference_fields(self):
        """Clear the calibration reference fields in the control area."""
        # This should remove all child widgets from the calibration reference box
        # For example:
        for label, line_edit, button in self.calibration_reference_entries.values():
            label.deleteLater()
            line_edit.deleteLater()
            button.deleteLater()
        self.calibration_reference_entries.clear()
        
    def validate_json_structure(self, data):
        """Validate the JSON structure for the required keys in meta_info."""
        if "meta_info" not in data:
            return False
        required_keys = {"version", "doi", "Archived time"}
        return all(key in data["meta_info"] for key in required_keys)
    
    def transmit_data(self):
        # Validate the data first
        errors = self.validate_data()
        if errors:
            error_message = "\n".join(errors)
            QMessageBox.critical(self, "Validation Error", f"Cannot transmit data due to the following errors:\n{error_message}")
            return
        
        calibrated_params_path = os.path.join(self.selected_directory, "calibrated_params.txt")
        data_list = []
        data_list.extend([
                    ("Aspherix Info", self.extracted_data[0]),
                    ("Templates Info", self.extracted_data[1]),
                    ("Models Info", self.extracted_data[2]),
                    ("Input Parameters", self.extracted_data[3]),
                    ("PSD", self.extracted_data[4]),
                    ("Calibrated Parameter Properties", self.extracted_data[5]),
                    ("Convergence", self.extracted_data[6])
                    
                ])
            
        if os.path.exists(calibrated_params_path):
            calibrated_params_data = self.read_calibrated_params(calibrated_params_path)
            data_list.append(("Calibrated Parameters", calibrated_params_data))
            
        # If validation passes, prepare the data for transmission
        try:
            # Prepare the calibration case data
            calibration_case_data = self.prepare_calibration_case_data()
    
            # Send the data through the corresponding output channels
            self.send_data("user_data", self.user_info)
            self.send_data("calibration_case", calibration_case_data)
            
            for name, data_dict in data_list:
                self.send_data(name.replace(" ", "_").lower(), data_dict)
            
            self.send_data("template_meta_info", self.flatten_meta_info(self.templates_meta_info))
    
            # Prepare and send the JSON output
            all_data = {
                "User Data": self.user_info,
                "Calibration Case": calibration_case_data
            }
            for name, data_dict in data_list:
                all_data[name] = data_dict
            all_data["Template Meta Info"] = self.templates_meta_info
            
            json_output = json.dumps(all_data, indent=4)
            self.Outputs.json_output.send(json_output)
    
        except Exception as e:
            QMessageBox.critical(self, "Transmission Error", f"An error occurred while transmitting data: {e}")
    
    def prepare_calibration_case_data(self):
        # This function prepares the calibration case data dictionary
        return {
            "Case Name": self.Case_Name,
            "Cohesivity": ["cohesionless", "cohesive"][self.Cohesivity],
            "Target Flow State": ["Quasi-static", "Intermediate", "Rapid"][self.Target_Flow_State],
            "Consolidation level": ["low", "high"][self.Consolidation_level],
            "Consolidation Pressure": self.consolidation_pressure_spinbox.value(),
            "Local Directory": self.selected_directory
        }
    
    def flatten_meta_info(self, meta_info):
        # Convert nested dictionaries to strings in JSON format
        flattened = {}
        for key, nested_dict in meta_info.items():
            flattened[key] = json.dumps(nested_dict)
        return flattened
    
    def send_data(self, signal_name, data_dict):
        # Convert the data dictionary to an Orange data table
        table = dict_to_orange_table(data_dict)
        # Send the data table through the corresponding output signal
        getattr(self.Outputs, signal_name).send(table)

    # def transmit_data(self):
    #     """Transmit the data as Orange data tables and a JSON file."""
    #     # Clear previous warnings
    #     self.warning()
    #     errors = []
    #     # Validation checks
    #     errors = self.validate_data()

    #     # If there are errors, display them and do not transmit data
    #     if errors:
    #         error_text = "<br/>".join(errors)
    #         self.warning(error_text)
    #         return
    #     self.warning()
    #     log_file_path = os.path.join(self.selected_directory, "log_aspherix-calibration.txt")
    #     calibrated_params_path = os.path.join(self.selected_directory, "calibrated_params.txt")
        
    #     data_list = []
    
    #     # Include the user data
    #     if self.user_info:
    #         data_list.append(("User Data", self.user_info))
        
    #     # Include the Calibration Case data
    #     calibration_case_data = {
    #         "Case Name": self.Case_Name,
    #         "Cohesivity": ["cohesionless", "cohesive"][self.Cohesivity],
    #         "Target Flow State": ["Quasi-static", "Intermediate", "Rapid"][self.Target_Flow_State],
    #         "Consolidation level": ["low", "high"][self.Consolidation_level],
    #         "Consolidation Pressure": self.consolidation_pressure_spinbox.value(),
    #         "Local Directory": self.selected_directory
    #     }
    #     data_list.append(("Calibration Case", calibration_case_data))
        
    #     if os.path.exists(log_file_path):
    #         extracted_data = self.extract_calibration_data(log_file_path)
    #         data_list.extend([
    #             ("Aspherix Info", extracted_data[0]),
    #             ("Templates Info", extracted_data[1]),
    #             ("Models Info", extracted_data[2]),
    #             ("Input Parameters", extracted_data[3]),
    #             ("PSD", extracted_data[4]),
    #             ("Calibrated Parameter Properties", extracted_data[5]),
    #             ("Convergence", extracted_data[6])
                
    #         ])
        
    #     if os.path.exists(calibrated_params_path):
    #         calibrated_params_data = self.read_calibrated_params(calibrated_params_path)
    #         data_list.append(("Calibrated Parameters", calibrated_params_data))
        
    #     # Append Template Meta Info data
    #     # data_list.append(("Template Meta Info", self.templates_meta_info))
        
    #     # Convert dictionaries to Orange data tables using the provided function
    #     try:
    #         for name, data_dict in data_list:
    #             signal_name = name.replace(" ", "_").lower()
    #             if hasattr(self.Outputs, signal_name):
    #                 table = dict_to_orange_table(data_dict)
    #                 getattr(self.Outputs, signal_name).send(table)
    #                 self.warning(f"Sent data for {signal_name}")  # Debugging print
    #             else:
    #                 self.warning(f"Output signal '{signal_name}' does not exist.")  # Debugging print
    #         # Additional code for sending JSON output
    #     except Exception as e:
    #         QMessageBox.information(self, "Debug", f"An error occurred while transmitting data: {e}")
    #         self.warning(f"An error occurred while transmitting data: {e}")
    #         self.warning(f"An error occurred: {e}")  # Debugging print
        
                   
    #     # Convert all data to a JSON string and send it
    #     all_data_json = json.dumps({name: data for name, data in data_list}, indent=4)
    #     self.Outputs.json_output.send(all_data_json)