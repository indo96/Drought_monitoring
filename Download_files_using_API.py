### DOWNLOAD FILES FROM https://aszalymonitoring.vizugy.hu/ 
###########################################################

### IMPORT NEEDED MODULES
import json
import requests
import pandas as pd
import os
    
# Define a default directory for saving files
output_directory = "C:/Users/.../Downloaded_data"

# Check if the directory exists; if not, create it
if not os.path.exists(output_directory):
    os.makedirs(output_directory, exist_ok=True)

# Create Station class
class Station:
    def __init__(self, statid, name, eovx, eovy):
        self.statid = statid
        self.name = name
        self.eovx = eovx
        self.eovy = eovy

# Create Variable class
class Variable:
    def __init__(self, name, level, unit, minfreq, computed, varid):
        self.name = name
        self.level = level
        self.unit = unit
        self.minfreq = minfreq
        self.computed = computed
        self.varid = varid     


# API endpoint URL
api_url_stations = 'https://aszalymonitoring.vizugy.hu/api.php?view=getstations' 
api_url_variables = 'https://aszalymonitoring.vizugy.hu/api.php?view=getvariables'  
api_url_values = 'https://aszalymonitoring.vizugy.hu/api.php?view=getmeas&statid={stat_id}&varid={var_id}&fromdate=2018-01-01&todate=2022-12-31'

# Make a GET request to the API
response_stations = requests.get(api_url_stations)
response_variables = requests.get(api_url_variables)

# Check if the request was successful (status code 200)
if response_variables.status_code == 200 and response_stations.status_code == 200:

    # Set the encoding of the response content to ISO-8859-1 beacuse of Hungarian letters
    response_stations.encoding = 'ISO-8859-1'
    response_variables.encoding = 'ISO-8859-1'

    # Parse the JSON response
    stations_data = json.loads(response_stations.text)
    variables_data = json.loads(response_variables.text)

    # Extract the list of variables from the API response
    stations_data = stations_data.get('entries')
    variables_data = variables_data.get('entries', [])

    # Create a list to hold the Variable objects
    stations_objects = []
    variables_objects = []

    # Iterate through the stations and create Station objects
    for stat in stations_data:
        station = Station(stat["statid"], stat["name"], stat["eovx"], stat["eovy"])
        if station.eovx is not None:
            station.eovx = int(float(station.eovx))
            station.eovy = int(float(station.eovy))
        else:
            # Handle the case where 'eovx' is missing
            # You can set a default value or take appropriate action
            station.eovx = "NA"  
            station.eovy = "NA" 

        stations_objects.append(station)
    
    # Iterate through the variables and create Variable objects
    for var in variables_data:
        name = var.get('name', '')
        level = var.get('level', '')
        unit = var.get('unit', '')
        minfreq = var.get('minfreq', '')
        computed = var.get('computed', '')
        varid = var.get('varid', '')

        variable = Variable(name, level, unit, minfreq, computed, varid)
        variable.level = variable.level.replace(" ", "")
        variables_objects.append(variable)


        if variable.varid in range(8,14):
            for station in stations_objects:
                api_url = api_url_values.format(var_id=varid, stat_id=station.statid)
                response_values = requests.get(api_url)

                # Check if the request was successful (status code 200)
                if response_values.status_code == 200:

                    response_text = response_values.text

                    # Load the JSON data
                    values_data = json.loads(response_text)

                    # Extract the first element from 'entries' (the original JSON format is not suitable for Python)
                    first_entry = values_data['entries'][0]

                    # Create a DataFrame 
                    df_values = pd.DataFrame(first_entry)

                    # Transpose the DataFrame (the rows become columns)
                    df_transposed_values = df_values.T

                    # Define the desired column order
                    desired_columns = ['date', 'value']

                    # Check if the DataFrame has the expected columns
                    if all(column in df_transposed_values.columns for column in desired_columns):

                        # If the columns exist, reorder them
                        df_transposed_values = df_transposed_values[desired_columns]

                        # Replace entire rows with NA if all values in the row are missing
                        df_transposed_values.fillna("NA", inplace=True)

                        # Save the DataFrame to a CSV file
                        output_file = os.path.join(output_directory, f"{variable.level}_{variable.name}_{station.name}_{station.eovx}_{station.eovy}.csv")
                        df_transposed_values.to_csv(output_file, index=False, float_format="%.2f", date_format="%Y-%m-%d %H:%M")

                    else:
                        print(f"DataFrame does not contain expected columns. Skipping file writing.")


    # Print stations_objects
    for station in stations_objects:
        print(f"Name: {station.name}, EOVX: {station.eovx}, EOVY: {station.eovy}")

    # Print variables_objects
    for variable in variables_objects:
        print(f"Name: {variable.name}, Level: {variable.level}, Varid: {variable.varid}")


else:
    print(f"Failed to fetch data from the API.")







    