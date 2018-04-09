#! /usr/bin/python

import os
import paramiko
import xlsxwriter
import socket
import  re
import sys
import smtplib
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.MIMEText import MIMEText


username = raw_input('Enter your nbkid:')
password = raw_input('Enter the corresponding password:')
recipient = raw_input('Enter your email-id where the results of the test will be mailed to you(*****) :')
print "Running the tests..this might take some time..Patience is a virtue.."

# Opens file in read mode
f1 = open('host','r')

# Creates list based on f1
devices = f1.readlines()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

data = []
for device in devices:
	column = device.split()
        data.append([column[0]])
        print column[0] 
        data[-1].append(column[1])
        try:
                conn=ssh.connect(column[1], username=username, password=password, timeout=4)
                if conn is None:
                    output= "Successfully Authenticated"
		    data[-1].append(output)	
                    ssh.close()
        except  paramiko.AuthenticationException:
                output = "Authentication Failed"
                data[-1].append(output)
        except  paramiko.SSHException:
                output = "Issues with SSH service"
                data[-1].append(output)
        except  socket.error, e:
                output = "Connection Error"
                data[-1].append(output)
        data[-1] = tuple(data[-1])

f1.close()
print data
#Create Workbook instance
book = xlsxwriter.Workbook('nbkidcheck_'+username+'.xlsx')
sheet = book.add_worksheet('Access')
sheet.set_column(0,0,38)
sheet.set_column(1,1,24)
sheet.set_column(2,2,28)

#Define and format header
header_format = book.add_format({'bold':True , 'bg_color':'yellow'}) 
header = ["Hostname","IP Address", "Access Result"]
for col, text in enumerate(header):
    sheet.write(0, col, text, header_format)

#success = book.add_format({'bg_color': 'green'})
#failure = book.add_format({'bg_color': 'red'})

# Now, let's write the contents

for row, data_in_row in enumerate(data):
    for col, text in enumerate(data_in_row):
        sheet.write(row + 1, col, text)

# Conditional Formatting for Data
'''
sheet.conditional_format('B1:B5000', {'type':     'cell',
                                'criteria': 'containing',
                                'value':    'Failed',
                                'format':   failure})

sheet.conditional_format('B1:B5000', {'type':     'cell',
                                'criteria': 'containing',
                                'value':    'Successfully',
                                'format':   success})
'''
book.close()

# send mail to ** with parameters

SMTP_SERVER = 'fqdn.com'
SMTP_PORT = 587


sender = 'prod-scripting@domain.com'
password = ""
subject = 'Access check results'
message = 'Find attached the results of the script which checked your ** credentials against all ** managed F5 and Bluecoat devices'

def main():
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['To'] = recipient
    msg['From'] = sender
    part = MIMEText('text', "plain")
    part.set_payload(message)
    msg.attach(part)
    session = smtplib.SMTP(SMTP_SERVER)
    fp = open('nbkidcheck_'+username+'.xlsx', 'rb')
    msgq = MIMEBase('audio', 'audio')
    msgq.set_payload(fp.read())
    fp.close()
    # Encode the payload using Base64
    encoders.encode_base64(msgq)
    # Set the filename parameter
    filename='nbkidcheck_'+username+'.xlsx'
    msgq.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.attach(msgq)
    # Now send or store the message
    qwertyuiop = msg.as_string()
    session.sendmail(sender, recipient, qwertyuiop)

    session.quit()

if __name__ == '__main__':
    main()

print "Please check your mail for the results of the test..A mail with the subject 'Access check results' should be waiting in your inbox"
os.remove('nbkidcheck_'+username+'.xlsx')
