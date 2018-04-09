#! /usr/bin/python

import os
import paramiko
import xlsxwriter
import socket
import re
import sys
import time


username = raw_input('Enter username for device login:')
password = raw_input('Enter the corresponding password:')
print "Ahhhh ......"

# Opens file in read mode
f1 = open('device.txt','r')


# Creates list based on f1
devices = f1.readlines()
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
data = []

for device in devices:
    column = device.split()
    data.append([column[0]])
    data[-1].append(column[1])
    print column[0]
    ssh.connect(column[1], username=username, password=password)
    remote_conn = ssh.invoke_shell()
    output = remote_conn.recv(1000)
    remote_conn.send("ssh sccp")
    remote_conn.send("\n")
    remote_conn.send("cat /etc/config/eth0.conf | grep address")
    remote_conn.send("\n")
    time.sleep(2)
    output = remote_conn.recv(5000)
	match=re.search(r'(?<=address=)(\d+(\.\d+){3})',output)
	regex= match.group()
	data[-1].append(regex)
	
	
    
        
   
 #data is of datastructure List of List to serve as input for xlsxwriter
    
f1.close()
ssh.close()

#Create Workbook instance
book = xlsxwriter.Workbook('aom.xlsx')
sheet = book.add_worksheet(column[0])


#Define and format header
header_format = book.add_format({'bold':True , 'bg_color':'yellow'})
header = ["Hostname","IPaddress","AOM"]
for col, text in enumerate(header):
    sheet.write(0, col, text, header_format)



# Now, let's write the contents
for row, data_in_row in enumerate(data):
    for col, text in enumerate(data_in_row):
        sheet.write(row + 1, col, text)


book.close()

print "Data Generated"


