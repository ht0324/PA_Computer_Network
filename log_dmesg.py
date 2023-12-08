import re
import subprocess
from collections import defaultdict
import matplotlib.pyplot as plt

def get_dmesg_output():
    """Execute the dmesg command and return its output."""
    try:
        result = subprocess.run(['sudo', 'dmesg'], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing dmesg: {e}")
        return ""
def parse_dmesg_output(dmesg_output):
    """Parse the dmesg output and extract the desired data, including average RTT."""
    pattern = r"\[\s*(\d+\.\d+)\] SRC IP: (\d+), DST IP: \d+, tp->snd_cwnd is (\d+), RTT is (\d+) microseconds"
    data = defaultdict(list)
    avg_rtts = {}

    for line in dmesg_output.splitlines():
        match = re.search(pattern, line)
        if match:
            timestamp = match.group(1)
            src_ip = match.group(2)
            cwnd = match.group(3)
            rtt = int(match.group(4))
            data[src_ip].append({'timestamp': float(timestamp), 'cwnd': int(cwnd), 'rtt': rtt})

    # Calculate average RTT
    for src_ip, values in data.items():
        total_rtt = sum(entry['rtt'] for entry in values)
        avg_rtts[src_ip] = total_rtt / len(values)

    return data, avg_rtts

# Use this function to get both parsed data and average RTTs
dmesg_output = get_dmesg_output()
parsed_data, average_rtts = parse_dmesg_output(dmesg_output)

# Display average RTTs in sorted order of SRC IP
for src_ip in sorted(average_rtts, key=int):
    avg_rtt = average_rtts[src_ip]
    print(f"Average RTT for SRC IP {src_ip}: {avg_rtt} microseconds")




def plot_rtt_over_time(data):
    """Plots the RTT of each source IP over time."""
    plt.figure(figsize=(10, 6))

    for src_ip, values in data.items():
        times = [entry['timestamp'] for entry in values]
        rtts = [entry['rtt'] for entry in values]
        plt.plot(times, rtts, label=f"SRC IP: {src_ip}", marker='o')

    plt.xlabel('Time (s)')
    plt.ylabel('RTT (microseconds)')
    plt.title('RTT vs Time for Each Source IP')
    plt.legend()
    plt.grid(True)
    plt.show()

# Example usage
# Assuming 'parsed_data' is the data obtained from the previous function
plot_rtt_over_time(parsed_data)
