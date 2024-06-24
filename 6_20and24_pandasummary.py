import csv
from datetime import datetime
import pytz

def read_csv_to_parallel_arrays(file_path):
    data = {}

    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        csv_reader = csv.reader(file, delimiter=',')
        
        headers = next(csv_reader)
        for header in headers:
            data[header] = []  # Initialize each column as a list
    
        for row in csv_reader:
            for header, value in zip(headers, row):
                data[header].append(value.strip())  # Append value to respective column list
    
    return data

def convert_utc_to_pacific(utc_time_str):
    if utc_time_str == 'NA':
        return 'NA'
    
    # Define UTC and Pacific time zones
    utc_zone = pytz.timezone('UTC')
    pacific_zone = pytz.timezone('US/Pacific')

    # Parse the UTC time string into a datetime object
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")

    # Set the timezone for the datetime object to UTC
    utc_time = utc_zone.localize(utc_time)

    # Convert the datetime object to Pacific time
    pacific_time = utc_time.astimezone(pacific_zone)

    # Return the Pacific time as a string in the same format
    return pacific_time.strftime("%Y-%m-%dT%H:%M:%S")

def print_to_text_file(data, output_file):
    with open(output_file, mode='w', encoding='utf-8') as file:
        # Write headers
        headers = list(data.keys())
        time = headers[0] + "Pacific"
        header_line = f"{time:<20}" + "".join(f"{header:>16}" for header in headers[1:]) + "\n"
        file.write(header_line)
        
        # Write data
        num_rows = len(data[headers[0]])
        for i in range(num_rows):
            row_values = []
            for header in headers:
                if header == headers[0]:  # Convert TimeFrame from Zulu to Pacific
                    time_frame_value = convert_utc_to_pacific(data[header][i]).ljust(20)
                    row_values.append(time_frame_value)
                else:
                    row_values.append(data[header][i].rjust(16))
            
            row_line = "".join(row_values) + "\n"
            file.write(row_line)


## doesnt work 
def count_pings_per_timeframe(data):
    time_frame_header = list(data.keys())[0]  # Assuming the first key is the time frame header
    time_frames = data[time_frame_header]     # List of time frames
    
    satellite_columns = [
        'V3023D368BAA', 'V3023D156846', 'V3023D36E6B0', 
        'V30B0154CF14', 'V3023D363087', 'V30B0154B2A1', 
        'V30B0154B2DE', 'V3023D368F92', 'V30B0154E9A4'
    ]
    
    num_rows = len(time_frames)
    ping_summary = []
    
    for row in range(num_rows):
        time_frame = time_frames[row]
        ping_count = 0
        
        for col in satellite_columns:
            value = data[col][row]  # Access the value at row index `row` in column `col`
            if value.isdigit():
                ping_count += 1
        
        if ping_count >= 2:
            ping_summary.append((time_frame, ping_count))
    
    return ping_summary


def print_ping_summary(data, output_file):
    
    # Count pings for each time frame
    ping_summary = count_pings_per_timeframe(data)
    
    # Write summary to output file
    with open(output_file, mode='a', encoding='utf-8') as file:
        file.write("\n\nPing Summary:\n")
        for time_frame, ping_count in ping_summary:
            file.write(f"{time_frame} - {ping_count} pings\n")


# Example usage
file_path = '/Users/kaylaracelis/Downloads/T6178194B_RSSI(in).csv'   # Update this path to your actual file path
output_file = '6_20Summary.txt'

# Read data from CSV to parallel arrays (row-major order)
data_dict = read_csv_to_parallel_arrays(file_path)

# Print the data to a text file with specified formatting
print_to_text_file(data_dict, output_file)

# Print summary of timeframes with 2 or more occurrences of pings to the same text file
print_ping_summary(data_dict, output_file)

print(f"Data and summary printed to {output_file}")
