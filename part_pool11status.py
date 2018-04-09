import bigsuds
import csv

device=raw_input('Enter Device :')

outputFile = open(device+'-post.txt', 'w+')
#outputWriter = csv.writer(outputFile)
b = bigsuds.BIGIP(hostname = device,username = 'admin', password = 'password',)
partlist=b.Management.Partition.get_partition_list()
for part in partlist:
  pname= part['partition_name']
  partcount=len(partlist) 
  print >>outputFile,"*****"+pname+"****" 
  b.Management.Partition.set_active_partition(pname)
  pools=b.LocalLB.Pool.get_list()
  virtuals=b.LocalLB.VirtualServer.get_list()
  virtualcount=len(virtuals)
  poolcount=len(pools)
  print >>outputFile,"Total Pool Count:"+ str(poolcount)
  print >>outputFile,"Total Virtual Count"+ str(virtualcount)
  statcount=0

  for pool in pools:
    rmpool=pool.replace("/"+pname+"/","")
    try:
      print pool
      poolmembers=b.LocalLB.PoolMember.get_monitor_status([pool])
    except Exception, e:
      poolmem11=b.LocalLB.Pool.get_member_v2([pool])
      status11=b.LocalLB.Pool.get_member_monitor_status([pool],poolmem11)
      for statusc in status11:
        statx=statusc
      inc=0  
      rmpx=rmpool 
      for p11 in poolmem11:
        for p11v in p11:
          sant= p11v['address'].replace("/Common/","")
          portx= p11v['port']
          addcomb=str(sant)+":"+str(portx)
          print >>outputFile,rmpx,addcomb,statx[inc]
          if statx[inc]=="MONITOR_STATUS_UP":
            statcount=statcount+1     
          inc=inc+1
    else:
      for poolmember in poolmembers:
        for status in poolmember:
          x=status['member']['address']
          y=status['member']['port']
          z= str(x)+":"+str(y)
          monstat= status['monitor_status']
          if monstat == "MONITOR_STATUS_UP":
            statcount=statcount+1
          print >>outputFile,rmpool,z,monstat

  print >>outputFile,"Total Pool Members UP:"+str(statcount)

print >>outputFile,"Total Partitions:"+str(partcount) 
