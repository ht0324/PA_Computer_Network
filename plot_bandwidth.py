import os
import pandas as pd
import matplotlib.pyplot as plt
import re

def read_log_file(file_path):
    """Reads a log file and returns a DataFrame with time and bandwidth data."""
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            if 'sec' in line:
                parts = line.split()
                end_time = float(parts[2].split('-')[1])
                bandwidth = float(parts[6])
                data.append([end_time, bandwidth])
    return pd.DataFrame(data, columns=['Time', 'Bandwidth'])

def plot_all_logs(directory_path):
    """Plots bandwidth data from all log files in the given directory."""
    plt.figure(figsize=(12, 6))

    for filename in sorted(os.listdir(directory_path)):
        if re.match(r'iperf_h\d+\.log', filename):
            file_path = os.path.join(directory_path, filename)
            df = read_log_file(file_path)
            # Extracting the 'hX' part from the filename
            test_label = re.search(r'h\d+', filename).group()
            plt.plot(df['Time'], df['Bandwidth'], marker='o', linestyle='-', label=test_label)

    plt.title('TCP Host Bandwidth Over Time for Multiple Tests')
    plt.xlabel('Time (sec)')
    plt.ylabel('Bandwidth (Mbits/sec)')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    # Replace the path below with the path to your log file directory
    # log_files_directory = '/path/to/your/log/files'
    log_files_directory = os.getcwd() 
    plot_all_logs(log_files_directory)
