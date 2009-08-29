# -*- coding:utf-8 -*-

import threading
import thread
import socket
import time
import os
import SimpleHTTPServer
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


class FileSharing():
    
    def HTTPServer(self):
        if not os.path.exists('FileShare.cfg'):
            print 'not exist'
        else:
            localName = socket.gethostname()    #获取主机名
            self.localIP = socket.gethostbyname(localName)   #获取本地ip
            file = open('FileShare.cfg', 'r')
            self.directory = file.read()
            file.close()
            os.chdir(self.directory)     #切换工作目录到共享目录
            
            '''将本机目录共享出去，启动HTTP服务器'''
            handler = SimpleHTTPServer.SimpleHTTPRequestHandler
            httpd = SocketServer.TCPServer((self.localIP, 8000), handler)
            print "HTTP server is at: ", self.localIP, ': 8000'
            print 'Server Booting successful...'
            httpd.serve_forever()
    
    def HTTP_svr_Thread(self):
        HTTP_svr_Thread = mythread(self.HTTPServer)
        HTTP_svr_Thread.setDaemon(True)
        HTTP_svr_Thread.start()
    
    
    def Server(self):
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        
        self.neighbor_list = []     #局域网列表
        localIP = socket.gethostbyname(socket.gethostname())
        s.bind((localIP,1080))
        print "waitting data..."
        while 1:
            try:
                d, a=s.recvfrom(8192)    #d是data，a是address
                #列表添加一个字典('IP':'' ; 'share_dir_list':'')
                dict = {}
                dict['IP'] = a
                dict['share_dir_list'] = d
                
                #如果目录已在字典中则忽略。否则将IP和共享目录添加到字典。
                try:
                    if self.neighbor_list.index(dict)+1:
                        pass
                except:
                    self.neighbor_list.append(dict)
                print self.neighbor_list
                
            except:
                print "error"
        s.close()
        
        
    def boardcast(self):
        #另起线程接收和发送
        self.HTTP_svr_Thread()      #启动HTTP简单服务器做共享
        self.svr_thread()           #接受广播，随时更新局域网内共享目录（工作线程）
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        file = open('FileShare.cfg', 'r')
        directory = file.read()
        data = directory
        file.close()
        
        while  1:
            time.sleep(10)      #每隔10秒发一次广播,并更新局域网列表
            s.sendto(data, ('255.255.255.255',1080))
        s.close()
        
        
    def svr_thread(self):
        svr = mythread(self.Server)
        svr.setDaemon(True)
        svr.start()
        

    def get_neighbor_list(self):
        return self.neighbor_list       #返回局域网列表
    
    
if __name__ == '__main__':
    t = FileSharing()
    t.boardcast()
    list = t.get_neighbor_list
    print list

