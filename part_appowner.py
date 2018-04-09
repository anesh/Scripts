import bigsuds
import xlsxwriter
import socket

f1 = open('devices.txt', 'r')
devices = f1.readlines()
book = xlsxwriter.Workbook('appowner.xlsx')

for device in devices:
  row=0
  col=0
  column = device.split()
  name=column[0].strip("fqdn.com")
  sheet = book.add_worksheet(name)
  print device
  b = bigsuds.BIGIP(hostname = column[1],username = 'admin', password = 'password',)
  partlist=b.Management.Partition.get_partition_list()
  for part in partlist:
    pname= part['partition_name']
    partcount=len(partlist)
    print pname
    b.Management.Partition.set_active_partition(pname)
    pools=b.LocalLB.Pool.get_list()
    
    for pool in pools:
      poolmembers=b.LocalLB.PoolMember.get_monitor_status([pool])
      for poolmember in poolmembers:
        for status in poolmember:
          row=row+1
          x=status['member']['address']
          try:  
            fqdn=socket.gethostbyaddr(x)
          except socket.error:
            print fqdn
          y=status['member']['port']
          z= str(x)+":"+str(y)
          sheet.write(row , col, pool)
          sheet.write(row,col+1,x)
          sheet.write(row,col+2,fqdn[0])   

book.close()
