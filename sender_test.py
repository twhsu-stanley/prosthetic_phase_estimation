def graph(elapsed_time, 
          transmit1, transmit1_2, ylabel1, ylabelU1=None,
		  transmit2=None, transmit2_2=None, ylabel2=None, ylabelU2=None,
		  transmit3=None, transmit3_2=None, ylabel3=None, ylabelU3=None, 
		  transmit4=None, transmit4_2=None, ylabel4=None, ylabelU4=None):
	import socket
	import struct

	UDP_IP = "35.3.40.105"	## Change to IP address you are streaming data to
	
	# elapsed time and data streams
	UDP_PORT0 = 5012
	UDP_PORT1 = 5013
	UDP_PORT2 = 5014
	UDP_PORT3 = 5015
	UDP_PORT4 = 5016

	### additional data streams ###
	UDP_PORT1_2 = 5025
	UDP_PORT2_2 = 5026
	UDP_PORT3_2 = 5027
	UDP_PORT4_2 = 5028
	###############################

	# y labels
	UDP_PORTY1 = 5017
	UDP_PORTY2 = 5018
	UDP_PORTY3 = 5019
	UDP_PORTY4 = 5020
	
	# y labels' units => legend
	UDP_PORTU1 = 5021
	UDP_PORTU2 = 5022
	UDP_PORTU3 = 5023
	UDP_PORTU4 = 5024

	sock = socket.socket(socket.AF_INET, # Internet
						 socket.SOCK_DGRAM) # UDP

	data0 =struct.pack('d', elapsed_time)
	sock.sendto(data0, (UDP_IP, UDP_PORT0))

	data1 =struct.pack('d', transmit1)
	sock.sendto(data1, (UDP_IP, UDP_PORT1))
	sock.sendto(ylabel1.encode(), (UDP_IP, UDP_PORTY1))
	sock.sendto(ylabelU1.encode(), (UDP_IP, UDP_PORTU1))
	##### additional data streams ##########################
	data1_2 =struct.pack('d', transmit1_2)
	sock.sendto(data1_2, (UDP_IP, UDP_PORT1_2))
	#######################################################
	
	if transmit2 is not None:
		data2 =struct.pack('d',transmit2)
		sock.sendto(data2, (UDP_IP, UDP_PORT2))
		sock.sendto(ylabel2.encode(), (UDP_IP, UDP_PORTY2))
		sock.sendto(ylabelU2.encode(), (UDP_IP, UDP_PORTU2))
	##### additional data streams ##########################
	if transmit2_2 is not None:
		data2_2 =struct.pack('d', transmit2_2)
		sock.sendto(data2_2, (UDP_IP, UDP_PORT2_2))
	#########################################################
	
	if transmit3 is not None:
		data3 =struct.pack('d',transmit3)
		sock.sendto(data3, (UDP_IP, UDP_PORT3))
		sock.sendto(ylabel3.encode(), (UDP_IP, UDP_PORTY3))
		sock.sendto(ylabelU3.encode(), (UDP_IP, UDP_PORTU3))
	##### additional data streams ##########################
	if transmit3_2 is not None:
		data3_2 =struct.pack('d', transmit3_2)
		sock.sendto(data3_2, (UDP_IP, UDP_PORT3_2))
	#########################################################
	
	if transmit4 is not None:
		data4 =struct.pack('d',transmit4)
		sock.sendto(data4, (UDP_IP, UDP_PORT4))
		sock.sendto(ylabel4.encode(), (UDP_IP, UDP_PORTY4))
		sock.sendto(ylabelU4.encode(), (UDP_IP, UDP_PORTU4))
	##### additional data streams ##########################
	if transmit4_2 is not None:
		data4_2 =struct.pack('d', transmit4_2)
		sock.sendto(data4_2, (UDP_IP, UDP_PORT4_2))
	#########################################################