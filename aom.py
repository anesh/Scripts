#Developed by Anesh Kesavan
#! /usr/bin/python

import os
import paramiko
import xlsxwriter
import socket
import re
import getpass
import sys
import time


username = raw_input('Enter username for device login:')
password = getpass.getpass()
print "......"

# Opens file in read mode
f1 = open('device.txt','r')


# Creates list based on f1
devices = f1.readlines()
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
data = []
output1=""

def portcheck(x):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((x,22))
    sock.close()
    return result    

for device in devices:
    column = device.split()
    data.append([column[0]])
    data[-1].append(column[1])
    print column[0]
    try:
        ssh.connect(column[1], username=username, password=password,timeout=5)
    except socket.error, e:
        output = "Socket error"
        data[-1].append(output)
        continue
    except paramiko.AuthenticationException:
        output = "Authentication Failed"
        data[-1].append(output)
        continue
    remote_conn = ssh.invoke_shell()
    remote_conn.send("ssh sccp\n")
    time.sleep(4)
    output1=remote_conn.recv(10240)
    if "Welcome to the F5 Networks AOM" not in output1:
        data[-1].append("AOM OUT of Service")
        continue
    if "root@sccp's password:" in output1:
        data[-1].append("host/aom mismatch")
        continue
    else:
        remote_conn.send("cat /etc/config/eth0.conf | grep address")
        remote_conn.send("\n")
        time.sleep(2)
        output = remote_conn.recv(5000)
        if "No such file or directory" in output:
            data[-1].append("Not configured")
            continue
        else:
            match=re.search(r'(?<=address=)(\d+(\.\d+){3})',output)
            regex= match.group()
            data[-1].append(regex)
            print regex
            check=portcheck(regex)
            if check == 0:
                data[-1].append("YES")
            else:
                data[-1].append("NO")	
    
            ssh.close()
   
 #data is of datastructure List of List to serve as input for xlsxwriter
    
f1.close()

#Create Workbook instance
book = xlsxwriter.Workbook('aom.xlsx')
sheet = book.add_worksheet(column[0])


#Define and format header
header_format = book.add_format({'bold':True , 'bg_color':'yellow'})
header = ["Hostname","IPaddress","AOM IP","SSH Access"]
for col, text in enumerate(header):
    sheet.write(0, col, text, header_format)



# Now, let's write the contents
for row, data_in_row in enumerate(data):
    for col, text in enumerate(data_in_row):
        sheet.write(row + 1, col, text)


book.close()

print "Data Generated"


