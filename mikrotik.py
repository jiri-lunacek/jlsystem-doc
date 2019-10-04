from string import Template
from socket import inet_aton, inet_ntoa

def iptoint(ip):
    return int(inet_aton(ip).encode('hex'),16)

def inttoip(ip):
    return inet_ntoa(hex(ip)[2:].decode('hex'))

config_template='''
/interface bridge
add fast-forward=no mtu=1500 name=lan protocol-mode=none
/interface ethernet
set [ find default-name=ether3 ] master-port=ether2
set [ find default-name=ether4 ] master-port=ether2
/interface ovpn-client
add certificate=cert2 cipher=aes256 connect-to=${vpn_server_ip} mode=ethernet name=jlsystem user=dummy
/ip neighbor discovery
set jlsystem discover=no
/ip ipsec proposal
set [ find default=yes ] enc-algorithms=3des
/ip pool
add name=pool1 ranges=${lan_pool_from}-${lan_pool_to}
/ip dhcp-server
add address-pool=pool1 authoritative=after-2sec-delay disabled=no interface=\
    lan name=server1
/port
set 0 baud-rate=2400 parity=even
/queue interface
set jlsystem queue=default
/system logging action
set 0 memory-lines=100
set 1 disk-lines-per-file=100
/interface bridge port
add bridge=lan interface=ether2
/ip address
add address=${lan_ip}/${lan_netmask} interface=lan
/ip dhcp-client
add dhcp-options=hostname,clientid disabled=no interface=ether1 use-peer-ntp=\
    no
/ip dhcp-server network
add address=${lan_ip_net}/${lan_netmask} gateway=${lan_ip} netmask=${lan_netmask}
/ip dns
set max-udp-packet-size=512 servers=10.178.104.1,8.8.8.8
/ip service
set telnet disabled=yes
set ftp disabled=yes
set www disabled=yes
set api disabled=yes
/port remote-access
add port=serial0 protocol=raw tcp-port=10000
/routing prefix-lists
add action=discard chain=intra invert-match=yes prefix=172.16.0.0/12
/routing rip
set redistribute-connected=yes redistribute-static=yes
/routing rip interface
add interface=jlsystem out-prefix-list=intra
/routing rip neighbor
add address=10.178.104.1
/system clock
set time-zone-autodetect=no time-zone-name=Europe/Prague
/system console
set [ find ] disabled=yes
/system identity
set name=mikrotik20
/system ntp client
set enabled=yes primary-ntp=213.203.238.86 secondary-ntp=85.125.61.2
/system routerboard settings
set baud-rate=off
'''

GLOBAL_IP_BASE = iptoint('172.16.1.0')
LAN_NETMASK = 29
LAN_NETLEN = 1<<(32-LAN_NETMASK)


if __name__ == "__main__":
	import sys
	CONFIG_ID = int(sys.argv[1])

	# get ca
	# get cert
	# /root/easyrsa-test/pkitool --batch test

	ip_base = GLOBAL_IP_BASE + (LAN_NETLEN*(CONFIG_ID))
	conf = Template(config_template)
	print conf.substitute(
		{
			'vpn_server_ip': '130.193.10.1',
			'lan_ip': inttoip(ip_base+LAN_NETLEN-2),
			'lan_netmask': '29',
			'lan_ip_net': inttoip(ip_base),
			'lan_pool_from': inttoip(ip_base+1),
			'lan_pool_to': inttoip(ip_base+LAN_NETLEN-3),
		}
	)
