import bigsuds

device=raw_input('Enter Device :')

outputFile = open(device+'-gtmpre.txt', 'w+')
#outputWriter = csv.writer(outputFile)
b = bigsuds.BIGIP(hostname = device,username = 'admin', password = 'password',)
pools=b.LocalLB.Pool.get_list()
wideips=b.GlobalLB.WideIP.get_list()
wideipcount=len(wideips)
print >>outputFile,"Total Wideips"+str(wideipcount)


for wideip in wideips:
  wideipstatus=b.GlobalLB.WideIP.get_object_status([wideip])
  wideippools=b.GlobalLB.WideIP.get_wideip_pool([wideip])
  for status in wideipstatus:

    statd= status['status_description']
    print >> outputFile,statd
    #print statd
  for wideippool in wideippools:
    for pool in wideippool:
      poolname= pool['pool_name']
      poolsstat= b.GlobalLB.Pool.get_object_status([poolname])
      poolmembers= b.GlobalLB.Pool.get_member([poolname])
      for poolstat in poolsstat:
        #print poolstat['status_description']
        print >> outputFile,poolstat['status_description'] 
      for poolmember in poolmembers:
        for mem in poolmember:
          x= mem['member']['address']
          y=mem['member']['port']
          z= str(x)+":"+str(y)
          print >> outputFile,z
'''iiiprint >>outputFile,"Total Pool Count:"+ str(poolcount)
print >>outputFile,"Total Virtual Count"+ str(virtualcount)
statcount=0


for pool in pools:
  poolmembers=b.LocalLB.PoolMember.get_monitor_status([pool])
  for poolmember in poolmembers:
    for status in poolmember:
      x=status['member']['address']
      y=status['member']['port']
      z= str(x)+":"+str(y)
      monstat= status['monitor_status']
      if monstat == "MONITOR_STATUS_UP":
        statcount=statcount+1
      #outputWriter.writerow([pool,z,monstat])
      print >>outputFile,pool,z,monstat

print >>outputFile,"Total Pool Members UP:"+str(statcount)'''
