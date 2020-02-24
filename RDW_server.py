#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
import datetime
import time

from socket import *
from threading import Thread

from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr,formataddr
import smtplib

address = "192.168.1.15"
port = 54321
buffsize = 1024
Msock = socket(AF_INET,SOCK_STREAM)
Msock.bind((address,port))
Msock.listen(24)        #set max connect 24,it is enough for me
conn_list = []         #save connecting connect
conn_hist = []         #save last log for every connect
conn_dt = {}
logStorage = "C:/watermarkServer/"
acccount = "yumefx@yumefx.com"
password = "123456"   #some mail put the offer code in mail client settings , not the password, just like QQmail.
toMailAddrs = ["admin@yumefx.com","develope@yumefx.com"]
smtpServer = "smtp.yumefx.com"


def formatAddress(s):
    name,addr = parseaddr(s)
    return formataddr((Header(name,"utf-8").encode(),addr))

def sendmail(title,text):
    server = smtplib.SMTP(smtpServer,25)    #25 is default smtp port, check mail setting
    server.set_debuglevel(1)
    server.login(acccount,password)

    msg = MIMEText(text,"plain","utf-8")
    msg["Form"] = formatAddress("Watermark Service<%s>" %acccount)
    msg["Subject"] = Header(title,"utf-8").encode()

    for ta in toMailAddrs:
        msg["To"] = formatAddress("SiteGroup<%s>" % ta)
        server.sendmail(acccount,ta,msg.as_string())
    server.quit()

def tcplink(sock,addr):
    while True:
        try:
            #accept message and save
            recvData = sock.recv(buffsize).decode("utf-8")
            print(recvData,addr)
            conn_hist[conn_list.index(addr)] = recvData
            recvDatas = recvData.split("\n")
            #host + "\n" + name + "\n" + date + "\n" + state
            printLog(recvDatas[0],addr[0],recvDatas[1],recvDatas[2],recvDatas[3])
            if recvDatas[3] == "login":
                sendmail("watermark service user login:" + recvDatas[1],
                         "user login succeed,now show watermark.\nuse machine:" + recvDatas[0] + "\nuser account:" +
                         recvDatas[1] + "\nIP:" + addr[0] + "\nlogin time:" + recvDatas[2])
            else:
                sendmail("watermark service user logout:" + recvDatas[1],
                         "user logout succeed,now hide watermark.\nuse machine:" + recvDatas[0] + "\nuser account:" +
                         recvDatas[1] + "\nIP:" + addr[0] + "\nlogout time:" + recvDatas[2])
            if not recvData:
                break

        except:
            #when break connect send warning mail
            sock.close()
            print(addr,"offline")
            _index = conn_list.index(addr)
            print(conn_hist[_index])
            sendmail("watermark offline warning!","IP:" + addr[0] + "\nthe last log is:\n" + conn_hist[_index])
            conn_dt.pop(addr)
            conn_list.pop(_index)
            conn_hist.pop(_index)
            break

def printLog(host,ip,user,date,state):
    hostDir = logStorage + host + "-" + ip
    if not os.path.isdir(hostDir):
        os.makedirs(hostDir)
    logFilePath = hostDir + "/" + user + ".log"
    logfile = None
    if not os.path.isfile(logFilePath):
        logfile = open(logFilePath,"w")
    else:
        logfile = open(logFilePath,"a")
    logfile.write(date + ":" + state)
    logfile.close()

def recs():
    while True:
        clientsock,clientaddress = Msock.accept()
        if clientaddress not in conn_list:
            conn_list.append(clientaddress)
            conn_hist.append("")
            conn_dt[clientaddress] = clientsock
        print("connect from:",clientaddress)

        #start thread
        t = Thread(target=tcplink,args=(clientsock,clientaddress))
        t.start()
        tj = Thread(target=sendLog)
        tj.start()

def sendLog():
    while True:
        #send current watermark state every 4 hours
        time.sleep(14400)
        mailText = "Now there are " + str(len(conn_list)) + "client is online\nthese last log is:"
        for i in range(len(conn_list)):
            mailText += conn_list[i][0] + ": " + conn_hist[i].replace("\n","  ") + "\n"
        sendmail("watermark service current state")

if __name__  == "__main__":
    recs()









