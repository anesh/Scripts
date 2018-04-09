import re
import paramiko
import xlsxwriter
import passhash

f1 = open('host','r')
devices = f1.readlines()

book = xlsxwriter.Workbook('AppXcel.xlsx')
sheet = book.add_worksheet('Baseline')
header_format = book.add_format({'bold':True , 'bg_color':'yellow'})
header = ["Management IP","Mode","NTP Servers","SNMP Trap","SNMP Poll","Radius Main","Radius Bak","Model","Version",
          "TPS","Concurrent Connections","RAM","Base MAC","SSL Card","Compression","Gateway","DNS",
          "World ID","Key Table","Action","Key Index","Sniffing IP","FIPS mode","Proxy Cert Table","Cert Mode"]
for col, text in enumerate(header):
  sheet.write(0, col, text, header_format)

row = 1
col = 0
pass1=passhash.passenc()

for device in devices:
  column = device.split()
  print column[0]

  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect(column[1], username='admin', password=pass1, timeout=4)
  chan = ssh.invoke_shell()

  buff = ''
  while not buff.endswith('[AppXcel]$ '):
    resp = chan.recv(9999)
    buff += resp
  
  chan.send('net management-ip get\n')
  buff = ''
  while not buff.endswith('[AppXcel]$ '):
    resp = chan.recv(9999)
    buff += resp
  mgmtrawlist=buff.splitlines()
  mgmtlist=[item.translate(None,"\xc4\xda\xc2\xbf\xc6\xcd\xd8\xb5\xb3\xc0\xc1\xd9") for item in mgmtrawlist]
  mgmtidx=[ i for i, word in enumerate(mgmtlist) if re.search(r'(?<=Lan)(.*)',word) ]
  mgmtidxs = ','.join(str(i) for i in mgmtidx)
  mgmt=int(mgmtidxs)
  print mgmtlist[mgmt]
  sheet.write(row, col,mgmtlist[mgmt])

  chan.send('system mode get\n')
  buff = ''
  while not buff.endswith('[AppXcel]$ '):
    resp = chan.recv(9999)
    buff += resp
  modelist=buff.splitlines()
  modindx=[ i for i, word in enumerate(modelist) if re.search('^Current system mode is',word,re.IGNORECASE) ]
  mod  = ','.join(str(i) for i in modindx)
  idx=int(mod)
  print modelist[idx]
  sheet.write(row, col+1,modelist[idx])

  chan.send('system ntp\n')
  buff = ''
  while not buff.endswith('[AppXcel]$ '):
    resp = chan.recv(9999)
    buff += resp
  ntplist=buff.splitlines()
  try:
    ntp1=[ i for i, word in enumerate(ntplist) if re.search('^NTP Server\(1\) Address',word,re.IGNORECASE) ]
    ntp2=[ i for i, word in enumerate(ntplist) if re.search('^NTP Server\(2\) Address',word,re.IGNORECASE) ]
    #ntp3=[ i for i, word in enumerate(ntplist) if re.search('^NTP Server Address',word,re.IGNORECASE) ]
    ntpip1  = ','.join(str(i) for i in ntp1)
    ntpip2 = ','.join(str(i) for i in ntp2)
    #ntpip3 = ','.join(str(i) for i in ntp3)
    idx1=int(ntpip1)
    idx2=int(ntpip2)
    #idx3=int(ntpip3)
    print ntplist[idx1]
    print ntplist[idx2]
    sheet.write(row, col+2,ntplist[idx1]+ntplist[idx2])
    #print ntplist[idx3]
  except ValueError:
    print "Only one NTP server Configured"
    sheet.write(row, col+2,"Only one NTP server Configured")

  chan.send('system message snmp\n')
  buff = ''
  while not buff.endswith('[AppXcel]$ '):
    resp = chan.recv(9999)
    buff += resp
  snmplist=buff.splitlines()
  try:
    #snmp1=[ i for i, word in enumerate(snmplist) if re.search('^Current SNMP traps',word,re.IGNORECASE) ]
    #snmp2=[ i for i, word in enumerate(snmplist) if re.search('^Current SNMP community',word,re.IGNORECASE) ]
    snmp3=[ i for i, word in enumerate(snmplist) if re.search('^Current SNMP traps collector',word,re.IGNORECASE) ]
    #snmpint1  = ','.join(str(i) for i in snmp1)
    #snmpint2 = ','.join(str(i) for i in snmp2)
    snmpint3 = ','.join(str(i) for i in snmp3)
    #idx3=int(snmpint1)
    #idx4=int(snmpint2)
    idx5=int(snmpint3)
    #print snmplist[idx3]
    #print snmplist[idx4]
    print snmplist[idx5]
    sheet.write(row, col+3,snmplist[idx5])
  except ValueError:
    print "SNMP trap server not configured"
    sheet.write(row, col+3,"SNMP trap server not configured")

  chan.send('system device community\n')
  buff = ''
  while not buff.endswith('[AppXcel]$ '):
    resp = chan.recv(9999)
    buff += resp
  commlist=buff.splitlines()
  commstr=[ i for i, word in enumerate(commlist) if re.search('^The current community string',word,re.IGNORECASE) ]
  comint  = ','.join(str(i) for i in commstr)
  idx5=int(comint)
  print commlist[idx5]
  sheet.write(row, col+4,commlist[idx5])  

  chan.send('system radius main-server\n')
  buff = ''
  while not buff.endswith('[AppXcel]$ '):
    resp = chan.recv(9999)
    buff += resp
  radiuslist=buff.splitlines()
  radmain=[ i for i, word in enumerate(radiuslist) if re.search('^IP',word,re.IGNORECASE) ]
  radmainint  = ','.join(str(i) for i in radmain)
  idx6=int(radmainint)
  print "Radius Main server"+radiuslist[idx6]
  sheet.write(row, col+5,radiuslist[idx6])

  chan.send('system radius backup-server\n')
  buff = ''
  while not buff.endswith('[AppXcel]$ '):
    resp = chan.recv(9999)
    buff += resp
  radbaklist=buff.splitlines()
  print radbaklist[1]
  sheet.write(row, col+6,radbaklist[1])

  chan.send('system device info\n')
  buff = ''
  while not buff.endswith('[AppXcel]$ '):
    resp = chan.recv(9999)
    buff += resp
  devinfolist=buff.splitlines()
  devmod=[ i for i, word in enumerate(devinfolist) if re.search('^Device model',word,re.IGNORECASE) ]
  softver=[ i for i, word in enumerate(devinfolist) if re.search('^Software version',word,re.IGNORECASE) ]
  tps=[ i for i, word in enumerate(devinfolist) if re.search('^TPS',word,re.IGNORECASE) ]
  conn=[ i for i, word in enumerate(devinfolist) if re.search('^Concurrent',word,re.IGNORECASE) ]
  ram=[ i for i, word in enumerate(devinfolist) if re.search('^RAM',word,re.IGNORECASE) ]
  base=[ i for i, word in enumerate(devinfolist) if re.search('^Base',word,re.IGNORECASE) ]
  ssl=[ i for i, word in enumerate(devinfolist) if re.search('^SSL Card',word,re.IGNORECASE) ]
  comp=[ i for i, word in enumerate(devinfolist) if re.search('^Compression',word,re.IGNORECASE) ]
  devint  = ','.join(str(i) for i in devmod)
  softint = ','.join(str(i) for i in softver)
  tpsint = ','.join(str(i) for i in tps)
  connint = ','.join(str(i) for i in conn)
  ramint = ','.join(str(i) for i in ram)
  baseint = ','.join(str(i) for i in base)
  sslint = ','.join(str(i) for i in ssl)
  compint = ','.join(str(i) for i in comp)
  idx7=int(devint)
  idx8=int(softint)
  idx9=int(tpsint)
  idx10=int(connint)
  idx11=int(ramint)
  idx12=int(baseint)
  idx13=int(sslint)
  idx14=int(compint)
  print devinfolist[idx7]
  sheet.write(row, col+7,devinfolist[idx7])
  print devinfolist[idx8]
  sheet.write(row, col+8,devinfolist[idx8])
  print devinfolist[idx9]
  sheet.write(row, col+9,devinfolist[idx9])
  print devinfolist[idx10]
  sheet.write(row, col+10,devinfolist[idx10])
  print devinfolist[idx11]
  sheet.write(row, col+11,devinfolist[idx11])
  print devinfolist[idx12]
  sheet.write(row, col+12,devinfolist[idx12])
  print devinfolist[idx13]
  sheet.write(row, col+13,devinfolist[idx13])
  print devinfolist[idx14]
  sheet.write(row, col+14,devinfolist[idx14])


  chan.send('net route table get defaultgw\n')
  buff = ''
  while not buff.endswith('[AppXcel]$ '):
    resp = chan.recv(9999)
    buff += resp
  gateway=buff.splitlines() 
  print gateway[4]
  sheet.write(row, col+15,gateway[4])

  chan.send('net dns table\n')
  buff = ''
  while not buff.endswith('[AppXcel]$ '):
    resp = chan.recv(9999)
    buff += resp
  dnsrawlist=buff.splitlines()
  dnslist=[item.translate(None,"\xc4\xda\xc2\xbf\xc6\xcd\xd8\xb5\xb3\xc0\xc1\xd9") for item in dnsrawlist]
  dnsidx=[ i for i, word in enumerate(dnslist) if re.search(r'(?<=primary)(.*)',word) ]
  dnsidxs = ','.join(str(i) for i in dnsidx)
  idx=int(dnsidxs)
  print "DNS:"+ dnslist[idx]
  sheet.write(row, col+16,dnslist[idx])

  chan.send('appxcel security-world get\n')
  buff = ''
  while not buff.endswith('[AppXcel]$ '):
    resp = chan.recv(9999)
    buff += resp
  seclist=buff.splitlines()
  print seclist[2]
  sheet.write(row, col+17,seclist[2])

  chan.send('appxcel key table get\n')
  buff = ''
  while not buff.endswith('[AppXcel]$ '):
    resp = chan.recv(9999)
    buff += resp
  certrawlist=buff.splitlines()
  certlist=[item.translate(None,"\xc4\xda\xc2\xbf\xc6\xcd\xd8\xb5\xb3\xc0\xc1\xd9") for item in certrawlist]
  certidx=[ i for i, word in enumerate(certlist) if re.search(r'(?<=Crt)(.*)',word) ]
  certidxs = ','.join(str(i) for i in certidx)
  idx=int(certidxs)
  print certlist[idx]
  sheet.write(row, col+18,certlist[idx])

  chan.send('appxcel server-auth-action table\n')
  buff = ''
  while not buff.endswith('[AppXcel]$ '):
    resp = chan.recv(9999)
    buff += resp
  actionrawlist=buff.splitlines()
  actionlist=[item.translate(None,"\xc4\xda\xc2\xbf\xc6\xcd\xd8\xb5\xb3\xc0\xc1\xd9") for item in actionrawlist]
  print actionlist[7]
  sheet.write(row, col+19,actionlist[7])

  chan.send('appxcel ssl-sniffing key\n')
  buff = ''
  while not buff.endswith('[AppXcel]$ '):
    resp = chan.recv(9999)
    buff += resp
  keyindex=buff.splitlines()
  print keyindex[2]
  sheet.write(row, col+20,keyindex[2])

  chan.send('appxcel ssl-sniffing ip\n')
  buff = ''
  while not buff.endswith('[AppXcel]$ '):
    resp = chan.recv(9999)
    buff += resp
  sniffrawip=buff.splitlines()
  sniffip=[item.translate(None,"\xc4\xda\xc2\xbf\xc6\xcd\xd8\xb5\xb3\xc0\xc1\xd9") for item in sniffrawip]
  print "SSL sniffing IP:"+sniffip[7]
  sheet.write(row, col+21,sniffip[7])

  chan.send('appxcel fips mode get\n')
  buff = ''
  while not buff.endswith('[AppXcel]$ '):
    resp = chan.recv(9999)
    buff += resp
  fipsmode=buff.splitlines()
  print fipsmode[2]
  sheet.write(row, col+22,fipsmode[2])
  
  chan.send('appxcel proxy certificate table get\n')
  buff = ''
  while not buff.endswith('[AppXcel]$ '):
    resp = chan.recv(9999)
    buff += resp
  proxycert=buff.splitlines()
  proxyrawcert=[item.translate(None,"\xc4\xda\xc2\xbf\xc6\xcd\xd8\xb5\xb3\xc0\xc1\xd9") for item in proxycert]
  proxycertidx=[ i for i, word in enumerate(proxyrawcert) if re.search(r'(?<=Crt)(.*)',word) ]
  proxycertidxs = ','.join(str(i) for i in proxycertidx)
  proxyidx=int(proxycertidxs)
  print proxyrawcert[proxyidx]
  sheet.write(row, col+23,proxyrawcert[proxyidx])
  
  chan.send('appxcel ssl-sniffing certificate-mode get\n')
  buff = ''
  while not buff.endswith('[AppXcel]$ '):
    resp = chan.recv(9999)
    buff += resp
  certmode=buff.splitlines()
  print certmode[2]    
  sheet.write(row, col+24,certmode[2])
 
  row += 1
  chan.close()

book.close()
  
