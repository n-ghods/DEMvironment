## User Widget

### Overview:

The `User` widget is designed to collect and preview user information. This information can be transmitted as a dictionary for further use.

### Features:

- Input Fields

  : Collect information about the user:

  - First Name
  - Last Name
  - Email
  - Affiliation

- **Preview Area**: View the information entered in a formatted dictionary-like style.

- **Transmit Button**: Send the collected information to the next widget as a data table.

------

## Experiment Widget

### Overview:

The `Experiment` widget is created to collect detailed experiment-related information and allows the user to connect it with the previously collected user data.

### Features:

#### 1. User Info:

- **Received Input**: This section shows the information received from the `User` widget in a formatted dictionary style.

#### 2. Experiment Info:

Allows user to input and preview:

- Name of the experimental measurement
- Measured quantities
- Measurement Device
- Methods/software for data collection
- Method for processing data
- Standards and calibration information
- Environmental/experimental conditions
- People involved with sample collection, processing, analysis, and/or submission
- Unit system

#### 3. Particle Info:

Collect information about the particles used in the experiment:

- Particle's Material
- Particle's diameter (in meters)
- Particle's shape
- Particles's density
- Media (e.g., air, water, ...)
- Link to Material Safety Data Sheet (MSDS) or more details
- Material preprocessing (if applied)

#### 4. Data Info:

Collects and previews:

- File location (either via browsing local files or by providing links)
- Number of variables (Single or Multi). If "Multi" is selected, specify the count.
- Date of data collection
- Place of data collection
- Licenses/restrictions placed on the data

### Outputs:

- **User Data**: Outputs user data as an Orange data table.
- **Experiment Data**: Outputs experiment data as an Orange data table.
- **Particle Data**: Outputs particle data as an Orange data table.
- **Data Info Data**: Outputs data info as an Orange data table.
- **All Data as Dictionary**: Outputs all the collected data as a string-formatted Python dictionary.

## Relational Data Widget

### Overview:

The `Relational Data` widget is designed to integrate and connect data from the `User` widget and provide features to input correlations from literature.

### Features:

#### 1. User Info:

- **Received Input**: This section previews the user information received from the `User` widget in a formatted dictionary style.

#### 2. Literature Correlations:

Allows the user to input details about known correlations from literature. This could include:

- Correlation name
- Variables involved
- Equation
- Source (e.g., research paper, book, URL)
- Comments or additional notes

### Outputs:

- Outputs the literature correlation data, combined with user data, for further analysis or connection with other widgets.

------

## Simulation Widget

### Overview:

The `Simulation` widget is versatile and can receive data from the `User`, `Experiment`, or `Relational Data` widgets. It provides functionalities to append data related to simulations.

### Features:

#### 1. Received Data:

- **Received Input**: Displays the data received from connected widgets (like User, Experiment, or Relational Data) in a formatted dictionary style.

#### 2. Simulation Data:

Allows the user to input and preview details about the simulation:

- Type of simulation (e.g., FEM, FDM, DEM, CFD)
- Software used
- Version of software
- Simulation parameters and settings
- Initial and boundary conditions
- Results summary
- Computational resources used (like CPU, GPU details)

### Outputs:

- **Simulation Data**: Outputs simulation details as an Orange data table or other desired format.

## Add to DB Widget

### Overview:

The `Add to DB` widget is crafted to consolidate dictionary signals from the `Experiment`, `Relational Data`, and `Simulation` widgets and persist them to a database. It integrates the incoming data, checks for duplicity, and then facilitates the saving process, ensuring a streamlined and efficient workflow for data management.

### Features:

#### 1. Received Data:

- **Received Input**: Methodically presents the data received from connected widgets (`Experiment`, `Relational Data`, `Simulation`) in a clearly formatted dictionary style.

#### 2. Database Operations:

- **Duplication Check**: Before any data is committed to the database, this widget runs an automatic check against the existing database entries to prevent redundant submissions. A feedback mechanism notifies the user if any duplicate data is detected.

- Save to Database

  : On successful validation (with no duplication), the data is saved to the database in two distinct manners:

  - **JSON File**: The complete data dictionary is serialized into a JSON format and saved as a file within the database system.
  - **Database Table**: Relevant parts of the data are tabulated and saved in structured tables in the database, making it easier for querying and data extraction operations.

#### 3. Notifications:

The widget provides real-time feedback on the status of the database operation. Users are informed if:

- Data is successfully saved.
- There are issues or errors.
- Duplicate entries are detected.

#### 4. Manual Review:

Before committing, users are given an option to review the consolidated data, ensuring that they have full control and awareness of what gets added to the database.

### Outputs:

- **Status Report**: On successful operation, a status report is generated detailing the operation's success and any other metadata. This report can be directed to other widgets or tools that might benefit from such feedback.