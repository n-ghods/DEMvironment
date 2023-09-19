import os
import json

from Orange.widgets import widget, gui
from Orange.widgets.settings import Setting
from PyQt5.QtWidgets import QFormLayout, QPushButton, QTextEdit, QFileDialog, QComboBox, QMessageBox, QLineEdit, QLabel,QHBoxLayout

class OWMetaDataGenerator(widget.OWWidget):
    name = "MetaData Generator"
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
        form_layout = QFormLayout()

        self.info_line_edit = QLineEdit(self)
        form_layout.addRow("Simulation Information:", self.info_line_edit)

        # You can add more form fields as necessary

        form_box.layout().addLayout(form_layout)

        # Generate metadata button
        self.generate_button = QPushButton("Generate Metadata", self)
        self.generate_button.clicked.connect(self.generate_metadata)
        self.controlArea.layout().addWidget(self.generate_button)

        # Log display
        self.log_display = QTextEdit(self)
        self.mainArea.layout().addWidget(self.log_display)

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
        log_file_path = os.path.join(self.directory, "log.txt")

        # Read log file
        with open(log_file_path, 'r') as f:
            log_content = f.read()
            self.log_display.setPlainText(log_content)  # Display log in widget

        # Create metadata dictionary
        metadata = {
            "simulation_info": simulation_info,
            "log_content": log_content
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
    window = OWMetaDataGenerator()
    window.show()
    app.exec()
