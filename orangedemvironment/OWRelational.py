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
from PyQt5.QtWidgets import QHBoxLayout, QTextEdit, QFileDialog, QLineEdit, QLabel,QPushButton
from Orange.widgets import widget, gui, settings
from Orange.data import Table
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp
from PyQt5.QtCore import Qt
from shared.dictHandler import dict_to_orange_table, format_dict_as_text, orange_table_to_dict
import ast #Abstarct Syntax Tree:  It's commonly used for analyzing the structure of Python code.
import json


class OWRelational(widget.OWWidget):
    name = "Relational"
    description = "Add equations from the literature."
    icon = "icons/Relational.png"
    priority = 3
    want_main_area = True
    
    selected_python_file = settings.Setting("")
    reference_type = settings.Setting(0)  # 0 for Article, 1 for Book
    title = settings.Setting("")
    authors = settings.Setting("")
    id_type = settings.Setting(0)  # 0 for DOI, 1 for ISBN
    id_value = settings.Setting("")
    url = settings.Setting("")
    year = settings.Setting("")
    equation_ref = settings.Setting("")
    journal = settings.Setting("")  
    publisher = settings.Setting("") 
    edition = settings.Setting("") 
    correlation_name_value = settings.Setting("") 

    
    # Input signals
    class Inputs:
        user_data = widget.Input("User Data", Table)
        
    class Outputs:
        user_data = widget.Output("User Data", Table)
        correlation_data =  widget.Output("Correlation Data", Table)
        reference_data = widget.Output("Reference Data", Table)
        full_data = widget.Output("Full Data (JSON)", str)

    def __init__(self):
        super().__init__()
        
        
        self.user_info = {}
        self.correlation_info = {}
        self.reference_info = {}
        
        
        # Control Area
        # User Info Box
        user_box = gui.widgetBox(self.controlArea, "User Info", orientation="vertical")
        self.info_label = gui.widgetLabel(user_box, "Please connect the user data from the User widget.")
        self.info_label.setStyleSheet('color: red')
        
        # Correlation Info Box
        correlation_box = gui.widgetBox(self.controlArea, "Correlation Info", orientation='vertical')
        # Correlation Name Entry
        correlation_name_layout = QHBoxLayout()
        self.correlation_name_label = QLabel("Correlation Name:")
        self.correlation_name = QLineEdit(self)
        self.correlation_name.setText(self.correlation_name_value)
        correlation_name_layout.addWidget(self.correlation_name_label)
        correlation_name_layout.addWidget(self.correlation_name)
        self.correlation_name.textChanged.connect(self.update_correlation_name_value)
        correlation_box.layout().addLayout(correlation_name_layout)
        
        # Python File Path Entry and Load Button
        python_file_layout = QHBoxLayout()
        self.python_file_path = QLineEdit(self.selected_python_file)
        self.python_file_path.setReadOnly(False)  # Make it read-only
        self.load_python_file_btn = QPushButton("Load Python File", self)
        self.load_python_file_btn.clicked.connect(self.load_python_file)
        python_file_layout.addWidget(self.python_file_path)
        python_file_layout.addWidget(self.load_python_file_btn)
        correlation_box.layout().addLayout(python_file_layout)

        # Connect the textChanged signal to update the preview
        self.python_file_path.textChanged.connect(self.update_preview)
        
        self.selected_python_file_label = gui.label(self.controlArea, self, "")
                
        # Article/Book Info Box
        info_box = gui.widgetBox(self.controlArea, "Reference Info", orientation="vertical")

        # Reference Type (Article or Book)
        self.reference_type_combo = gui.comboBox(info_box, self, "reference_type", label="Reference Type:",
                                                 items=["Article", "Book"], callback=self.on_reference_type_changed)
        # self.journal_edit = gui.lineEdit(info_box, self, "journal", label="Journal:")
        # self.publisher_edit = gui.lineEdit(info_box, self, "publisher", label="Publisher:")
        # self.edition_edit = gui.lineEdit(info_box, self, "edition", label="Edition:")
        self.journal_label = gui.label(info_box, self, "Journal:")
        self.journal_edit = gui.lineEdit(info_box, self, "journal")
        
        self.publisher_label = gui.label(info_box, self, "Publisher:")
        self.publisher_edit = gui.lineEdit(info_box, self, "publisher")
        
        self.edition_label = gui.label(info_box, self, "Edition:")
        self.edition_edit = gui.lineEdit(info_box, self, "edition")

        # Initially hide publisher and edition fields and their labels
        self.publisher_label.hide()
        self.publisher_edit.hide()
        self.edition_label.hide()
        self.edition_edit.hide()
        

    
        # Title
        self.title_edit = gui.lineEdit(info_box, self, "title", label="Title:")

        # Authors
        #self.authors_edit = gui.lineEdit(info_box, self, "authors", label="Authors:")
        # Authors
        self.authors_edit = gui.lineEdit(info_box, self, "authors", label="Authors:")
        self.authors_edit.setPlaceholderText("(Last Name, First Name), (Last Name, First Name), ...")

        id_layout = QHBoxLayout()

        # ID (DOI or ISBN)
        self.id_type_combo = gui.comboBox(info_box, self, "id_type", items=["DOI", "ISBN"], label="ID Type:")
        id_layout.addWidget(self.id_type_combo)
        
        self.id_value_edit = gui.lineEdit(None, self, "id_value", label="ID Value:")
        id_layout.addWidget(self.id_value_edit)
        
        # Add the horizontal layout to the info_box
        info_box.layout().addLayout(id_layout)

        # URL
        self.url_edit = gui.lineEdit(info_box, self, "url", label="URL:")

        # Year
        self.year_edit = gui.lineEdit(info_box, self, "year", label="Year:")

        # Equation Reference Number
        self.equation_ref_edit = gui.lineEdit(info_box, self, "equation_ref", label="Equation Ref. Number:")
        
        # connect for real-time signal
        self.title_edit.textChanged.connect(self.update_preview)
        self.authors_edit.textChanged.connect(self.update_preview)
        self.id_value_edit.textChanged.connect(self.update_preview)
        self.url_edit.textChanged.connect(self.update_preview)
        self.year_edit.textChanged.connect(self.update_preview)
        self.equation_ref_edit.textChanged.connect(self.update_preview)
        self.journal_edit.textChanged.connect(self.update_preview)
        self.publisher_edit.textChanged.connect(self.update_preview)
        self.edition_edit.textChanged.connect(self.update_preview)              
        self.reference_type_combo.currentIndexChanged.connect(self.update_preview)
        self.id_type_combo.currentIndexChanged.connect(self.update_preview)
        self.python_file_path.textChanged.connect(self.update_preview)
        # Main Area
        self.preview_text = QTextEdit(self.mainArea)
        self.preview_text.setReadOnly(True)
        self.mainArea.layout().addWidget(self.preview_text)
    
        # Now, it's safe to call the on_reference_type_changed method
        self.on_reference_type_changed()
    
        # Add "Validate and Send Data" button to the bottom of the control area
        gui.button(self.controlArea, self, "Validate and Send Data", callback=self.validate_and_send_data)

        
        # Add validators
        self.year_edit.setPlaceholderText("e.g., 2021")
        self.url_edit.setPlaceholderText("e.g., https://www.example.com")
        self.authors_edit.setPlaceholderText("(Last Name, First Name), ...")
        self.id_value_edit.setPlaceholderText("Enter DOI or ISBN based on the selected ID Type")
    
        # Call the update_preview method to initialize the preview
        self.update_preview()
        
        # Restore widget state
        self.restore_widget_state()
    
    def update_correlation_name_value(self):
        self.correlation_name_value = self.correlation_name.text()
    
    def on_reference_type_changed(self):
        if self.reference_type == 0:  # Article
            self.journal_label.show()
            self.journal_edit.show()
            self.publisher_label.hide()
            self.publisher_edit.hide()
            self.edition_label.hide()
            self.edition_edit.hide()
        else:  # Book
            self.journal_label.hide()
            self.journal_edit.hide()
            self.publisher_label.show()
            self.publisher_edit.show()
            self.edition_label.show()
            self.edition_edit.show()
        self.update_preview()
    
    def get_id_validator(self):
        if self.id_type == 0:  # DOI
            return QRegExpValidator(QRegExp("^10.\d{4,9}/[-._;()/:A-Z0-9]+$", Qt.CaseInsensitive))
        else:  # ISBN
            return QRegExpValidator(QRegExp("^(97(8|9))?\d{9}(\d|X)$"))

    def on_id_type_changed(self):
        self.id_value_edit.setValidator(self.get_id_validator())
        self.id_value_edit.update()
    
        
    def load_python_file(self):
        """Load a Python file and validate its content."""
        
        # Open a file dialog to select a ".py" file
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Python File", "", "Python Files (*.py)")
        if file_path:
            self.selected_python_file = file_path
            self.python_file_path.setText(file_path)  # Update the QLineEdit with the new path
            #self.selected_python_file_label.setText(file_path)
            if self.validate_python_file(file_path):
                # If the file contains a function, display a success message
                self.selected_python_file_label.setText(f"{file_path}\nContains a valid function!")
                self.selected_python_file_label.setStyleSheet('color: green')
            else:
                # Display an error message if the file doesn't contain a function
                self.selected_python_file_label.setText(f"{file_path}\nError: No valid function found!")
                self.selected_python_file_label.setStyleSheet('color: red')
            

    def validate_python_file(self, file_path):
        """Validate if the selected Python file contains a function."""
        with open(file_path, "r") as f:
            content = f.read()
            try:
                parsed_ast = ast.parse(content)
                for node in parsed_ast.body:
                    if isinstance(node, ast.FunctionDef):
                        return True
            except Exception as e:
                # Handle any parsing errors or other exceptions
                self.selected_python_file_label.setText(f"Error parsing file: {e}")
                self.selected_python_file_label.setStyleSheet('color: red')
        return False

    def validate_and_send_data(self):
        self.preview_text.clear()
        
        errors = self.validate_data()

        # If there are no errors, validation has passed
        if not errors:
            self.update_preview()  # Update the preview with the latest valid data
            self.send_validated_data()  # Emit the output signals with the valid data
        else:
            # If validation fails, show the errors and clear the outputs
            error_text = "<br/>".join(errors)
            self.preview_text.setHtml(f'<span style="color: red;">{error_text}</span>')
            self.clear_outputs()  # Clear the outputs so that no invalid data is sent

    def validate_data(self):
        errors = []
        
        # Check if the correlation name is empty
        if not self.correlation_name.text():
            errors.append("Please enter a correlation name before proceeding.")

        # Validate Year
        if not self.year.isdigit() or len(self.year) != 4:
            errors.append("Year should be a four-digit integer.")
    
        # Validate URL
        import re
        url_pattern = re.compile(r'^(http|https)://.*$')
        if not url_pattern.match(self.url):
            errors.append("Invalid URL format.")
        
        # Validate the Python file
        if not self.selected_python_file or not self.validate_python_file(self.selected_python_file):
            errors.append("A valid Python file is required.")
        
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
        
        # Validate Authors
        # authors_pattern = re.compile(r"^(\([A-Za-z\s]+,\s[A-Za-z\s]+\),\s*)+(\([A-Za-z\s]+,\s[A-Za-z\s]+\))?$")
        authors_pattern = re.compile(r"^(\([A-Za-z\s]+,\s[A-Za-z\s]+\))(,\s*\([A-Za-z\s]+,\s[A-Za-z\s]+\))*$")


        if not authors_pattern.match(self.authors):
            errors.append("Authors should be in the format '(Last Name, First Name), ...'.")
    
        # Validate ID
        if self.id_type == 0:  # DOI
            doi_pattern = re.compile(r"^10.\d{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)
            if not doi_pattern.match(self.id_value):
                errors.append("Invalid DOI format.")
        else:  # ISBN
            isbn_pattern = re.compile(r"^(97(8|9))?\d{9}(\d|X)$")
            if not isbn_pattern.match(self.id_value):
                errors.append("Invalid ISBN format.")
    
        # Display errors or send data
        if errors:
            error_text = "<br/>".join(errors)
            self.preview_text.setHtml(f'<span style="color: red;">{error_text}</span>')
        else:
            self.preview_text.setHtml('<span style="color: green;">Data is valid!</span>')
            self.update_preview()

        # Validate selected Python file
        if not hasattr(self, 'selected_python_file') or not self.selected_python_file or not self.validate_python_file(self.selected_python_file):
            errors.append("Please select a valid Python file containing a function.")
    
       # Display errors or send data
        if errors:
            error_text = "<br/>".join(errors)
            self.preview_text.setHtml(f'<span style="color: red;">{error_text}</span>')
        else:
            self.preview_text.setHtml('<span style="color: green;">Data is valid!</span>')
            self.update_preview()
        
        return errors

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
        
        # Update widget attributes based on GUI components
        self.title = self.title_edit.text()
        self.authors = self.authors_edit.text()
        self.id_value = self.id_value_edit.text()
        self.url = self.url_edit.text()
        self.year = self.year_edit.text()
        self.equation_ref = self.equation_ref_edit.text()
        self.journal = self.journal_edit.text()
        self.publisher = self.publisher_edit.text()
        self.edition = self.edition_edit.text()
        self.reference_type = self.reference_type_combo.currentIndex()
        self.id_type = self.id_type_combo.currentIndex()
        self.selected_python_file = self.python_file_path.text()
        self.correlation_name_value = self.correlation_name.text()
        
        # Update the selected_python_file setting with the current file path
        #self.selected_python_file = self.selected_python_file.text()
        
        # Extract User Info
        user_info_text = format_dict_as_text(self.user_info, "User Info")

        self.correlation_info = {
            "Correlation Name": self.correlation_name_value,
            "Python file path": self.selected_python_file
            }
        # Filter out None values
        self.correlation_info = {k: v for k, v in self.correlation_info.items() if v is not None and v != ""}
        correlation_info_text = format_dict_as_text(self.correlation_info, "Correlation Info")
        #correlation_data_table = dict_to_orange_table(correlation_info)
        # Create a dictionary from article input
        self.reference_info = {
            "Reference Type": "Article" if self.reference_type == 0 else "Book",
            "Title": self.title,
            "Authors": self.authors,
            "Journal": self.journal if self.reference_type == 0 else None,
            "Publisher": self.publisher if self.reference_type == 1 else None,
            "Edition": self.edition if self.reference_type == 1 else None,
            "ID Type": "DOI" if self.id_type == 0 else "ISBN",
            "ID Value": self.id_value,
            "URL": self.url,
            "Year": self.year,
            "Equation Ref. Number": self.equation_ref
        }

        # Filter out None values
        self.reference_info = {k: v for k, v in self.reference_info.items() if v is not None and v != ""}

        reference_info_text = format_dict_as_text(self.reference_info, "reference Info")
        #reference_data_table = dict_to_orange_table(reference_info)
        # Combine the texts for the preview
        combined_text = "<br/><br/>".join([user_info_text,correlation_info_text, reference_info_text])  # Add other info texts
        self.preview_text.setHtml(combined_text)
        
        
        # # Emit the data as Orange data tables
        # self.Outputs.user_data.send(dict_to_orange_table(self.user_info))
        # self.Outputs.correlation_data.send(correlation_data_table)
        # self.Outputs.reference_data.send(reference_data_table)
        
        # # Emit the full nested dictionary as JSON
        # full_data = {
        #     "User Info": self.user_info, #orange_table_to_dict(self.user_data),
        #     "Correlation Info": correlation_info,
        #     "Reference Info": reference_info
        # }
        # self.Outputs.full_data.send(json.dumps(full_data, indent=4))
        

    def send_validated_data(self):
        # Prepare the data for emission
        user_data_table = dict_to_orange_table(self.user_info)
        correlation_data_table = dict_to_orange_table(self.correlation_info)
        reference_data_table = dict_to_orange_table(self.reference_info)

        # Emit the data as Orange data tables
        self.Outputs.user_data.send(user_data_table)
        self.Outputs.correlation_data.send(correlation_data_table)
        self.Outputs.reference_data.send(reference_data_table)
        
        # Emit the full nested dictionary as JSON
        full_data = {
            "User Info": self.user_info,
            "Correlation Info": self.correlation_info,
            "Reference Info": self.reference_info
        }
        self.Outputs.full_data.send(json.dumps(full_data, indent=4))
    
    def clear_outputs(self):
        # Clear the outputs
        self.Outputs.user_data.send(None)
        self.Outputs.correlation_data.send(None)
        self.Outputs.reference_data.send(None)
        self.Outputs.full_data.send(None)
    
    def restore_widget_state(self):
        """Restore the widget state based on saved settings."""
        # # Restore Python file path
        # if self.selected_python_file:
        #     self.selected_python_file_label.setText(f"{self.selected_python_file}")
        #     self.selected_python_file_label.setStyleSheet('color: green')
        #     if not self.validate_python_file(self.selected_python_file):
        #         self.selected_python_file_label.setText(f"Invalid Python file: {self.selected_python_file}")
        #         self.selected_python_file_label.setStyleSheet('color: red')

        # Restore other fields
        self.title_edit.setText(self.title)
        self.authors_edit.setText(self.authors)
        self.id_value_edit.setText(self.id_value)
        self.url_edit.setText(self.url)
        self.year_edit.setText(self.year)
        self.equation_ref_edit.setText(self.equation_ref)
        self.journal_edit.setText(self.journal)
        self.publisher_edit.setText(self.publisher)
        self.edition_edit.setText(self.edition)
        self.reference_type_combo.setCurrentIndex(self.reference_type)
        self.id_type_combo.setCurrentIndex(self.id_type)

        # Update the preview
        self.update_preview()
    
   

