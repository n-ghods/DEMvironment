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
import json
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QComboBox, QLineEdit, QListWidget, QMessageBox, 
                             QFileDialog, QWidget, QTextEdit)
from Orange.widgets import widget, gui, settings
from Orange.widgets.widget import Output

class OWLookupMetadataWarehouse(widget.OWWidget):
    name = "Lookup Metadata Warehouse"
    description = "Search and preview metadata from a warehouse directory."
    icon = "icons/LookupMetadataWarehouse.png"
    priority = 7

    class Inputs:
        metadata_warehouse_directory = widget.Input("Metadata Warehouse Directory", str)

    # Output signal to display the previewed file content
    class Outputs:
        file_content = widget.Output("File Content", str)

    # Settings
    metadata_warehouse_directory = settings.Setting("")

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.file_stats = {"exp": 0, "rel": 0, "calib": 0}
        self.current_file_type = None
        self.keys_for_file_type = {"exp": set(), "rel": set(), "calib": set()}
        
        # self.search_results_list = QListWidget()
        # self.search_results_list.itemClicked.connect(self.display_file_content)
        # self.mainArea.layout().addWidget(self.search_results_list)
    
        # self.file_preview = QTextEdit()
        # self.file_preview.setReadOnly(True)
        # self.mainArea.layout().addWidget(self.file_preview)

    def setup_ui(self):
        # Layout for directory path input and browse button
        directory_layout = QHBoxLayout()
        self.directory_input = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_directory)
        directory_layout.addWidget(self.directory_input)
        directory_layout.addWidget(self.browse_button)
        self.controlArea.layout().addLayout(directory_layout)

        # Load and Validate button
        self.load_validate_button = QPushButton("Load and Validate")
        self.load_validate_button.clicked.connect(self.load_and_validate)
        self.controlArea.layout().addWidget(self.load_validate_button)

        # File statistics display
        self.stats_label = QLabel("File Statistics: Not Loaded")
        self.controlArea.layout().addWidget(self.stats_label)

        # Lookup Box
        lookup_box = gui.widgetBox(self.controlArea, "Look up")
        self.file_type_combo = QComboBox()
        self.file_type_combo.addItems(["Experiment", "Relational", "Calibration"])
        self.file_type_combo.currentTextChanged.connect(self.on_file_type_changed)
        lookup_box.layout().addWidget(self.file_type_combo)

        # Search key dropdown and Search value input
        self.search_key_combo = QComboBox()
        self.search_value_input = QLineEdit()
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.on_search_clicked)
        lookup_box.layout().addWidget(QLabel("Search Key:"))
        lookup_box.layout().addWidget(self.search_key_combo)
        lookup_box.layout().addWidget(QLabel("Search Value:"))
        lookup_box.layout().addWidget(self.search_value_input)
        lookup_box.layout().addWidget(self.search_button)

        # Search results list
        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.preview_file)
        self.mainArea.layout().addWidget(self.results_list)

        # File content preview
        self.file_preview = QTextEdit()
        self.file_preview.setReadOnly(True)
        self.mainArea.layout().addWidget(self.file_preview)

    def browse_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Metadata Warehouse Directory")
        if dir_path:
            self.metadata_warehouse_directory = dir_path
            self.directory_input.setText(dir_path)

    def load_and_validate(self):
        if not os.path.exists(self.metadata_warehouse_directory):
            QMessageBox.warning(self, "Error", "Directory does not exist.")
            return

        self.file_stats = {"exp": 0, "rel": 0, "calib": 0}
        self.keys_for_file_type = {"exp": set(), "rel": set(), "calib": set()}

        for file in os.listdir(self.metadata_warehouse_directory):
            if file.endswith(".json"):
                prefix = file.split("-")[0]
                if prefix in ["exp", "rel", "calib"]:
                    self.file_stats[prefix] += 1
                    self.collect_keys_from_file(file, prefix)

        self.stats_label.setText(f"File Statistics: exp-{self.file_stats['exp']}, "
                                 f"rel-{self.file_stats['rel']}, calib-{self.file_stats['calib']}")

    def collect_keys_from_file(self, file_name, prefix):
        file_path = os.path.join(self.metadata_warehouse_directory, file_name)
        with open(file_path, 'r') as file:
            data = json.load(file)
            self.extract_keys(data, self.keys_for_file_type[prefix])
    
    def extract_keys(self, data, keys_set):
        if isinstance(data, dict):
            for key, value in data.items():
                keys_set.add(key)
                self.extract_keys(value, keys_set)
        elif isinstance(data, list):
            for item in data:
                self.extract_keys(item, keys_set)


    def on_file_type_changed(self, text):
        self.current_file_type = {"Experiment": "exp", "Relational": "rel", "Calibration": "calib"}[text]
        self.populate_search_key_dropdown()

    def populate_search_key_dropdown(self):
        self.search_key_combo.clear()
        keys = self.keys_for_file_type.get(self.current_file_type, set())
        self.search_key_combo.addItems(sorted(keys))


    def search_files(self):
        search_key = self.search_key_combo.currentText()
        search_value = self.search_value_input.text()
        self.results_list.clear()

        for file in os.listdir(self.metadata_warehouse_directory):
            if file.startswith(self.current_file_type) and file.endswith(".json"):
                file_path = os.path.join(self.metadata_warehouse_directory, file)
                with open(file_path, 'r') as json_file:
                    data = json.load(json_file)
                    if search_key in data and data[search_key] == search_value:
                        self.results_list.addItem(file)
    
    def match_key_value(self, data, key, value):
        if isinstance(data, dict):
            for k, v in data.items():
                if k == key and str(v) == value:
                    return True
                elif isinstance(v, (dict, list)):
                    if self.match_key_value(v, key, value):
                        return True
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    if self.match_key_value(item, key, value):
                        return True
        return False

    def on_search_clicked(self):
        search_key = self.search_key_combo.currentText()
        search_value = self.search_value_input.text()
    
        # Clear the previous results
        self.results_list.clear()
    
        # Check if the key and value are provided
        if not search_key or not search_value:
            QMessageBox.warning(self, "Warning", "Please provide both search key and value.")
            return
    
        # Iterate over the files in the selected category
        for file_name in os.listdir(self.metadata_warehouse_directory):
            if file_name.startswith(self.current_file_type) and file_name.endswith('.json'):
                file_path = os.path.join(self.metadata_warehouse_directory, file_name)
                with open(file_path, 'r') as json_file:
                    data = json.load(json_file)
                    if self.match_key_value(data, search_key, search_value):
                        self.results_list.addItem(file_name)
    
    def preview_file(self, item):
        file_name = item.text()
        file_path = os.path.join(self.metadata_warehouse_directory, file_name)
        with open(file_path, 'r') as file:
            content = json.load(file)
            self.file_preview.setText(json.dumps(content, indent=4))
            self.Outputs.file_content.send(json.dumps(content))
    
    def display_file_content(self, item):
        file_name = item.text()
        file_path = os.path.join(self.metadata_warehouse_directory, file_name)
        
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                pretty_json = json.dumps(data, indent=4, sort_keys=True)
                self.file_preview.setText(pretty_json)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file: {e}")
    
    @Inputs.metadata_warehouse_directory
    def set_metadata_warehouse_directory(self, path):
        if path:
            self.metadata_warehouse_directory = path
            self.directory_input.setText(path)
            self.load_and_validate()

