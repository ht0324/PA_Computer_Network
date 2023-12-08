import os
import pandas as pd
import matplotlib.pyplot as plt
import re

def compile_data(directory_path, experiment, time):
    """Compiles data from all log files in the given directory into a single DataFrame."""
    compiled_data = []
    filename_pattern = re.compile(rf'{experiment}_{time}_iperf_h\d+\.log')  # Updated regex pattern

    for filename in sorted(os.listdir(directory_path)):
        if filename_pattern.match(filename):
            file_path = os.path.join(directory_path, filename)
            test_label = re.search(r'h\d+', filename).group()
            with open(file_path, 'r') as file:
                for line in file:
                    if 'sec' in line:
                        parts = line.split()
                        end_time = float(parts[2].split('-')[1])

                        # Transfer unit conversion
                        transfer, transfer_unit = parts[4], parts[5]
                        if transfer_unit == "KBytes":
                            transfer = float(transfer) / 1024  # Convert KBytes to MBytes
                        else:
                            transfer = float(transfer)

                        # Bandwidth unit conversion
                        bandwidth, bandwidth_unit = parts[6], parts[7]
                        if bandwidth_unit == "Kbits/sec":
                            bandwidth = float(bandwidth) / 1000  # Convert Kbits/sec to Mbits/sec
                        else:
                            bandwidth = float(bandwidth)

                        compiled_data.append([test_label, end_time, transfer, bandwidth])
    
    return pd.DataFrame(compiled_data, columns=['Test', 'Time', 'Transfer', 'Bandwidth'])

def generate_test_labels(input_value):
    """Generates a list of test labels based on the input value (single number or range)."""
    if '-' in input_value:
        start, end = map(int, input_value.split('-'))
        return [f'h{i}' for i in range(start, end + 1)]
    else:
        return [f'h{int(input_value)}']

def plot_transfer(data, input_value):
    """Plots transfer data for specified tests."""
    plt.figure(figsize=(12, 6))
    test_labels = generate_test_labels(input_value)

    for test_label in test_labels:
        test_data = data[data['Test'] == test_label]
        if not test_data.empty:
            plt.plot(test_data['Time'], test_data['Transfer'], marker='o', linestyle='-', label=test_label)

    plt.title('TCP Host Transfer Over Time for Specified Tests')
    plt.xlabel('Time (sec)')
    plt.ylabel('Transfer (MBytes)')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_bandwidth(data, input_value):
    """Plots bandwidth data for specified tests."""
    plt.figure(figsize=(12, 6))
    test_labels = generate_test_labels(input_value)

    for test_label in test_labels:
        test_data = data[data['Test'] == test_label]
        if not test_data.empty:
            plt.plot(test_data['Time'], test_data['Bandwidth'], marker='o', linestyle='-', label=test_label)

    plt.title('TCP Host Bandwidth Over Time for Specified Tests')
    plt.xlabel('Time (sec)')
    plt.ylabel('Bandwidth (Mbits/sec)')
    plt.legend()
    plt.grid(True)
    plt.show()

def calculate_link_utilization(data, total_bandwidth):
    """Calculates link utilization based on the provided data and total link bandwidth."""
    # Grouping data by time and summing bandwidths
    utilization = data.groupby('Time')['Bandwidth'].sum() / total_bandwidth
    # if the sum of bandwidths is greater than the total link bandwidth, set it to 1
    utilization[utilization > 1] = 1
    # convert to percentage
    return utilization * 100

def plot_link_utilization(data, total_bandwidth):
    """Plots the link utilization over time."""
    utilization = calculate_link_utilization(data, total_bandwidth)

    plt.figure(figsize=(12, 6))
    utilization.plot(marker='o', linestyle='-')

    # print the average link utilization
    print(f"Average link utilization: {utilization.mean()}%")
    
    plt.title('Link Utilization Over Time')
    plt.xlabel('Time (sec)')
    plt.ylabel('Link Utilization (%)')
    plt.grid(True)
    plt.show()

def calculate_jains_fairness_index(data):
    """Calculates Jain's Fairness Index for each time point in the provided data."""
    fairness_indices = {}

    for time in data['Time'].unique():
        time_data = data[data['Time'] == time]
        bandwidths = time_data['Bandwidth'].values
        sum_of_bandwidths = sum(bandwidths)
        sum_of_squares = sum(bandwidth ** 2 for bandwidth in bandwidths)
        n = len(bandwidths)

        if n > 0 and sum_of_squares > 0:
            fairness_index = (sum_of_bandwidths ** 2) / (n * sum_of_squares)
        else:
            fairness_index = 0

        fairness_indices[time] = fairness_index

    return fairness_indices

def plot_jains_fairness_index(data):
    """Plots Jain's Fairness Index over time."""
    fairness_indices = calculate_jains_fairness_index(data)

    # print average fairness index
    print(f"Average fairness index: {sum(fairness_indices.values()) / len(fairness_indices)}")

    plt.figure(figsize=(12, 6))
    plt.plot(list(fairness_indices.keys()), list(fairness_indices.values()), marker='o', linestyle='-')
    
    plt.title("Jain's Fairness Index Over Time")
    plt.xlabel('Time (sec)')
    plt.ylabel('Jain\'s Fairness Index')
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    # Replace the path below with the path to your log file directory
    # log_files_directory = '/path/to/your/log/files'
    log_files_directory = os.getcwd() 
    # experiment = "HighDelay"
    # experiment = "HighBandwidth"
    experiment = "OneToFifty"
    time = 60
    all_data = compile_data(log_files_directory, experiment, time)

    # remove the data after 40 seconds
    all_data = all_data[all_data['Time'] <= time]
    
    # plot_transfer(all_data, '2-51')
    plot_transfer(all_data, '2-11')
    plot_bandwidth(all_data, '2-11')

    plot_link_utilization(all_data, 1000)  # MUST CHANGE
    plot_jains_fairness_index(all_data)