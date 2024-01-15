## ReadAspherix Widget Documentation

### Overview:

The `OWReadAspherix` widget is designed to load data from Aspherix. It provides a user interface to input and display various parameters related to Aspherix calibration. All the provided information are categorized to different group of data, e.g. User Info, Calibration Case, Simulation details and the Calibration Reference Metadata. The User Info is an input signal to this widget. The calibration case info contains the key values that are entered by the use in the respected info box (that once registered in the metadata warehouse directory, will be used to retrieve information). The Simulation details, contains all the necessary information that is required to reproduce the calibration case, by reading the log file and the file that contains the calibrated parameter. Base on the retrieved data, the Calibration Reference (Exp./Rel.) Info box will be mounted with the used references for the calibration purpose which should be provided with th e relevant metadata file by user.

### Features:

- **User Info Box**: Displays a message prompting the user to connect user data from the User widget.
- **Calibration Case Box**: Allows the user to input various calibration case parameters such as:
  - Case Name
  - Cohesivity (options: cohesionless, cohesive)
  - Target Flow State (options: Quasi-static, Intermediate, Rapid)
  - Consolidation level (options: low, high)
  - Consolidation Pressure (with a spin box for input)
- **Simulation Details Box**: Provides an interface for the user to:
  - Select a directory containing the required files.
  - Check for the presence of specific files in the selected directory.
  - Extract data from the selected directory. This data includes the software specifications that were used for the calibration, the simulation input parameters, the experiments that were used for each target parameters and information about the convergence of the calibration process and finally the calibrated parameters.
    * Note: here the calibration process is also linked to the reference data's metadata which were used for the calibration process. This can highly keep all the calibration data connected.
- **Main Area**: Displays the extracted data in a tree structure.
- **Transmit Data Button**: Allows the user to transmit the data as Orange data tables and a JSON file.

### Methods:

- `update_consolidation_pressure(value)`: Updates the consolidation pressure value.
- `load_directory()`: Opens a dialog for the user to select a directory.
- `check_files()`: Checks for the presence of specified files in the directory.
- `set_input_data(data)`: Receives user data as input and updates the user info.
- `extract_calibration_data(logfile_path)`: Extracts calibration data from the provided log file.
- `read_calibrated_params(file_path)`: Reads calibrated parameters from the provided file.
- `extract_data()`: Extracts data from user info, log, and calibrated_params files and displays it in the main area.
- `transmit_data()`: Transmits the data as Orange data tables and a JSON file.

### Signals:

- **Inputs**:
  - `user_data`: Accepts user data in the form of an Orange Table.
- **Outputs**:
  - `aspherix_info`: Outputs Aspherix data as an Orange Table.
  - `models_info`: Outputs models information as an Orange Table.
  - `input_parameters`: Outputs input parameters as an Orange Table.
  - `psd`: Outputs PSD data as an Orange Table.
  - `calibrated_parameter_properties`: Outputs calibrated parameter properties as an Orange Table.
  - `convergence`: Outputs convergence data as an Orange Table.
  - `calibrated_parameters`: Outputs calibrated parameters as an Orange Table.
  - `user_data`: Outputs user data as an Orange Table.
  - `calibration_case`: Outputs calibration case data as an Orange Table.
  - `json_output`: Outputs all data in JSON format.

### Usage:

1. Connect the user data from the User widget to the `OWReadAspherix` widget.
2. Input the required calibration case parameters.
3. Select a directory containing the required files using the "Browse" button.
4. Click on the "Extract Data" button to extract and display the data in the main area.
5. Load the relevant metadata JSON files per reference (experiment or relational data) that was utilized in the calibration case.
6. Click on the "Transmit Data" button to transmit the data as Orange data tables and a JSON file.