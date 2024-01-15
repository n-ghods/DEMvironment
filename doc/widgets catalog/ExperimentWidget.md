# Experiment Widget Documentation

## Overview

The `OWExperiment` widget is designed to create and manage metadata for experimental files. It provides a user-friendly interface to input various details related to an experiment, particle information, and data details. The widget also allows users to preview the entered data and validate it before sending it to other widgets or processes.

## Features

1. **User Info Box**: Displays information about the user. This data is received from another widget, typically named "User widget".
2. **Experiment Info Box**: Allows users to input details about the experiment, such as the name, quantities measured, device used, and more.
3. **Particle Info Box**: Enables users to provide information about the particles used in the experiment, including material, diameter, shape, density, and more.
4. **Data Info Box**: Lets users specify details about the data, such as file location, number of variables, date of collection, and licensing information.
5. **Preview Area**: Displays a real-time preview of the entered data in a formatted manner.
6. **Validation Button**: Validates the entered data and sends it to the outputs if it meets the criteria.

## Inputs

- **user_data**: Accepts a table containing user data. This data is typically provided by the "User widget".

## Outputs

- **user_data_table**: Outputs the user data as an Orange data table.
- **experiment_data_table**: Outputs the experiment information as an Orange data table.
- **particle_data_table**: Outputs the particle information as an Orange data table.
- **data_info_table**: Outputs the data information as an Orange data table.
- **full_data**: Outputs the combined data (User, Experiment, Particle, Data Info) as a JSON string.

## Methods

- **set_input_data(data)**: Receives user data from another widget and updates the User Info Box.
- **update_preview()**: Updates the preview area with the latest entered data.
- **validate_data()**: Validates the entered data based on specific criteria.
- **validate_and_send_data()**: Validates the data and sends it to the outputs if valid.
- **create_exp_info_fields(form_layout)**: Creates input fields for the Experiment Info Box.
- **create_data_info_fields(form_layout)**: Creates input fields for the Data Info Box.
- **toggle_num_variables()**: Toggles the visibility of the number of variables input based on the selected option.
- **browse_file()**: Opens a file dialog to allow users to select a file.

## Usage

1. Connect the "User widget" to the `OWExperiment` widget to provide user data.
2. Fill in the details in the Experiment Info, Particle Info, and Data Info boxes.
3. Preview the entered data in the main area.
4. Click on the "Validate and Send Data" button to validate the data.
5. If the data is valid, it will be sent to the outputs. Otherwise, an error message will be displayed.

## Dependencies

- **PyQt5**: For the graphical user interface.
- **Orange**: For data processing and widget management.
- **json**: For JSON data handling.
- **os**: For file path operations.
- **re**: For regular expression operations.