#! /usr/bin/python

import os
import paramiko
import xlsxwriter
import socket
from getpass import getpass
import smtplib
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.MIMEText import MIMEText
from colorama import Fore, Back, Style, init

init(autoreset=True)

username = raw_input(Fore.GREEN + 'Enter username for device login:')

def enterPassword():
  while True: 
    password = getpass(Fore.GREEN + 'Enter corresponding password:')
    password_again = getpass(Fore.GREEN + 'Confirm password:')
    if password != password_again:
      print (Fore.RED + 'Password and confirmation do not match.Please try again!!')
    else:
      return password
password = enterPassword()

recipient = raw_input(Fore.GREEN + 'Enter your email-id where the results of the test will be mailed to you(only ******) :')
print (Fore.CYAN + 'Running the script on the following devices..this might take some time..')


f1 = open('GTMhost', 'r')
f2 = open('GTMcommand', 'r')

devices = f1.readlines()
commands = f2.readlines()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

data = []
for device in devices:
    column = device.split()
    data.append([column[0]])
    print (Fore.YELLOW + column[0])
    try:
	ssh.connect(column[1], username=username, password=password, timeout=4)
        stdin, stdout, stderr = ssh.exec_command("cat /VERSION | grep Version | awk {'print $2'}")
        version = stdout.read()
        data[-1].append(version)
        base_version = version.split(".")[0]
        if '4'in base_version or '9' in base_version:
            data[-1].append("Version 4.x and 9.x is not in the purview of the Baseline Report")
            continue
	for command in commands:
	    stdin, stdout, stderr = ssh.exec_command(command)
	    data[-1].append(stdout.read())
	ssh.close()
    except  paramiko.AuthenticationException:
        data[-1].append("Authentication Failed")
    except  paramiko.SSHException:
        data[-1].append("Issues with SSH service")
    except  socket.error, e:
        data[-1].append("Connection Error")
		
f1.close()
f2.close()

#Create Workbook instance
book = xlsxwriter.Workbook('GTMcheck.xlsx')
sheet = book.add_worksheet('GTM')

#Define and format header
header_format = book.add_format({'bold':True , 'bg_color':'yellow'})
header = ["Device Name", "Version","synchronization-time-tolerance", "synchronize-zone-files",
          "heartbeat-interval", "cache-ldns-servers", "drain-persistent-requests",
          "auto-discovery","max-synchronous-monitor-requests","monitor-disabled-objects", 
          "gtm-sets-recursion", "static-persist-cidr-ipv4", "static-persist-cidr-ipv6",
          "domain-name-check", "topology-longest match"]

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
subject = 'F5 GTM Baseline Configuration Check'
message = 'Find attached the results of the script which performed the baseline Configuration check of F5 devices against standards'

def main():
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['To'] = recipient
    msg['From'] = sender
    part = MIMEText('text', "plain")
    part.set_payload(message)
    msg.attach(part)
    session = smtplib.SMTP(SMTP_SERVER)
    fp = open('GTMcheck.xlsx', 'rb')
    msgq = MIMEBase('audio', 'audio')
    msgq.set_payload(fp.read())
    fp.close()
    # Encode the payload using Base64
    encoders.encode_base64(msgq)
    # Set the filename parameter
    filename='GTMcheck.xlsx'
    msgq.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.attach(msgq)
    # Now send or store the message
    qwertyuiop = msg.as_string()
    session.sendmail(sender, recipient, qwertyuiop)

    session.quit()

if __name__ == '__main__':
    main()

print (Fore.GREEN + 'Please check your mail for the results of the baseline check...A mail with the \
subject ***F5 GTM Baseline Configuration Check*** should be waiting in your inbox')
os.remove('GTMcheck.xlsx')
