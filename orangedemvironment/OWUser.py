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
from PyQt5.QtWidgets import QLineEdit, QTextEdit, QFormLayout
from Orange.widgets import widget, gui, settings
from Orange.data import Table, Domain, StringVariable
from Orange.widgets.widget import Output
import re


class OWUser(widget.OWWidget):
    name = "User"
    description = "Collect user information and preview and transmit as a dictionary."
    icon = "icons/user.png"  
    priority = 1
    want_main_area = True  # This will create the main area for the preview.
    
    # Defined the settings for each input field
    first_name = settings.Setting("")
    last_name = settings.Setting("")
    email = settings.Setting("")
    affiliation = settings.Setting("")
    
    
    class Outputs:
        user_data = Output("User Data", Table)

    def __init__(self):
        super().__init__()

        # Control Area
        form_layout = QFormLayout()
        
        # Initialize input fields with the saved settings
        self.first_name_edit = QLineEdit(self.first_name, self)
        self.last_name_edit = QLineEdit(self.last_name, self)
        self.email_edit = QLineEdit(self.email, self)
        self.affiliation_edit = QLineEdit(self.affiliation, self)


        # Add fields to form layout
        form_layout.addRow("First Name:", self.first_name_edit)
        form_layout.addRow("Last Name:", self.last_name_edit)
        form_layout.addRow("Email:", self.email_edit)
        form_layout.addRow("Affiliation:", self.affiliation_edit)

        # Add form layout to control area
        box = gui.widgetBox(self.controlArea, orientation="vertical")
        box.layout().addLayout(form_layout)

        # Connect signals for real-time updates
        self.first_name_edit.textChanged.connect(self.update_settings_and_preview)
        self.last_name_edit.textChanged.connect(self.update_settings_and_preview)
        self.email_edit.textChanged.connect(self.update_settings_and_preview)
        self.affiliation_edit.textChanged.connect(self.update_settings_and_preview)

        # Add Transmit Data button
        self.transmit_button = gui.button(box, self, "Transmit Data", callback=self.transmit_data)

        # Main Area for preview
        self.preview_text = QTextEdit(self)
        self.preview_text.setReadOnly(True)  # Make the preview read-only
        self.mainArea.layout().addWidget(self.preview_text)
        # Update the preview
        self.preview_data()
    def update_settings_and_preview(self):
        # Update settings
        self.first_name = self.first_name_edit.text()
        self.last_name = self.last_name_edit.text()
        self.email = self.email_edit.text()
        self.affiliation = self.affiliation_edit.text()

        # Update the preview
        self.preview_data()

    def is_valid_email(self, email):
        """Check if the provided email has a valid format."""
        email_regex = r"[^@]+@[^@]+\.[^@]+"
        return re.match(email_regex, email) is not None

    def validate_inputs(self):
        """Validate the user inputs."""
        # Check if all fields are filled out
        if not all([self.first_name_edit.text(),
                    self.last_name_edit.text(),
                    self.email_edit.text(),
                    self.affiliation_edit.text()]):
            return False, "All fields are required."

        # Validate email format
        if not self.is_valid_email(self.email_edit.text()):
            return False, "Invalid email format."

        return True, ""

    def preview_data(self):
        user_info = {
            "First Name": self.first_name_edit.text(),
            "Last Name": self.last_name_edit.text(),
            "Email": self.email_edit.text(),
            "Affiliation": self.affiliation_edit.text(),
        }

        # Convert the dictionary to a colored and formatted string
        entries = [f'<font color="blue">"{key}"</font>: <font color="green">"{value}"</font>' for key, value in user_info.items()]
        formatted_text = '{<br/>' + ',<br/>'.join(entries) + '<br/>}'
        self.preview_text.setHtml(formatted_text)

    def transmit_data(self):
        # Validate the inputs
        is_valid, error_message = self.validate_inputs()
        if not is_valid:
            # Display an error message to the user
            self.error(error_message)
            return
        else:
            # Clear any previous error messages
            self.error()

        # Extract data from the form
        user_info = {
            "First Name": self.first_name_edit.text(),
            "Last Name": self.last_name_edit.text(),
            "Email": self.email_edit.text(),
            "Affiliation": self.affiliation_edit.text(),
        }
        # Create a domain with the desired attributes
        domain = Domain([], [], metas=[StringVariable(key) for key, value in user_info.items()])

        # Convert dictionary to a list of rows
        data = [[value for key, value in user_info.items()]]

        # Create an Orange Table from the data
        table = Table.from_list(domain, data)

        # Emit the table through the output signal
        self.Outputs.user_data.send(table)