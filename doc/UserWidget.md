## User Widget Documentation

### Overview

The "User" widget in the Orange3 add-on package is designed to collect user information, provide a preview of the entered data, and transmit this data as a dictionary to other connected widgets.

### Features

- **User Input Fields**: Allows users to input their personal information, including:
  - First Name
  - Last Name
  - Email
  - Affiliation
- **Real-time Preview**: Displays a formatted preview of the user's information as it's being entered.
- **Transmit Data**: Sends the user's information as an Orange `Table` object to any connected widgets.

### Usage

1. **Entering Data**: Users can input their information in the provided fields. All fields are required.
2. **Preview**: As users type in their information, a real-time preview is displayed in the main area of the widget.
3. **Transmitting Data**: After filling out all fields, users can click the "Transmit Data" button to send their information to other widgets. If there's an issue with the entered data (e.g., missing fields or invalid email format), an error message will be displayed.

### Validation

- **Email Format**: The widget checks if the entered email follows a standard email format. If not, an error message is displayed.
- **Required Fields**: All fields are mandatory. If any field is left empty, an error message will be shown.

### Error Handling

- The widget provides feedback to users through error messages. For instance, if the email format is incorrect or if any field is left empty, an error message will guide the user to correct the input.
- After correcting the input based on the error message, users can click the "Transmit Data" button again to re-validate and transmit their data.

### Technical Details

- **Implementation**: The widget is implemented using PyQt5 for the user interface and integrates with the Orange3 widget framework.
- **Output**: The widget outputs an Orange `Table` object with the user's information as metadata.