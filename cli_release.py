#!/usr/bin/python
# -*- coding:utf-8 -*-
#Filename: cli_release.py


import re
import os, sys
import time
import socket
import thread
import threading
import webbrowser
import SocketServer
import SimpleHTTPServer

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
    
class fileShare:

    def __init__(self):

        self.localName = socket.gethostname()
        #get the localhost IP address throught connecting Google Server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('google.com', 0))
        self.local_IP = s.getsockname()[0]
        self.neighbor_list = []
        
        cur = os.path.dirname(os.path.realpath(__file__))
        self.directory = os.path.dirname(os.path.dirname(cur))
        

    def HTTPServer(self):
        try:
            '''Share the current directory, start the http server'''
            os.chdir(self.directory)     #switch to the share directory
            handler = SimpleHTTPServer.SimpleHTTPRequestHandler
            httpd = SocketServer.TCPServer((self.local_IP, 8800), handler)
            print '\tService start successfully...'
            print "\thttp Server URL: http://" + self.local_IP + ':8800'
            httpd.serve_forever()
        except:
            print '\tError : The service couldnot startup twice.'
    
    
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
                dict['IP'] = address[0]
                dict['share_dir_list'] =  message
                print "Got data from", address
                
                #if the host has already in the dict, then pass.
                try:
                    if self.neighbor_list.index(dict) + 1:
                        pass
                except:
                    self.neighbor_list.append(dict)
                    #len = self.neighbor_list.__len__() - 1      #add the last online user 
                    #print (self.neighbor_list[len])['IP'] + ':8800' + '\t\t' + (self.neighbor_list[len])['share_dir_list']
                
                s.sendto(self.directory, address)    #send a reply.

        
    def svr_thread(self):
        svr = mythread(self.Server)
        svr.setDaemon(True)
        svr.start()
        
        
    def boardcast(self, widget=None):
        #send a boardcast message for renewing the list
        self.neighbor_list = []     #initialize the list
        #self.neighbor_list = [{'192.168.1.102':'/windows/sda5'}, {'192.168.1.103':'/windows/sda7'}]
        dest = ("<broadcast>",50000)    #boardcast address
        self.reply_socket.sendto(self.directory, dest)
        
        
    def replyReceive(self):
        
        self.reply_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.reply_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.boardcast()
        
        while 1:
            message, address = self.reply_socket.recvfrom(2048)
            dict = {}
            dict['IP'] = address[0]
            dict['share_dir_list'] =  message
            #print "Got data from",address
            
            try:
                if self.neighbor_list.index(dict) + 1:
                    pass
            except:
                self.neighbor_list.append(dict)
                #len = self.neighbor_list.__len__() - 1
                #print  (self.neighbor_list[len])['IP'] + ':8800' + '\t\t' + (self.neighbor_list[len])['share_dir_list']
    
    def reply_thread(self):
        reply = mythread(self.replyReceive)
        reply.setDaemon(True)
        reply.start()
    
    
    def main(self):

        try:
	        while 1:
	            str = raw_input('Yuki-Share>')
	            if str == 'help':
	                print 'yuki-share.py : the command_line release of the Yuki-Share system\n'
	                print 'Usage:\n\tYuki-Share> [options]'
	                print 'Options: '
	                print '\thelp     --get more help about Yuki-Share'
	                print '\tinfo     --show the host information'
	                print '\tstart    --start the share service'
	                print '\tisstart  --check out whether the sevice was start or not'
	                print '\tlist     --print the online users and their sharing'
	                print '\topen     --open a page for browsing the neighbor\'s sharing file'
	                print '\t         --Usage: open [IP Address]\n\t         --For example: open 192.168.1.100'
	                print '\texit     --exit'
	                print ''
	            elif str == 'info':
	                print '\thost Name:', self.localName
	                print '\toperate system:', os.sys.platform
	                print '\tlocalhost IP:', self.local_IP
	                print '\tlocalhost Share Directory:', self.directory
	            elif str == 'start':
	                self.HTTP_svr_Thread()
	                self.svr_thread()
	                self.reply_thread()
	                time.sleep(0.1)
	            elif str == 'isstart':
	                #the file shouldn't exist since the current dir has changed
	                if not os.path.exists('cli_release.py'):
	                    print '\tService has been started'
	                else:
	                    print '\tService has not been started'
	            elif str == 'list':
	                try:
	                    self.boardcast()
	                except:
	                    print 'Error: Your program has not been started'
	                    continue
	                time.sleep(1)
	                if self.neighbor_list == []:
	                    print '\tResult: There is no any other users online now.'
	                else:
	                    print '\t  LAN Host' + '\t\t' + '  Share Dir'
	                    for user in self.neighbor_list:
	                        print '\t' + user.keys()[0] + '\t\t' + user.values()[0]
	            elif str.find('open') != -1:
	                array = str.split()
	                if array[0] == 'open':
	                    if len(array) == 2:
	                        check = re.match(r"^[\d]*[\d|.]*[\d]$", array[1])
	                        if check != None:
	                            webbrowser.open_new_tab('http://' + array[1] + ':8800')
	                        else:
	                            print '\tInvalid Usage.\tTry: open [IP Address]'
	                    else:
	                        print '\tInvalid Usage.\tTry: open [IP Address]'
	            elif str == 'exit':
	                print '\tThank you for using Yuki-Share.'
	                sys.exit()
	            else:
	                print '\tFor more help or getting more Usages, Try input \'help\' '
        except KeyboardInterrupt:
            print '\n\tThank you for using Yuki-Share.'
            sys.exit()
                    
    
if __name__ == '__main__':
    fs = fileShare()
    fs.main()
