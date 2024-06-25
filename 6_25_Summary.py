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

def count_pings_per_timeframe(data): 
    #Get the list of headers from the dictionary
    headers = list(data.keys())

    #get time frame header & data
    time_frame_header = headers[0]
    time_frames = data[time_frame_header] 

    #determine the number of rows by checking th elength of any column list 
    num_rows = len(data[headers[0]]) if headers else 0

    ping_summary = []

    #skip the timeframe and tagid vv
    start_index = 2

    #iterate through satellite row/cols to identify which rows have more than 1 ping data 
    for i in range(num_rows): 
        time_frame = time_frames[i]
        ping_count = 0

        for header in headers[start_index:]: 
            value = data[header][i] #access value in row i 

            #check if value is an int
            if isinstance(value, int): 
                ping_count += 1
            
            elif isinstance(value,str): 
                #check if the string value represents an int. 
                try: 
                    int_value = int(value)
                    ping_count += 1

                except ValueError: 
                    pass 


        if ping_count > 1: 
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


#import file with pings (RSSI) and angles (bearings)
ping_file_path = '/Users/kaylaracelis/Downloads/T6178194B_RSSI(in).csv'   
angle_file_path = '/Users/kaylaracelis/Downloads/T6178194B_Bearing(in).csv'

output_file = '6_20Summary.txt'

# Read data from CSV to parallel arrays (row-major order)
ping_data_dict = read_csv_to_parallel_arrays(ping_file_path)
angle_data_dict = read_csv_to_parallel_arrays(angle_file_path)

# Print the data to a text file with specified formatting
print_to_text_file(ping_data_dict, angle_data_dict, output_file)

# Print summary of timeframes with 2 or more occurrences of pings to the same text file
print_ping_summary(ping_data_dict, output_file)

print(f"Data and summary printed to {output_file}")
