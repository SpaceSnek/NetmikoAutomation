from netmiko import Netmiko
from getpass import getpass


password = getpass()
cisco_ios = {
    'host': '10.1.2.1',
    'username': 'admin',
    'password': password,
    'device_type': 'cisco_ios'
}
cisco_nxos = {
    'host': 'host',
    'username': 'user',
    'password':'pass',
    'device_type': 'cisco_nxos'
}
arista_eos = {
    'host': 'host',
    'username': 'user',
    'password': 'password',
    'device_type': 'arista_eos'
}

for device in (cisco_ios, cisco_nxos, arista_eos):
    net_conn = Netmiko(**device)
    output = net_conn.send_command('show ip arp')
    print(output)
