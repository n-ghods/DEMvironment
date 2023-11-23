## Relational Widget

### Description:

The `OWRelational` widget allows users to add equations from the literature. It provides a GUI interface for the user to input various details related to the correlation and the reference from which the equation is taken.

### Features:

1. **User Info Box**: Displays a message prompting the user to connect user data from the User widget.
2. **Correlation Info Box**: Allows the user to input the name of the correlation and select a Python file.
3. **Reference Info Box**: Provides fields for the user to input details about the reference, such as type (Article/Book), title, authors, ID type (DOI/ISBN), URL, year, equation reference number, journal, publisher, and edition.

### Settings:

- `selected_python_file`: Path to the selected Python file.
- `reference_type`: Type of reference (0 for Article, 1 for Book).
- `title`: Title of the reference.
- `authors`: Authors of the reference.
- `id_type`: Type of ID (0 for DOI, 1 for ISBN).
- `id_value`: Value of the ID.
- `url`: URL of the reference.
- `year`: Publication year of the reference.
- `equation_ref`: Equation reference number.
- `journal`: Journal of the reference (for articles).
- `publisher`: Publisher of the reference (for books).
- `edition`: Edition of the reference (for books).
- `correlation_name_value`: Name of the correlation.

### Signals:

- Inputs:
  - `user_data`: Accepts user data in the form of an Orange table.
- Outputs:
  - `user_data`: Outputs user data as an Orange table.
  - `correlation_data`: Outputs correlation data as an Orange table.
  - `reference_data`: Outputs reference data as an Orange table.
  - `full_data`: Outputs the full data in JSON format.

### Methods:

- `update_correlation_name_value()`: Updates the correlation name value.
- `on_reference_type_changed()`: Handles changes in the reference type dropdown.
- `get_id_validator()`: Returns the appropriate validator for the ID based on its type (DOI/ISBN).
- `on_id_type_changed()`: Handles changes in the ID type dropdown.
- `load_python_file()`: Opens a file dialog to select a Python file and validates its content.
- `validate_python_file(file_path)`: Validates if the selected Python file contains a function.
- `validate_and_send_data()`: Validates the input data and sends it if valid.
- `set_input_data(data)`: Sets the input data for the widget.
- `update_preview()`: Updates the preview text based on the input data.
- `restore_widget_state()`: Restores the widget state based on saved settings.

### Notes:

- The widget uses the `ast` module to parse and validate the content of the selected Python file.
- The widget provides real-time validation for fields like year, URL, authors, and ID.
- The widget emits the input data in various formats, including Orange tables and JSON.