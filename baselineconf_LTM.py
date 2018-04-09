#! /usr/bin/python

import os
import paramiko
import bigsuds
from getpass import getpass
import xlsxwriter
import socket
import itertools
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

recipient = raw_input(Fore.GREEN + 'Enter your email-id where the results of the test will be mailed to you(*****) :')
print (Fore.CYAN + 'Running the script on the following devices..this might take some time..')


f1 = open('LTMhost', 'r')

devices = f1.readlines()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
data = []
irule_prof = ['http2https', 'SNAT2VIP', 'forwardingl4', 'tcp_nagledisable', 'http-xff', 'bac_oneconnect', 
               'bac_oneconnect_32mask', 'src_ip_1800', 'src_ip_3600', 'bac_ssl', 'bac_ssl_1800', 'bac_cookie' ]
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
        stdin, stdout, stderr = ssh.exec_command("less /config/startup | grep 'vodadmin >>' | awk {'print $3'}")
        data[-1].append(stdout.read())
        stdin, stdout, stderr = ssh.exec_command("tmsh list sys | grep -i auto-detect | awk '{ print $2}'")
        data[-1].append(stdout.read())
        
        b = bigsuds.BIGIP(hostname = column[1], username=username, password=password)
        vlans = b.Networking.VLAN.get_list() 
        data_vlans = [vlan for vlan in vlans if 'failover' not in vlan]
        fail_vlans = [vlan for vlan in vlans if 'failover' in vlan]
        data_vlans_failsafe = list(itertools.chain.from_iterable([b.Networking.VLAN.get_failsafe_state([vlan]) for vlan in data_vlans]))
        fail_vlans_failsafe = list(itertools.chain.from_iterable([b.Networking.VLAN.get_failsafe_state([vlan]) for vlan in fail_vlans]))
        if "STATE_DISABLED" in data_vlans_failsafe:
            data[-1].append("Disabled")
        else:
            data[-1].append("Enabled")
        if "STATE_ENABLED" in fail_vlans_failsafe:
            data[-1].append("Enabled")
        else:
            data[-1].append("Disabled")
        trunks = b.Networking.Trunk.get_list()
        if not  trunks:
            data[-1].append("No Trunks found")
        else:
            lacp_status = b.Networking.Trunk.get_active_lacp_state(trunks)
            if "STATE_DISABLED" in lacp_status:
                data[-1].append("Disabled")
            else:
                data[-1].append("Enabled")
        b.Management.KeyCertificate.certificate_check_validity("MANAGEMENT_MODE_WEBSERVER", ["server"], [1])
        db = b.Management.DBVariable.query(['SystemAuth.source', 'Failover.ForceActive', 'Failover.ForceStandby'])
        for item in db:
            data[-1].append(item['value'])
        cert_exp = b.Management.KeyCertificate.certificate_check_validity("MANAGEMENT_MODE_WEBSERVER", ["server"], [1])
        data[-1].append(cert_exp[0][18:])
        device_irule_prof =(b.LocalLB.ProfileTCP.get_list() + b.LocalLB.Rule.get_list() + b.LocalLB.ProfileOneConnect.get_list() + 
                            b.LocalLB.ProfilePersistence.get_list() + b.LocalLB.ProfileFastL4.get_list() + b.LocalLB.ProfileHttp.get_list())
        for item in irule_prof:
            if any(item in word for word in device_irule_prof):
                data[-1].append("YES")
            else:
                data[-1].append("NO")
    except  paramiko.AuthenticationException:
        data[-1].append("Authentication Failed")
    except  paramiko.SSHException:
        data[-1].append("Issues with SSH service")
    except  socket.error, e:
        data[-1].append("Connection Error")
    except Exception, e:
        print e
        data[-1].append("Bigsuds Exception")
		
f1.close()


#Create Workbook instance
book = xlsxwriter.Workbook('LTMcheck.xlsx')
sheet = book.add_worksheet('LTM')

#Define and format header
header_format = book.add_format({'bold':True , 'bg_color':'yellow'})
header = ['Device Name','Version', 'Vodadmin in Startup Script','Config Sync Autodetect',
          'Failsafe in Data VLANS', 'Failsafe in Failover VLANS','LACPD in Trunks', 'System Auth Source', 'Force Active Status',
          'Force Standby Status','Device Cert Validity', 'http2https irule presence', 'SNAT2VIPirule presence', 
          'forwardingl4 profile presence', 'tcp_nagledisable profile presence', 'http-xff profile presence', 
          'bac_oneconnect profile presence', 'bac_oneconnect_32mask profile presence', 'src_ip_1800 profile presence', 
          'src_ip_3600 profile presence', 'bac_ssl profile presence', 'bac_ssl_1800 profile presence', 'bac_cookie profile presence']
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
subject = 'F5 LTM Baseline Configuration Check'
message = 'Find attached the results of the script which performed the baseline\
Configuration check of F5 devices against standards'

def main():
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['To'] = recipient
    msg['From'] = sender
    part = MIMEText('text', "plain")
    part.set_payload(message)
    msg.attach(part)
    session = smtplib.SMTP(SMTP_SERVER)
    fp = open('LTMcheck.xlsx', 'rb')
    msgq = MIMEBase('audio', 'audio')
    msgq.set_payload(fp.read())
    fp.close()
    # Encode the payload using Base64
    encoders.encode_base64(msgq)
    # Set the filename parameter
    filename='LTMcheck.xlsx'
    msgq.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.attach(msgq)
    # Now send or store the message
    qwertyuiop = msg.as_string()
    session.sendmail(sender, recipient, qwertyuiop)

    session.quit()

if __name__ == '__main__':
    main()

print 'A mail with the subject F5 LTM Baseline Configuration Check should be waiting in your inbox'
#os.remove('LTMcheck.xlsx')

