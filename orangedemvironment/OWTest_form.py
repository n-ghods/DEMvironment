# -*- coding: utf-8 -*-
import os
import json

from Orange.widgets import widget, gui
from Orange.widgets.settings import Setting
from PyQt5.QtWidgets import QFormLayout, QPushButton, QTextEdit, QFileDialog, QComboBox, QMessageBox, QLineEdit, QLabel,QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout, QDoubleSpinBox, QCheckBox, QSpinBox

class OWMetaDataGenerator2(widget.OWWidget):
    name = "MetaData Generator 2"
    description = "Generates metadata JSON from simulation log"
    icon = "icons/YourIcon.svg"  # Replace with your icon file

    # Define widget inputs and outputs here
    inputs = []
    outputs = []

    # Widget settings
    directory = Setting("")
    recent_directories = Setting([])  # List to save recent directories

    def __init__(self):
        super().__init__()

        # Directory selector with a horizontal layout
        box = gui.widgetBox(self.controlArea, "Simulation Directory")
        
        hbox = QHBoxLayout()  # Create a new horizontal box layout
        
        self.dir_combo_box = QComboBox(self)
        self.dir_combo_box.addItems(self.recent_directories)
        self.dir_combo_box.setEditable(True)
        self.dir_combo_box.setCurrentText(self.directory)
        self.dir_combo_box.currentTextChanged.connect(self.on_directory_change)
        
        self.browse_button = QPushButton("Browse", self)
        self.browse_button.clicked.connect(self.browse)
        
        hbox.addWidget(self.dir_combo_box)  # Add directory path field to the horizontal box layout
        hbox.addWidget(self.browse_button)  # Add browse button next to it
        
        box.layout().addLayout(hbox)  # Add the horizontal box layout to the box
        
        # Info label
        self.info_label = QLabel("", self)
        box.layout().addWidget(self.info_label)
        
        # Information form
        form_box = gui.widgetBox(self.controlArea, "Simulation Details")

        # Calibration Case Info
        calibration_layout = QFormLayout()
        self.calibration_name = QLineEdit(self.directory, self)  # Default to directory's name
        self.particle_cohesivity = QLineEdit(self)
        self.particle_type = QLineEdit(self)
        self.target_flow_state = QComboBox(self)
        self.target_flow_state.addItems(["quasi-static", "intermediate", "free flow", "rapid", "combined"])
        self.consolidation_level = QComboBox(self)
        self.consolidation_level.addItems(["low", "high"])
        self.consolidation_pressure = QDoubleSpinBox(self)
        self.consolidation_pressure.setSuffix(" Pa")
        self.consolidation_pressure.setRange(0, 1e6)  # You can adjust this range
        self.contact_model = QLineEdit(self)
        self.cohesion_model = QLineEdit(self)
        self.converged = QComboBox(self)
        self.converged.addItems(["yes", "no"])

        calibration_layout.addRow("Name:", self.calibration_name)
        calibration_layout.addRow("Particle Cohesivity:", self.particle_cohesivity)
        calibration_layout.addRow("Particle Type:", self.particle_type)
        calibration_layout.addRow("Target Flow State:", self.target_flow_state)
        calibration_layout.addRow("Consolidation Level:", self.consolidation_level)
        calibration_layout.addRow("Consolidation Pressure:", self.consolidation_pressure)
        calibration_layout.addRow("Contact Model:", self.contact_model)
        calibration_layout.addRow("Cohesion Model:", self.cohesion_model)
        calibration_layout.addRow("Converged:", self.converged)
        
        # PSD
        psd_layout = QVBoxLayout()
        self.psd_entries = []
        self.add_psd_button = QPushButton("Add PSD Entry", self)
        self.add_psd_button.clicked.connect(self.add_psd_entry)
        psd_layout.addWidget(self.add_psd_button)

        # Author Info
        author_layout = QFormLayout()
        self.author_name = QLineEdit(self)
        self.author_email = QLineEdit(self)
        author_layout.addRow("Name:", self.author_name)
        author_layout.addRow("Email:", self.author_email)

        # DEM Software Info
        software_layout = QFormLayout()
        self.software_name = QLineEdit(self)
        self.software_distribution = QLineEdit(self)
        self.software_version = QLineEdit(self)
        self.software_git_commit = QLineEdit(self)
        software_layout.addRow("Software Name:", self.software_name)
        software_layout.addRow("Distribution:", self.software_distribution)
        software_layout.addRow("Version:", self.software_version)
        software_layout.addRow("Git Commit:", self.software_git_commit)

        # Combine all categories
        form_box.layout().addLayout(calibration_layout)
        form_box.layout().addLayout(psd_layout)
        form_box.layout().addLayout(author_layout)
        form_box.layout().addLayout(software_layout)
        
        
        # Generate metadata button
        self.generate_button = QPushButton("Generate Metadata", self)
        self.generate_button.clicked.connect(self.generate_metadata)
        self.controlArea.layout().addWidget(self.generate_button)

        # Log display
        self.log_display = QTextEdit(self)
        self.mainArea.layout().addWidget(self.log_display)

    def add_psd_entry(self):
            """Adds PSD entry fields to the form"""
            layout = QFormLayout()
            diameter = QDoubleSpinBox(self)
            diameter.setRange(0, 1e3)  # Adjust the range as needed
            fraction_type = QComboBox(self)
            fraction_type.addItems(["mass", "volume"])
            fraction_value = QDoubleSpinBox(self)
            fraction_value.setRange(0, 1)
            layout.addRow("Diameter:", diameter)
            layout.addRow("Fraction Type:", fraction_type)
            layout.addRow("Fraction Value:", fraction_value)
            self.psd_entries.append((diameter, fraction_type, fraction_value))
            self.add_psd_button.parent().layout().insertLayout(self.add_psd_button.parent().layout().count()-1, layout)
    
    def on_directory_change(self, new_directory):
        # Handle directory change event
        self.directory = new_directory
        # Check directory contents and update info label
        self.update_info_label()
        # Check if directory is not empty
        if os.listdir(new_directory) is False:
            QMessageBox.warning(self, "Warning", "Selected directory is empty!")
        

        if new_directory not in self.recent_directories:
            self.recent_directories.insert(0, new_directory)
            self.dir_combo_box.insertItem(0, new_directory)

            # Limit to 10 recent directories for simplicity. Adjust as needed.
            while len(self.recent_directories) > 10:
                last_dir = self.recent_directories.pop()
                idx = self.dir_combo_box.findText(last_dir)
                if idx >= 0:
                    self.dir_combo_box.removeItem(idx)
    def update_info_label(self):
            if not os.path.exists(self.directory) or not os.listdir(self.directory):
                self.info_label.setText("Directory is empty! Provide another path.")
                return
    
            log_files = [f for f in os.listdir(self.directory) if f.startswith("log") and not f.endswith(".bak")]
            if log_files:
                self.info_label.setText("Log file(s) detected: " + ", ".join(log_files))
            else:
                self.info_label.setText("No valid log file detected!")
    def browse(self):
        # Use QFileDialog to pick directory
        chosen_directory = QFileDialog.getExistingDirectory(self, "Select Simulation Directory", self.directory or os.path.expanduser("~"))
        if chosen_directory:
            self.directory = chosen_directory
            self.on_directory_change(chosen_directory)
            self.dir_combo_box.setCurrentText(chosen_directory)
        # Check directory contents and update info label
        self.update_info_label()
    def generate_metadata(self):
        # Fetch details from form
        simulation_info = self.info_line_edit.text()

        # Assuming the log file is named 'log.txt' inside the simulation directory
        log_file_path = os.path.join(self.directory, "log-aspherix_calibration.txt")

        # Read log file
        with open(log_file_path, 'r') as f:
            log_content = f.read()
            self.log_display.setPlainText(log_content)  # Display log in widget

        # Fetch PSD details
        psd_data = [{"diameter": entry[0].value(), "type": entry[1].currentText(), "value": entry[2].value()} for entry in self.psd_entries]

        # Fetch Author and Software details
        author_info = {"name": self.author_name.text(), "email": self.author_email.text()}
        software_info = {"name": self.software_name.text(), "distribution": self.software_distribution.text(), "version": self.software_version.text(), "git_commit": self.software_git_commit.text()}

        # Assemble dictionary
        metadata = {
            #"calibration_case_info": calibration_data,
            "psd": psd_data,
            "author_info": author_info,
            "software_info": software_info
        }

        # Save as JSON
        metadata_file_path = os.path.join(self.directory, "metadata.json")
        with open(metadata_file_path, 'w') as f:
            json.dump(metadata, f, indent=4)

        self.log_display.append("\nMetadata generated and saved!")

# The following block is to test the widget outside Orange Canvas
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    window = OWMetaDataGenerator2()
    window.show()
    app.exec()
