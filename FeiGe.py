#! usr/bin/python
# -*- coding:utf-8 -*-
# Filename: FeiGe.py


import re
import os
import sys
import time
import thread
import threading
import webbrowser
import SocketServer
from socket import *


class mythread(threading.Thread):
    
    def __init__(self, func, *args, **kwargs):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.res = None

    def run(self):
            if 'name' in self.kwargs:
                print 'thread `%s` starting ...' % self.kwargs['name']
                self.kwargs.pop('name')
            self.res = apply(self.func, self.args, self.kwargs)

    def get_result(self):
        return self.res


class FeiGe():

    def __init__(self):

        self.software = 'FeiGe'
        self.author = 'Shane Chu'
        self.version = 1.0

        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(('google.com', 0))
        self.local_IP = s.getsockname()[0]
        self.tPort = 7777
        self.uPort = 50000
        self.tcpPort = (self.local_IP, self.tPort)
        self.udpPort = (self.local_IP, self.uPort)
        self.bufferSize = 1024
        self.onlineUser = []


    def fileSend(self, dest, fileName):

        svrSock.connect((dest, self.tPort))
        f = open(fileName, 'rb')
        while True:
            data = f.read(self.bufferSize)
            if not data:
                break
            while len(data) > 0:
                sent = svrSock.send(data)
                data = data[sent:]

        svrSock.close()
        print 'file has sended...'


    def fileRec(self):

        serSock = socket(AF_INET, SOCK_STREAM)
        serSock.bind(self.tcpPort)
        serSock.listen(15)

        while True:
            cliSock, addr = serSock.accept()
            print '...connected from:', addr
            #judge = raw_input("Do you want get the file?(y/n):")
            #if judge == 'y':
            time.sleep(0.5)
            self.rece_thr(cliSock)


    def frece_thread(self):
        frece_thr = mythread(self.fileRec)
        frece_thr.setDaemon(True)
        frece_thr.start()


    def rece(self, cliSock):

        f = open('ahane.jpg', 'wb')
        while True:
            data = cliSock.recv(self.bufferSize)
            if not data:
                break
            else:
                f.write(data)

        f.flush()
        f.close()
        cliSock.close()
        print 'file has downloaded...'


    def rece_thr(self, cliSock):
        rece_thr = mythread(self.rece, cliSock)
        rece_thr.setDaemon(True)
        rece_thr.start()
        rece_thr.join()


    def BrcaListen(self):
        
        uSock = socket(AF_INET, SOCK_DGRAM)
        uSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        uSock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        uSock.bind(self.udpPort)
        
        while 1:
            message, address = uSock.recvfrom(8192)
            #if receive a localhost IP, it will not send a reply.
            if not address[0] == self.local_IP:
                print "Got data from", address

                try:
                    if self.onlineUser.index(address) + 1:
                        pass
                except:
                    self.onlineUser.append(address)
                    s.sendto('Hi', address)

        
    def brc_thread(self):
        brc = mythread(self.BrcaListen)
        brc.setDaemon(True)
        brc.start()


    def broadcast(self, widget=None):

        ''' send a broadcast message for renewing the list '''

        #initialize the list
        #self.onlineUser = []
        self.neighbor_list = ['192.168.1.101', '172.16.1.10', '10.1.1.1']

        dest = ("<broadcast>", self.uPort)
        self.reply_socket.sendto('Hi', dest)
        
        
    def replyReceive(self):
        
        self.reply_socket = socket(AF_INET, SOCK_DGRAM)
        self.reply_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.broadcast()
        
        while 1:
            message, address = self.reply_socket.recvfrom(2048)

            if not address[0] == self.local_IP:
                print "Got data from", address

                try:
                    if self.onlineUser.index(address) + 1:
                        pass
                except:
                    self.onlineUser.append(address)

    
    def reply_thread(self):
        reply = mythread(self.replyReceive)
        reply.setDaemon(True)
        reply.start()


if __name__ == '__main__':

    fg = FeiGe()
    fg.frece_thread()
    fg.brc_thread()
    fg.reply_thread()

    print fg.onlineUser

    while True:
        t = raw_input('>')
        if t == '1':
            fg.fileSend(fg.local_IP, '/windows/sda7/picture/computer/4.jpg')






