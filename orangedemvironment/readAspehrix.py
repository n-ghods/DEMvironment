import re

def extract_calibration_data(logfile_path):
    # Define regular expressions to extract relevant lines
    variable_pattern = re.compile(r'variable (\w+) string ([\d.e+-]+)')
    param_fixed_pattern = re.compile(r'param_fixed (\w+) type scalar value (\$\{\w+\})')
    param_calibration_pattern = re.compile(r'param_calibration (\w+) type (\w+) init ([\d.e+-]+) min ([\d.e+-]+) max ([\d.e+-]+)')

    # Initialize dictionaries to store extracted data
    Aspherix_calibration_software_info = {
        "version": "",
        "git commit": "",
        "attempting to": "",
        "run mode": ""
    }
    calibration_templates = {}
    models = {
        "normal_contact_model": "",
        "tangential_contact_model": "",
        "cohesion_model": "",
        "rolling_friction_model": "",
        "surface_model": "",
        "coarsegraining_val": 0
    }
    input_parameters = {}
    PSD = {
        "radii_list": [],
        "mass_fractions_list": [],
        "dispersity": 0
    }
    calibrated_parameters_property = {}

    # Function to parse values with scientific notation
    def parse_value(value_str):
        try:
            return int(value_str)
        except ValueError:
            try:
                return float(value_str)
            except ValueError:
                return value_str

    # Open and read the log file in reverse order
    with open(logfile_path, 'r') as log_file:
        lines = log_file.readlines()

        # Check the final line for "ERROR" or anything other than "calibration ended successfully"
        final_line = lines[-1].strip()
        if ("ERROR" in final_line) or ("calibration ended successfully" not in final_line):
            converged = "No"
        else:
            converged = "Yes"

        for line in reversed(lines):
            # Extract values for models using re
            run_mode_match = re.search(r'run mode (single|sequential)', line)
            if run_mode_match:
                run_mode = run_mode_match.group(1)
                Aspherix_calibration_software_info["run mode"] = run_mode
                continue
            
            # Check if the line contains 'calibration_case'
            if 'calibration_case' in line:
                # Extract the template name
                template_match = re.search(r'template (\w+)', line)
                if template_match:
                    template_name = template_match.group(1)
                    # Initialize the list of target parameters for this template
                    if template_name not in calibration_templates:
                        calibration_templates[template_name] = []

                     # Find the section of the line between 'target_param' and 'measfile'
                    target_params_section = re.search(r'target_param(.*?)measfile', line)
                    if target_params_section:
                        # Extract all words in the section
                        target_params = re.findall(r'(\w+)', target_params_section.group(1))
                        # Add the target parameters to the template entry
                        calibration_templates[template_name].extend(target_params)

                   
            model_match = re.search(r'variable (\w+) string (\S+)', line)
            if model_match:
                name, value = model_match.groups()
                if name == "coarsegraining_val":
                    models[name] = parse_value(value)
                elif name in models:
                    models[name] = value
                    continue

            variable_match = variable_pattern.search(line)
            if variable_match:
                name, value = variable_match.groups()
                if name.startswith("rp"):
                    PSD["radii_list"].append(parse_value(value))
                elif name.startswith("mf"):
                    PSD["mass_fractions_list"].append(parse_value(value))
                input_parameters[name] = parse_value(value)
                continue

            param_calibration_match = param_calibration_pattern.search(line)
            if param_calibration_match:
                name, param_type, param_init, param_min, param_max = param_calibration_match.groups()

                # Create a dictionary to store parameter details
                param_details = {
                    'type': param_type,
                    'init': parse_value(param_init),
                    'min': parse_value(param_min),
                    'max': parse_value(param_max)
                }

                # Add the parameter details to the calibrated_parameters dictionary
                calibrated_parameters_property[name] = param_details
                continue

            attempting_match = re.search(r'attempting to (run|restart) ', line)
            if attempting_match:
                latest_attempting_to = attempting_match.group(1)
                Aspherix_calibration_software_info["attempting to"] = latest_attempting_to

            git_commit_match = re.search(r'git commit (.+)', line)
            if git_commit_match:
                latest_git_commit = git_commit_match.group(1)
                Aspherix_calibration_software_info["git commit"] = latest_git_commit

            version_match = re.search(r'This is Aspherix\(R\)calibration version (.+)', line)
            if version_match:
                latest_version = version_match.group(1)
                Aspherix_calibration_software_info["version"] = latest_version

        desired_parameters = {
            "density_p", "young_w", "young_p", "poisson_p", "poisson_w",
            "rest_coef_pw", "rest_coef_pp", "fric_coef_pp", "fric_coef_pw",
            "roll_fric_pp", "roll_fric_pw"
        }
        if models["normal_contact_model"] == "hooke":
            desired_parameters.add("char_vel")

        if models["rolling_friction_model"] == "epsd":
            desired_parameters.update({
                "roll_damp_pw", "roll_damp_pp"
            })

        if models["cohesion_model"] in {"sjkr", "sjkr2"}:
            desired_parameters.update({
                "cohesion_energy_pp", "cohesion_energy_pw"
            })

        if models["cohesion_model"] == "adaptive":
            desired_parameters.update({
                "init_coh_stress_pw", "init_coh_stress_pp",
                "max_coh_stress_pp_0", "max_coh_stress_pp_min", "max_coh_stress_pp_max",
                "coh_strength_pp_0", "coh_strength_pp_min", "coh_strength_pp_max"
            })

        # Create a new dictionary with only the desired parameters
        filtered_input_parameters = {
            key: value for key, value in input_parameters.items() if key in desired_parameters
        }

        # Update the input_parameters dictionary
        input_parameters = filtered_input_parameters

    return Aspherix_calibration_software_info,calibration_templates, models, input_parameters, PSD, calibrated_parameters_property

def read_calibrated_params(file_path):
    calibrated_parameters = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines[1:]:  # Skip the header line
            parts = line.strip().split()
            if len(parts) >= 2:
                param_name = parts[0]
                param_value = float(parts[1])
                calibrated_parameters[param_name] = param_value
    return calibrated_parameters

# Example usage:
calibrated_params_file_path = "C:\\Users\\Orangepanda\\DCS-Computing\\RUN\\Aspherix6.1.0_Examples\\calibration\\hydrogel_granuDrum_drained\\calibrated_params.txt"
calibrated_parameters = read_calibrated_params(calibrated_params_file_path)
# Example usage:
logfile_path = "C:\\Users\\Orangepanda\\DCS-Computing\\RUN\\Aspherix6.1.0_Examples\\calibration\\hamburgerSand\\log_aspherix-calibration.txt"
Aspherix_info,Templates, Models_info, Input_params, PSD_info, Calibrated_params = extract_calibration_data(logfile_path)
