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
from Orange.data import Table, Domain, StringVariable
import json

def dict_to_orange_table(data_dict):
    """Converts a dictionary to an Orange data table."""
    
    # Flatten the dictionary by converting nested dictionaries to JSON strings
    flat_dict = {}
    for key, value in data_dict.items():
        if isinstance(value, dict):
            # Convert nested dictionaries to a JSON string
            flat_dict[key] = json.dumps(value, indent=None)
        else:
            flat_dict[key] = value

    # Create domain with flat structure
    domain = Domain([], [], metas=[StringVariable(str(key)) for key in flat_dict.keys()])
    data = [[flat_dict[key] for key in flat_dict.keys()]]
    
    return Table.from_list(domain, data)

def format_dict_as_text(data_dict,title):
    """Formats the dictionary as colored and formatted HTML string."""
    
    entries = [f'<font color="blue">"{key}"</font>: <font color="green">"{value}"</font>' for key, value in data_dict.items() if value]
    return f'<b>{title}</b><br/>{ "{" }<br/>' + ',<br/>'.join(entries) + '<br/>{ "}" }'

def orange_table_to_dict(table: Table) -> dict:
    """
    Convert an Orange data table to a dictionary.
    
    Parameters:
        table (Table): Orange data table.
        
    Returns:
        dict: Dictionary representation of the data table.
    """
    # Extracting meta attribute names
    metas = [meta.name for meta in table.domain.metas]
    
    # Extracting data from the table
    data_dict = {}
    for row in table:
        for meta, value in zip(metas, row.metas):
            data_dict[meta] = str(value)
    
    return data_dict