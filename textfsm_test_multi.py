# Importing Netmiko modules
from netmiko import Netmiko
from netmiko.ssh_exception import NetMikoAuthenticationException, NetMikoTimeoutException
from getpass import getpass
from pprint import pprint
import signal, os

from queue import Queue
import threading

file = input('enter name for file (do not include extension): ')
file = file+'.txt'
print('file will be named: '+file +'!')
fileedit = open(file, 'w+')

password = getpass()

ip_addrs_file = open('hostnames.txt')
ip_addrs = ip_addrs_file.read().splitlines()

print(ip_addrs)

num_threads = 8
enclosure_queue = Queue()
print_lock = threading.Lock()

command = "show ver"


# Function used in threads to connect to devices, passing in the thread # and queue
def deviceconnector(i, q):
    while True:
        ip = q.get()
        device_dict = {
            'host': ip,
            'username': 'admin',
            'password': password,
            'device_type': 'cisco_nxos'
        }
        try:
            net_connect = Netmiko(**device_dict)
        except NetMikoTimeoutException:
            with print_lock:
                print("\n{}: ERROR: Connection to {} timed-out.\n".format(i, ip))
            q.task_done()
            continue
        except NetMikoAuthenticationException:
            with print_lock:
                print("\n{}: ERROR: Authentication failed for {}. Stopping script. \n".format(i, ip))
            q.task_done()
            os.kill(os.getpid(), signal.SIGUSR1)

        output = net_connect.send_command(command, use_textfsm=True)
        with print_lock:
            pprint(f"{output[0]['hostname']}: {output[0]['version']}")
            fileedit.write(f"{output[0]['hostname']}: {output[0]['version']}")
        net_connect.disconnect
        q.task_done()

def main():
    for i in range(num_threads):
        thread = threading.Thread(target=deviceconnector, args=(i, enclosure_queue,))
        thread.setDaemon(True)
        thread.start()

    for ip_addr in ip_addrs:
        enclosure_queue.put(ip_addr)

    enclosure_queue.join()
    fileedit.close()
    print("*** Script complete")

if __name__ == '__main__':
    main()