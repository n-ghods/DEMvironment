## Installation Guide for Add-on Package

Welcome to the Add-on Package for Orange! This guide will help you with the steps to get the add-on up and running in your Orange3 environment.

### Prerequisites:

Ensure you have the following prerequisites met before proceeding with the installation:

- **Python (>= 3.6)**: Python should be properly installed. You can download it from the [official website](https://www.python.org/downloads/).
- **Orange3**: This add-on requires Orange3 to be installed. If you haven't already, download and install Orange3 from [here](https://orange.biolab.si/download/).

### Installation Steps:

#### Step 1: **Install the package using pip**:

Pip is a package manager for Python packages. If you have Python and pip installed, you must install the add-on using the following steps/commands:

- change to the location on disk that contains the DEMvironment package (this folder contains the 'setup.py' file)
- issue the following command in a python/conda console
```bash
pip install -e .
```

#### 2. **Using Orange's Add-on manager**:

Orange comes with a built-in add-on manager. You can use it to install the add-on:

- Open Orange.
- Navigate to `Options` > `Add-ons`.
- A new window will open showing a list of available add-ons. Find `your-addon-name` in the list.
- Check the box next to `orange-demvironment`.
- Click 'OK'. The add-on will be installed, and you may need to restart Orange for the changes to take effect.

- Open Orange.
- Navigate to the canvas. If the installation was successful, you should see the new widget icons related to the add-on in the toolbox.

### Troubleshooting:

If you face any issues during the installation:

- Ensure you have all the prerequisites installed.
- Check if there's any specific error message and search for it online. The Orange community is active and might have solutions available.
- Reinstall the add-on.
- For further support or questions, contact n_ghods@ymail.com
