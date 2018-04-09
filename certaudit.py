#Developed by Anesh Kesavan

import bigsuds
import getpass
import collections
import hashlib
import sqlite3
import xlsxwriter
import os
import smtplib
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.MIMEText import MIMEText

def docertcompare(deviceip,username,password,devicename):
  try:
    foldercert=[]
    bindcertlist=[]
    finalcert=[]
    b = bigsuds.BIGIP(hostname = deviceip,username=username,password=password)
    listofcertdetails= b.Management.KeyCertificate.get_certificate_list('MANAGEMENT_MODE_DEFAULT')
    for certfilename in listofcertdetails:
      rmfolder=certfilename['file_name']
      x=rmfolder.replace("/config/ssl/ssl.crt/","")
      foldercert.append(x)
    #print foldercert

    sslprofiles=b.LocalLB.ProfileClientSSL.get_list()
    sslcerts= b.LocalLB.ProfileClientSSL.get_certificate_file(sslprofiles)
    for sslcert in  sslcerts:
      y= sslcert['value']
      bindcertlist.append(y)
    #print bindcertlist


    comparelist=set(foldercert).intersection(bindcertlist)

    for z in comparelist:
      finalcert.append(z)

    sortlist= sorted(finalcert)
    concatlist="".join(sortlist)
    certhash=hashlib.md5(concatlist).hexdigest()
    print certhash


    selfips=b.Networking.SelfIP.get_list()
    statefloatingselfips=b.Networking.SelfIP.get_floating_state(selfips)
    map_by_state = collections.defaultdict(list)
    for state, address in zip (statefloatingselfips, selfips):
      map_by_state[state].append(address)

    floatlist=map_by_state['STATE_ENABLED']
    if not floatlist:
      return

    sortiplist= sorted(floatlist)
    ipconcatlist="".join(sortiplist)
    iphash=hashlib.md5(ipconcatlist).hexdigest()
    print iphash
    c.execute('INSERT INTO sslobjs VALUES (?,?,?,?)',(devicename,deviceip,certhash,iphash))
  except Exception, e:
    print e
    
def peergroup():
  c.execute('''create table peers as select t1.device,t1.ip,t1.sslhash,t1.floathash from sslobjs t1
            where exists (select * from sslobjs t2 where t1.floathash=t2.floathash group by floathash having count(floathash)>1)''')

def createxcel():
  book = xlsxwriter.Workbook('certaudit.xlsx')
  sheet = book.add_worksheet('Peers')

  header_format = book.add_format({'bold':True , 'bg_color':'yellow'})
  header = ["Peer1","Peer2","SSL Match"]
  for col, text in enumerate(header):
    sheet.write(0, col, text, header_format)


  devicelist=[]
  sslhashlist=[]

  for rows in c.execute('select device from peers order by floathash'):
    for cur1 in rows:
      dumb2=str(cur1)
      devicelist.append(dumb2)

  for rows2 in c.execute('select sslhash from peers order by floathash'):
    for cur2 in rows2:
      dumb3=str(cur2)
      sslhashlist.append(dumb3)

  row = 1
  col = 0
  deviceodd=devicelist[1::2]
  deviceeven=devicelist[0::2]

  sslodd=sslhashlist[1::2]
  ssleven=sslhashlist[0::2]

  if len(deviceodd)==len(deviceeven):
    print "lets identify peers"
    i=0
    for deviceodds in deviceodd:
      if ssleven[i]== sslodd[i]:
        sheet.write(row, col,deviceeven[i])
        sheet.write(row, col+1,deviceodd[i])
        sheet.write(row, col+2,"YES")
        print deviceeven[i]+""+deviceodd[i]+"YES"
        i+=1
        row += 1
      else:
        sheet.write(row, col,deviceeven[i])
        sheet.write(row, col+1,deviceodd[i])
        sheet.write(row, col+2,"NO")
        print deviceeven[i]+""+deviceodd[i]+"NO"
        i+=1
        row += 1
  else:
    print "There is a rotten apple"

  book.close()


username = raw_input('Enter username:')
password = getpass.getpass()
recipient = raw_input('Enter your email-id where the results of the test will be mailed to you(******) :')
f1 = open('device.txt','r')
conn = sqlite3.connect('sslcert.db')
c = conn.cursor()
c.execute('''CREATE TABLE sslobjs (device text,ip text,sslhash text,floathash text)''')
devices = f1.readlines()
for device in devices:
  column = device.split()
  print column[0]
  deviceip=column[1]
  devicename=column[0]
  docertcompare(deviceip,username,password,devicename)
  conn.commit()

peergroup()
createxcel()
if os.path.exists("sslcert.db"):
  os.remove("sslcert.db")

SMTP_SERVER = 'fqdn.com'
SMTP_PORT = 587


sender = 'prod-scripting@domain.com'
password = ""
subject = 'F5 Cert Audit'
message = 'Find attached the results of the script which performed the F5 Cert Audit  on all ** managed F5 devices'

def main():
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['To'] = recipient
    msg['From'] = sender
    part = MIMEText('text', "plain")
    part.set_payload(message)
    msg.attach(part)
    session = smtplib.SMTP(SMTP_SERVER)
    fp = open('certaudit.xlsx', 'rb')
    msgq = MIMEBase('audio', 'audio')
    msgq.set_payload(fp.read())
    fp.close()
    # Encode the payload using Base64
    encoders.encode_base64(msgq)
    # Set the filename parameter
    filename='certaudit.xlsx'
    msgq.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.attach(msgq)
    # Now send or store the message
    qwertyuiop = msg.as_string()
    session.sendmail(sender, recipient, qwertyuiop)

    session.quit()

if __name__ == '__main__':
    main()

print "Please check your mail for the results of the test..A mail with the subject 'F5 Cert Audit' should be waiting in your inbox"

