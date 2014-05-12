from csvthings import import_csv_to_list
from csvthings import export_list_to_csv

# Import CSVs to list.
airlines = import_csv_to_list('airlines_raw.csv', headers = True, astuple = True)
aircraft = import_csv_to_list('aircraft_raw.csv', headers = True, astuple = True)

# Remove duplicate rows.
def remove_duplicates(data):
    data = set(data)
    data = list(data)
    return(data)

airlines = remove_duplicates(airlines)
aircraft = remove_duplicates(aircraft)

# Remove Regionnair observations. Not unique by name.
def remove_regionnair(data):
    newdata = []
    for i in range(len(data)):
        if('Regionnair' not in data[i]):
            newdata.append(data[i])
    return(newdata)

airlines = remove_regionnair(airlines)
aircraft = remove_regionnair(aircraft)

# Convert to list of lists from list of tuples for validate_status function.
def convert_to_list(data):
    newlist = [list(e) for e in data]
    return(newlist)

airlines = convert_to_list(airlines)
aircraft = convert_to_list(aircraft)

# Fix bad statuses in aircraft.csv.
def validate_status(data):
    valid_status = ["Active", "Scrapped", "Written off", "Stored", "On order"]
    for i in range(len(data)):
        if(data[i][8] not in valid_status):
            data[i][8] = "Unknown"
    return(data)

aircraft = validate_status(aircraft)

# Export cleaned data to CSV.
export_list_to_csv('airlines_clean.csv', airlines, headers = ["airline", "country", "status"])
export_list_to_csv('aircraft_clean.csv', aircraft, headers = ["msn", "model", "series", "airline", "ff_day", "ff_month", "ff_year", "registration", "status"])

# Remove raw datasets.
# os.remove('airlines_raw.csv')
# os.remove('aircraft_raw.csv')