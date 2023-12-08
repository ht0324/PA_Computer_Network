from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import OVSKernelSwitch
from mininet.cli import CLI
from mininet.node import Host
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import threading

class HighDelay(Topo):
    def build(self):
        switch = self.addSwitch('s1', cls=OVSKernelSwitch, failMode='standalone')

        server = self.addHost('h{}'.format(1), cls=Host, defaultRoute=None)
        self.addLink(server, switch, cls=TCLink, bw=500, delay='2ms', loss=0.1)
        
        for i in range(2, 52):
            host = self.addHost('h{}'.format(i), cls=Host, defaultRoute=None)
            self.addLink(host, switch, cls=TCLink, bw=10, delay='0.5ms', loss=0.1)


# def start_iperf_client(host, server_ip, duration, log_file):
#     # Output in CSV format and include timestamps
#     cmd = f"iperf -c {server_ip} -i 1 -t {duration} -y C > {log_file} 2>&1 &"
#     print(f"Running on {host.name}: {cmd}")  # Debugging statement
#     host.cmd(cmd)

def start_iperf_client(host, server_ip, duration, log_file):
    cmd = f"iperf -c {server_ip} -i 1 -t {duration} > {log_file} 2>&1 &"
    print(f"Running on {host.name}: {cmd}")  # Debugging statement
    host.cmd(cmd)

def start_test_command(host, log_file):
    cmd = f"echo 'Testing host {host.name}' > {log_file}"
    host.cmd(cmd)

def main():
    topo = HighDelay()
    net = Mininet(topo=topo, autoSetMacs=True, build=False, ipBase="10.0.0.0/24")

    net.start()

    experiment = "HighDelay"
    time = 60

    # Assuming h1 is the server
    server = net.getNodeByName('h1')
    server_ip = server.IP()

    # Starting the server
    server.cmd('iperf -s &')

    # Starting iperf clients in parallel
    for i in range(2, 52):  # Hosts from h2 to h51
        client = net.getNodeByName(f'h{i}')
        log_file = f"{experiment}_{time}_iperf_h{i}.log"
        # start_test_command(client, log_file)
        start_iperf_client(client, server_ip, time, log_file)

    CLI(net)

    # Killing iperf on all hosts
    for host in net.hosts:
        host.cmd('kill %iperf')

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    main()
