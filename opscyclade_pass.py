#! /usr/bin/python

#In version 1.1 interactive shell created by Anesh Kesavan

import os
import paramiko
import getpass
import xlsxwriter
import socket
import  re
import sys
import smtplib
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.MIMEText import MIMEText


username = raw_input('Enter username for login:')
def enterPassword():
  while True: # repeat forever
    password = getpass.getpass('Enter current password:')
    password_again = getpass.getpass('Confirm current password:')
    if password != password_again:
      print 'Password and confirmation do not match.Please try again!!'
    else:
      return password
password = enterPassword()

def enternewPassword():
  while True: # repeat forever
   new_password = getpass.getpass('Enter new password:')
   new_password_again = getpass.getpass('Confirm new password:')
   if new_password != new_password_again:
      print 'Password and confirmation do not match.Please try again!!'
   else:
      return new_password
new_password = enternewPassword()

recipient = raw_input('Enter your email-id where the results of the test will be mailed to you(*******) :')
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
        print column[0], column[1]
        try:
                conn=ssh.connect(column[1], username=username, password=password, timeout=4)
                if conn is None:
                    chan = ssh.invoke_shell()
                    chan.send('passwd\n')
                    buff = ''
                    while not buff.endswith('Old Password: '):
                      resp = chan.recv(9999)
                      buff += resp

                    chan.send(password+'\n')
                    buff = ''
                    while not buff.endswith('New password: '):
                      resp = chan.recv(9999)
                      buff += resp

                    chan.send(new_password+'\n')
                    buff = ''
                    while not buff.endswith('Re-enter new password: '):
                      resp = chan.recv(9999)
                      buff += resp

                    chan.send(new_password+'\n')
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

#Create Workbook instance
book = xlsxwriter.Workbook('password_change.xlsx')
sheet = book.add_worksheet('Password')
sheet.set_column(0,0,38)
sheet.set_column(1,1,38)

#Define and format header
header_format = book.add_format({'bold':True , 'bg_color':'yellow'})
header = ["Hostname", "Access Result"]
for col, text in enumerate(header):
    sheet.write(0, col, text, header_format)


# Now, let's write the contents

for row, data_in_row in enumerate(data):
    for col, text in enumerate(data_in_row):
        sheet.write(row + 1, col, text)

book.close()

# send mail to GNAM with parameters

SMTP_SERVER = 'fqdn.com'
SMTP_PORT = 587


sender = 'prod-scripting@domain.com'
password = ""
subject = ' Opsware Password change results'
message = 'Find attached the results of the script which changed the opsware password on all *** managed F5 devices'

def main():
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['To'] = recipient
    msg['From'] = sender
    part = MIMEText('text', "plain")
    part.set_payload(message)
    msg.attach(part)
    session = smtplib.SMTP(SMTP_SERVER)
    fp = open('password_change.xlsx', 'rb')
    msgq = MIMEBase('audio', 'audio')
    msgq.set_payload(fp.read())
    fp.close()
    # Encode the payload using Base64
    encoders.encode_base64(msgq)
    # Set the filename parameter
    filename='password_change.xlsx'
    msgq.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.attach(msgq)
    # Now send or store the message
    qwertyuiop = msg.as_string()
    session.sendmail(sender, recipient, qwertyuiop)

    session.quit()

if __name__ == '__main__':
    main()

print "Please check your mail for the results of the test..A mail with the subject 'Opsware Password change results' should be waiting in your inbox"
os.remove('password_change.xlsx')
