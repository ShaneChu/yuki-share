# -*- coding:utf-8 -*-

import threading
import thread
import os
import SimpleHTTPServer
import socket
import time
import SocketServer


class mythread(threading.Thread):
    '''Thread Class Encapsulation'''
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


class FileSharing:
    
    def HTTPServer(self):
        if not os.path.exists('FileShare.cfg'):
            print 'config file does not exist...fail to share...'
        else:
            localName = socket.gethostname()    #obtain the localhost name

            print 'localName is :', localName
            print 'local IP is :', self.local_IP
            
            file = open('FileShare.cfg', 'r')
            directory = file.read()
            file.close()
            os.chdir(directory)     #switch to the share directory
            print 'directory after changed :', os.getcwd()
            
            '''stratup the HTTP Server'''
            handler = SimpleHTTPServer.SimpleHTTPRequestHandler
            httpd = SocketServer.TCPServer((self.local_IP, 8800), handler)
            print "HTTP server is at: ", self.local_IP, ': 8800'
            print 'Server Booting successful...'
            httpd.serve_forever()
    
    
    def HTTP_svr_Thread(self):
        HTTP_svr_Thread = mythread(self.HTTPServer)
        HTTP_svr_Thread.setDaemon(True)
        HTTP_svr_Thread.start()
        
    
    def Server(self):
        
        host = ""
        port = 50000
        self.neighbor_list = []
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        s.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
        s.bind((host,port))
        
        while 1:
            message,address = s.recvfrom(8192)
            #if receive a localhost IP, it will not add to dict or send a reply.
            if not address[0] == self.local_IP:
                dict = {}
                dict['IP'] = address
                dict['share_dir_list'] =  message
                print "Got data from", address
                
                try:
                    if self.neighbor_list.index(dict) + 1:
                        pass
                except:
                    self.neighbor_list.append(dict)
                    len = self.neighbor_list.__len__() - 1
                    print (self.neighbor_list[len])['IP'] + ':8800' + '\t\t' + \
                          (self.neighbor_list[len])['share_dir_list'] + '\n'

                s.sendto(self.directory, address)    #send a reply.

        
    def svr_thread(self):
        svr = mythread(self.Server)
        svr.setDaemon(True)
        svr.start()
        
        
    def boardcast(self):
        #send a boardcast message for renewing the list
        self.neighbor_list = []     #initialize the list
        dest = ("<broadcast>",50000)    #boardcast address
        self.reply_socket.sendto(self.directory, dest)
        print 'online users:\n'
        
        
    def replyReceive(self):
        self.reply_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.reply_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.boardcast()
        
        while 1:
            message, address = self.reply_socket.recvfrom(2048)
            dict = {}
            dict['IP'] = address
            dict['share_dir_list'] =  message
            print "Got data from",address
            print 'online users:\n'
            
            #if the host has already in the dict, then pass.
            try:
                if self.neighbor_list.index(dict) + 1:
                    pass
            except:
                self.neighbor_list.append(dict)
                len = self.neighbor_list.__len__() - 1
                print (self.neighbor_list[len])['IP'] + ':8800' + '\t\t' + \
                      (self.neighbor_list[len])['share_dir_list'] + '\n'
    
    
    def boot(self):
                    
        #get the localhost IP address throught connecting Google Server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('google.com', 0))
        self.local_IP = s.getsockname()[0]
        
        #backup the share directory through a global variable
        file = open('FileShare.cfg', 'r')
        self.directory = file.read()
        file.close()
        
        self.HTTP_svr_Thread()      #http server work thread
        self.svr_thread()           #boardcast work thread
        self.replyReceive()
        
    
    def get_neighbor_list(self):
        return self.neighbor_list
    
if __name__ == '__main__':
    t = FileSharing()
    t.boot()
    print t.get_neighbor_list()
    
    
