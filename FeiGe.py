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

        sock = socket(AF_INET, SOCK_DGRAM)
        sock.connect(('google.com', 0))
        self.local_IP = sock.getsockname()[0]
        self.hostname = gethostname()

        self.tPort = 7777
        self.uPort = 50000
        self.tcpPort = ('', self.tPort)
        self.udpPort = ('', self.uPort)
        self.bufferSize = 1024
        self.onlineUser = []


    def fileSend(self, dest, fileName):
        svrSock = socket(AF_INET, SOCK_STREAM)
        svrSock.connect((dest, self.tPort))

        print 'Preparing to send..'
        svrSock.send(fileName.split(os.path.sep)[-1])
        reply = svrSock.recv(self.bufferSize)
        if reply == 'True':

            print 'the other side has confirmed..'
            if os.name == 'nt':
                fileName = fileName.decode('utf-8').encode('936')
            print 'file name :', fileName
            print 'file size : %*.*f KBytes' % (10, 2, os.path.getsize(fileName)/1024.0)
            f = open(fileName, 'rb')
            tstart = time.time()
        
            while True:
                data = f.read(self.bufferSize)
                if not data:
                    break
                while len(data) > 0:
                    sent = svrSock.send(data)
                    data = data[sent:]

            svrSock.close()
            tend = time.time()
            print 'file has sended..'
            print 'Total time used: %*.*f s..' % (9, 5, tend - tstart)

    def send_thr(self, dest, filename):
        send_thr = mythread(self.fileSend, dest, filename)
        send_thr.setName('FileSendThread')
        send_thr.setDaemon(True)
        send_thr.start()


    def fileRec(self):

        serSock = socket(AF_INET, SOCK_STREAM)
        serSock.bind(self.tcpPort)
        serSock.listen(15)

        while True:
            cliSock, addr = serSock.accept()
            print 'connected from:', addr

            name = cliSock.recv(self.bufferSize)
            #ron = func("get a file \'%s\', receive or not?"%(name))
            #if ron:
            cliSock.send('True')
            #time.sleep(0.5)
            self.rece_thr(cliSock, name)


    def frece_thread(self):
        frece_thr = mythread(self.fileRec)
        frece_thr.setName('FileListenThread')
        frece_thr.setDaemon(True)
        frece_thr.start()


    def rece(self, cliSock, name):

        #os.chdir('/home/administrator/桌面')
        if os.name == 'nt':
            name = name.decode('utf-8'.encode('936'))
        print 'receiving file "%s"' % (name)
        tstart = time.time()
        f = open(name, 'wb')
        while True:
            data = cliSock.recv(self.bufferSize)
            if not data:
                break
            else:
                f.write(data)

        f.flush()
        f.close()
        cliSock.close()
        tend = time.time()
        print 'file has downloaded..'
        print 'Total time used: %*.*f s..' % (9, 5, tend - tstart)


    def rece_thr(self, cliSock, name):
        rece_thr = mythread(self.rece, cliSock, name)
        rece_thr.setName('FileReceiveThread')
        rece_thr.setDaemon(True)
        rece_thr.start()


    def BrcaListen(self):
        
        uSock = socket(AF_INET, SOCK_DGRAM)
        uSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        uSock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        uSock.bind(self.udpPort)
        
        while True:
            message, address = uSock.recvfrom(8192)
            uSock.sendto(self.hostname, address)
            #if receive a localhost IP, it will not send a reply.
            #if address[0] <> self.local_IP:
            try:
                if self.onlineUser.index([address[0], message]) + 1:
                    pass
            except:
                self.onlineUser.append([address[0], message])

        
    def brc_thread(self):
        brc = mythread(self.BrcaListen)
        brc.setName('BroadListenThread')
        brc.setDaemon(True)
        brc.start()


    def broadcast(self, widget=None):

        ''' send a broadcast message for renewing the list '''
        #initialize the list
        self.onlineUser = []
        dest = ("<broadcast>", self.uPort)
        time.sleep(0.2)
        self.reply_socket.sendto(self.hostname, dest)

        
    def replyReceive(self):

        self.reply_socket = socket(AF_INET, SOCK_DGRAM)
        self.reply_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.broadcast()

        while True:
            message, address = self.reply_socket.recvfrom(2048)
            #if address[0] <> self.local_IP:
            try:
                if self.onlineUser.index([address[0], message]) + 1:
                    pass
            except:
                self.onlineUser.append([address[0], message])

    
    def reply_thread(self):
        reply = mythread(self.replyReceive)
        reply.setName('ReplyThread')
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
        if t == 'fuck':
            fg.fileSend(fg.local_IP, '/windows/sda7/picture/computer/4.jpg')







