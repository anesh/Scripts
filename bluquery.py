import sqlite3
import ast
import sys
import re
from netaddr import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--group", help="Provide AD group to match within policy")
parser.add_argument("--fqdn", help="Provide fqdn to match within policy")
parser.add_argument("--url", help="Provide url to match within policy")
parser.add_argument("--ip", help="Provide IP Address to match within policy")
args = parser.parse_args()
fqdn=args.group
url=args.fqdn
url2=args.url
ip=args.ip

#fqdn = sys.argv[1]
conn = sqlite3.connect('example.db')
c = conn.cursor()
customlist=[]

def customquery(customlist):
    mylist3=[]
    mylist50=[]
    for catlist4 in customlist:
        t50=('%'+catlist4+'%',)
        c.execute('select * from catcombs where objects2 like ?',t50)
        for cur11 in c:
            dumb20=str(cur11)
            match20=re.search(r'(?<=\'name\':\s\')(.*)(?=\'})',dumb20)
            regex30=match20.group()
            print regex30

    t50=('%'+regex30+'%',)
    c.execute('select * from combobj1 where objects2 like ?',t50)
    for cur1 in c:
        dumb2=str(cur1)
        print dumb2
        match21=re.search(r'(?<=\'name\':\s\')(.*)(?=\',)',dumb2)
        regex31=match21.group()
        mylist50.append(regex31)

    for objlist in customlist:
        t5=('%'+objlist+'%',)
        c.execute('select * from combobj1 where objects2 like ?',t5)
        for cur1 in c:
            dumb2=str(cur1)
            print dumb2
            match2=re.search(r'(?<=\'name\':\s\')(.*)(?=\',)',dumb2)
            regex3=match2.group()
            mylist3.append(regex3)
    
    print mylist3

    mylist5=[]
    for objlist2 in customlist:
        print objlist2
        t7=('%'+objlist2+'%',)
        c.execute('select * from combobj2 where objects2 like ?',t7)
        for cur11 in c:
            dumb12=str(cur11)
            print dumb12
            match3=re.search(r'(?<=\'name\':\s\')(.*)(?=\',)',dumb12)
            regex4=match3.group()
            mylist5.append(regex4)

    for layerlist in mylist3:
        t6=('%'+layerlist+'%',)
        print t6
        c.execute('select * from layers where objects2 like ?',t6)
        for cur2 in c:
            print cur2

    for layerlist2 in mylist5:
        t8=('%'+layerlist2+'%',)
        c.execute('select * from layers where objects2 like ?',t8)
        for cur22 in c:
            print cur22

    for layerlist3 in mylist50:
        t80=('%'+layerlist3+'%',)
        c.execute('select * from layers where objects2 like ?',t80)
        for cur221 in c:
            print cur221


if args.fqdn:
    t2=('%'+url+'%',)
    mylist=[]
    for row2 in c.execute('select * from categories where objects like ?',t2):
        for tuples in row2:
            x=str(tuples)
            print x
            match = re.search(r'(?<=:).*', x)  #the look-behind regex
            regex= match.group()
            mylist.append(regex)
    customquery(mylist)

        
if args.group:
    t3=('%'+fqdn+'%',)
    mylist4=[]
    c.execute('select * from groupobj where objects like ?',t3)
    for grplist in c:
        willwork=grplist[0]
        dichold=ast.literal_eval(willwork)
        result2=dichold['name']
        mylist4.append(result2)
    customquery(mylist4)

if args.url:
    t=('%'+url2+'%',)
    print t
    for row in c.execute('select * from url where objects like ?',t):
        check=row[0]
        test =ast.literal_eval(check)
        result1= test['name']
        t20=('%\''+result1+'\'%',)
        print t20
        c.execute('select * from combobj1 where objects2 like ?',t20)
        for cur1 in c:
            dumb2=str(cur1)
            print dumb2
            match2=re.search(r'(?<=\'name\':\s\')(.*)(?=\',)',dumb2)
            regex3=match2.group()
            print regex3

        t21=('%'+regex3+'%',)
        print t21
        c.execute('select * from layers where objects2 like ?',t21)
        for cur2 in c:
            print cur2

if args.ip:
    t30=('%'+ip+'%',)
    c.execute('select * from ipobject where objects like ?',t30)
    if c.fetchone():
        for row in c.execute('select * from ipobject where objects like ?',t30):
            check=row[0]
            test =ast.literal_eval(check)
            result2=test['name']
            result4=test['value']
            print result2
            print result4
            print ip
            t40=('%'+result2+'%',)
            c.execute('select * from combobj1 where objects2 like ?',t40)
            for cur1 in c:
                dumb2=str(cur1)
                print dumb2
                match2=re.search(r'(?<=\'name\':\s\')(.*)(?=\',)',dumb2)
                regex3=match2.group()
                print regex3

            t21=('%'+regex3+'%',)
            print t21
            c.execute('select * from layers where objects2 like ?',t21)
            for cur2 in c:
                print cur2
    else:
        c.execute('select * from  ipobject2')
        for ipsubnets in c:
            ipsubnet=ipsubnets[0]
            ipdict=ast.literal_eval(ipsubnet)
            ipobj= ipdict['name']
            ipsub= ipdict['value']
            if IPAddress(ip) in IPNetwork(ipsub):
                print ipsub+""+ipobj
                t400=('%\''+ipobj+'\'%',)
                print t400
                c.execute('select * from combobj1 where objects2 like ?',t400)
                for cur100 in c:
                    dumb200=str(cur100)
                    print dumb200
                    match200=re.search(r'(?<=\'name\':\s\')(.*)(?=\',)',dumb200)
                    regex300=match200.group()
                    print regex300

                t210=('%'+regex300+'%',)
                print t210
                c.execute('select * from layers where objects2 like ?',t210)
                for cur200 in c:
                    print cur200


