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
            localName = socket.gethostname()    #获取主机名

            print 'localName is :', localName
            print 'local IP is :', self.local_IP
            
            file = open('FileShare.cfg', 'r')
            directory = file.read()
            #print 'current directory is :', os.getcwd()
            file.close()
            os.chdir(directory)     #切换工作目录到共享目录
            print 'directory after changed :', os.getcwd()
            
            '''将本机目录共享出去，启动HTTP服务器'''
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
            #如果是本机IP，不添加进字典。也不发送应答！
            if not address[0] == self.local_IP:
                dict = {}
                dict['IP'] = address
                dict['share_dir_list'] =  message
                print "Got data from", address
                
                #如果目录已在字典中则忽略。否则将IP地址和共享目录添加到字典。
                try:
                    if self.neighbor_list.index(dict) + 1:
                        pass
                except:
                    self.neighbor_list.append(dict)
                    print '当前在线用户列表：', self.neighbor_list
                
                os.chdir(self.currentDir)
                file = open('FileShare.cfg', 'r')
                directory = file.read()
                file.close()
                s.sendto(directory, address)    #对广播的应答

        
    def svr_thread(self):
        svr = mythread(self.Server)
        svr.setDaemon(True)
        svr.start()
        
    def boardcast(self):
        dest = ("<broadcast>",50000)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        os.chdir(self.currentDir)
        file = open('FileShare.cfg', 'r')
        directory = file.read()
        file.close()
        s.sendto(directory, dest)
        
        while 1:
            message, address = s.recvfrom(2048)
            #如果是本机IP可以考虑不添加进字典
            dict = {}
            dict['IP'] = address
            dict['share_dir_list'] =  message
            #print "Got data from",address
            
            #如果目录已在字典中则忽略。否则将IP地址和共享目录添加到字典。
            try:
                if self.neighbor_list.index(dict) + 1:
                    pass
            except:
                self.neighbor_list.append(dict)
                print '当前在线用户列表：', self.neighbor_list
    
    
    def boot(self):
                    
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('google.com', 0))
        self.local_IP = s.getsockname()[0]   #linux下获取本地ip
        
        #self.localIP = socket.gethostbyname(socket.gethostname())   #win下获取本地ip
        
        #启动HTTP线程会改变当前路径。这句代码先保存该路径以做之后读取配置文件用。
        self.currentDir = os.getcwd()
        #另起线程接收和发送
        self.HTTP_svr_Thread()      #启动HTTP简单服务器做共享
        self.svr_thread()           #接受广播，随时更新局域网内共享目录（工作线程）
        self.boardcast()            #用户登录的时候发送广播
        
    
    def get_neighbor_list(self):
        self.boardcast()
    
if __name__ == '__main__':
    t = FileSharing()
    t.boot()
    t.get_neighbor_list()
    
    
