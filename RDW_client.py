#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import tkinter
import tkinter.messagebox
import win32api,win32con,pywintypes
from datetime import datetime
from getpass import getuser
from socket import *
from threading import Thread

def checkRemote(user):
    usersLog = os.popen("quser")
    userlist = usersLog.read().split("\n")
    del userlist[0]
    del userlist[-1]
    for ul in userlist:
        if (">" + user) == ul[:len(user) + 1]:
            userInfo = ul.split(" ")
            userInfo = [i for i in userInfo if i != ""]
            if "rdp-tcp" in userInfo[1]:
                return True
    return False

def getQueueText(text):
    space, str1, str2 = 70,"",""
    for i in range(5):
        str1 += text + " "* space
    str2 = " " * space +str1 + "\n\n\n\n"
    str1 += "\n\n\n\n"
    return (str1 + str2) * 10

class watermark(tkinter.Tk):
    procHide = False
    host = gethostname()
    ip = "192.168.1.15"
    port = "54321"
    conn = None
    company = "yumefx.com"

    def __init__(self,*args,**kwargs):
        super().__init__()
        self.text = tkinter.StringVar()
        self.text.set(getQueueText(self.company))

        #connect to server
        connThread = Thread(target = self.linkServer,args=(self.ip,self.port))
        connThread.start()

        #sent message that this service online
        self.trySendMsg(getuser(),datetime.now(),"add")
        self.run()

    def trySendMsg(self,name,date,state):
        sendThread = Thread(target=self.sendMsg,args=(name,date,state))
        sendThread.start()

    def sendMsg(self,name,date,state):
        #if send failed,try 3 times
        for i in range(3):
            try:
                self.conn.send(self.host + "\n" + name + "\n" + str(date) + "\n" + state)
                return True
            except:
                pass
            time.sleep(0.5)

        #when all 3 times failed,print log to localpath.
        logFileDir = "C:/watermark/" + self.host
        logFilePath = logFileDir + "/" + name + "log"
        logFile = None
        if not os.path.isdir(logFileDir):
            os.makedirs(logFileDir)
        if not os.path.isfile(logFilePath):
            logFile = open(logFilePath,"w")
        else:
            logFile = open(logFilePath,"a")
        logFile.write(str(date) + ":" + state)
        logFile.close()

    def linkServer(self,IP,Port):
        buffsize = 1024
        self.conn = socket(AF_INET,SOCK_STREAM)
        try:
            self.conn.connect((IP,Port))
        except:
            #this can show error window,but this service need be quiet for user,so comment it.
            #and if link failed,save log to local path(in def sendMsg).
            #tkinter.messagebox.showerror("Error","Can not link to the server,check that service.")
            self.conn = 2

    def refresh(self):
        currentUser = getuser()

        #hide watermark when no remote user
        if (not checkRemote(currentUser)) and (not self.procHide):
            self.withdraw()
            self.procHide = True
            self.trySendMsg(currentUser,datetime.now(),"logout")
        #show watermark when user remote link
        elif checkRemote(currentUser) and self.procHide:
            #change watermark content ,add the user name
            self.text.set(getQueueText(self.company + "-" + currentUser))
            self.update()
            self.deiconify()
            self.procHide = False
            self.trySendMsg(currentUser,datetime.now(),"login")
        #refresh every 0.5s
        self.after(500,self.refresh)

    def run(self):
        #actually this can put in def refresh,to get the remote desktop size
        #and i just set to 4000
        #what? you have a 8k screen,nevermind
        width = 4000 #win32api.GetSystemMetrics(0)
        height = 4000 #win32api.GetSystemMetrics(1)
        self.overrideredirect(True)                      #hide the window bounding box
        self.geometry("+0+0")                             #set window position or size
        self.lift()                                      #set window on top
        self.attributes("-alpha",0.6)                    #make watermark transparent
        self.wm_attributes("-topmost",True)              #always set window on top
        self.wm_attributes("-disabled",True)             #disable window,so mouse can not click
        self.wm_attributes("-transparentcolor","white")   #window background set white and transparent
        hwindow = pywintypes.HANDLE(int(self.frame(),16))
        exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
        win32api.SetWindowLong(hwindow,win32con.GWL_EXSTYLE,exStyle)
        #set text / font / text color / background color
        label = tkinter.Label(textvariable=self.text,font=("Times New Roman","40"),fg="#d5d5d5",bg="white")
        label.pack()
        self.withdraw()
        self.procHide = True
        self.refresh()
        self.mainloop()

if __name__ == "__main__":
    WM = watermark()















