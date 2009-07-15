# -*- coding:utf-8 -*-

import gtk
import smtplib
import base64
import re
import threading
import thread
import gobject
import ConfigParser
import os
        
        
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
    
    
class MyWindow(gtk.Window):     #由Window类派生

    def __init__(self):
        '''GUI Initialization'''
            
        self.CONF_FILE = 'conf.cfg'     # "配置文件" 常量
        
        super(MyWindow,self).__init__()     #基类构造函数
        self.set_title('YuKi - mail')
        self.set_default_size(320,400)
        #self.set_resizable(False)
        #self.set_icon_from_file('icon.png')
        self.set_position(gtk.WIN_POS_CENTER)   #窗口屏幕居中
        
        table = gtk.Table(1,15,False)      #创建Table表格
        self.add(table)
        
        
        mb = gtk.MenuBar()      #菜单栏
        filemenu = gtk.Menu()       #文件菜单
        filem = gtk.MenuItem('File')
        filem.set_submenu(filemenu)
        
        exit = gtk.ImageMenuItem(gtk.STOCK_QUIT)    #退出菜单项
        exit.connect('activate', gtk.main_quit)
        filemenu.append(exit)
        mb.append(filem)
        
        helpmenu = gtk.Menu()
        helpm = gtk.MenuItem('Help')    #帮助菜单
        helpm.set_submenu(helpmenu)

        about = gtk.ImageMenuItem(gtk.STOCK_ABOUT)  #关于菜单项
        about.connect('activate', self.on_about)    #菜单项事件绑定
        helpmenu.append(about)
        mb.append(helpm)
        
        menu = gtk.VBox(False, 2)
        menu.pack_start(mb, False, False, 0)
        
        table_info = gtk.Table(15,10,False)
        
        #帐号标签
        accLabel = gtk.Label('Account:')
        self.accEntry = gtk.combo_box_entry_new_text()    #下拉列表
        
        #读取配置文件，预置常用帐号
        if os.path.exists(self.CONF_FILE):
            
            config = ConfigParser.ConfigParser()
            config.readfp(open(self.CONF_FILE))
            account_list = config.get('info', 'account')
            account_list = account_list.split() #将用空格分开的字符串拆分成列表
            
            account_len = len(account_list)     #帐号列表的长度
            
            '''这里最多只获取最近使用的五个帐号，并加入下拉列表选项'''
            if account_len <= 5:
                for i in range (0, account_len):
                    self.accEntry.append_text(account_list[i])
            else:
                for i in range (account_len-5, account_len):
                    self.accEntry.append_text(account_list[i])
        
        #密码标签
        pwLabel = gtk.Label('Password:')
        self.pwEntry = gtk.Entry()
        self.pwEntry.set_visibility(False)
        #收件人标签
        receLabel = gtk.Label('Receiver:')
        self.receEntry = gtk.Entry()
        #主题标签
        subLabel = gtk.Label('Subject:')
        self.subEntry = gtk.Entry()
        #正文标签
        textLabel = gtk.Label('Text:')
        
        #发送按钮
        send = gtk.Button('Send')
        send.set_size_request(20,20)
        send.connect('clicked',self.on_send_thread)     #按钮启动子线程
        
        table_info.attach(accLabel,0,3,0,2)
        table_info.attach(self.accEntry,3,5,0,2)
        
        table_info.attach(pwLabel,0,3,2,4)
        table_info.attach(self.pwEntry,3,5,2,4)
        
        table_info.attach(receLabel,0,3,4,6)
        table_info.attach(self.receEntry,3,5,4,6)
        
        table_info.attach(subLabel,0,3,6,8)
        table_info.attach(self.subEntry,3,5,6,8)
        
        table_info.attach(textLabel,0,3,8,10)
        table_info.attach(send,7,13,4,8)
        
        blank_1 = gtk.Label('')
        blank_2 = gtk.Label('')
        table_info.attach(blank_1,5,10,8,10)
        table_info.attach(blank_2,12,15,8,10)
        
        
        #多行文本框(邮件正文)
        swindow = gtk.ScrolledWindow()
        text = gtk.TextView()
        self.textbuffer = text.get_buffer()      #文本框缓冲区
        swindow.add(text)
        
        hbox_textView = gtk.HBox(False,30)
        hbox_textView.show()
        hbox_textView.pack_start(swindow)
        
        table.attach(menu,0,1,0,1)     #将菜单加入table
        table.attach(table_info,0,1,1,2)
        table.attach(hbox_textView,0,1,2,15)
        #    table布局分为上中下三部分，最上部是菜单栏
        #    中部是一个包含各个标签，文本框和一个发送按钮的table容器，
        #    下部是一个用来写邮件的文本域。
        
        self.connect('destroy', gtk.main_quit)      #关闭时结束程序
        self.show_all()


    def on_send_thread(self,widget=None):
        
        self.user = self.accEntry.get_active_text()
        self.pw = self.pwEntry.get_text()
        self.toaddr = self.receEntry.get_text()
        self.subject = self.subEntry.get_text()
        self.content = self.textbuffer.get_text(self.textbuffer.get_start_iter(),
                                                self.textbuffer.get_end_iter())
                                                #获取文本框从开头到结束的文本内容
                                                
        if not (self.user and self.pw) :  #帐号密码为空的判断
            self.on_warn('incomplete login info, please reset...')
            return
        if not (self.toaddr) :  #收件人为空的判断
            self.on_warn('please input the recevier...')
            return
        if not (self.subject) :  #主题为空的判断
            self.on_warn('please input the subject...')
            return
        if not (self.content):  #邮件正文非空约束
            self.on_warn('Mail Content cannot be null')
            return
        
        #邮件头部
        Head = ("From:%s\r\nTo:%s\r\nSubject:%s\r\n\r\n" \
                % (self.user, self.toaddr, self.subject))
        self.msg = Head + self.content
        
        try:
            #正则表达式邮箱地址
            mailCheck = re.match(r"^[\w|.|-]*@[\w|.]*.(com|net)$",self.user)
        except:
            print 'regular express error...'
            self.on_warn('regular express error...')
            return
        
        if mailCheck != None :
            '''判断邮箱名的合法性，满足条件后会获取SMTP服务器域名并发送邮件。'''
            
            tmp = self.user.split('@')
            self.mailSvr = 'smtp.' + tmp[1]
            print 'Connect smtpServer...'
            #self.on_info('Connect smtpServer,please wait...')
            conf = ConfigParser.ConfigParser()
            
            if not os.path.exists(self.CONF_FILE):
                #如果配置文件不存在则另外新建
                fp = open(self.CONF_FILE,'w')
                conf.readfp(open(self.CONF_FILE))
                conf.add_section('info')
                conf.set('info', 'account', self.user)
                conf.write(fp)
                fp.close()
                
            else:       #配置文件存在则追加内容
                conf.readfp(open(self.CONF_FILE))
                    
                account_list = conf.get('info', 'account')
                account_list = account_list.split()
                
                #如果帐号列表里已经存在该帐号，则将帐号移到列表的最后
                try:
                    if account_list.index(self.user)+1:
                        account_list.remove(self.user)
                        account_list.append(self.user)
                except:
                    account_list.append(self.user)
                    
                account_list = ' '.join(account_list)
                conf.set('info', 'account', account_list)
                fp = open(self.CONF_FILE, 'w')
                
                conf.write(fp)
                fp.close()
            
            on_send_t = mythread(self.on_send)      #启动子线程发邮件
            on_send_t.setDaemon(True)
            on_send_t.start()
                    
        else:
            self.on_warn('invalid mail address,please reset...')
        
        
    def on_send(self):
        '''Button Event Process'''

        
        if self.mailSvr == 'smtp.gmail.com': #用gmail服务器的情况
            try:
                smtp = smtplib.SMTP(self.mailSvr,587)    #Gmail的TLS验证要用587端口
                smtp.starttls()     #TLS验证方法
                print 'Connect smtpServer successful...'
            except:
                gobject.idle_add(self.on_warn,'Connect smtpServer fail,exit now...')
                return
               
        elif self.mailSvr == 'smtp.vip.qq.com': #用QQ邮箱VIP的情况，服务器不变
            try:
                smtp = smtplib.SMTP('smtp.qq.com')
                print 'Connect smtpServer successful...'
            except:
                gobject.idle_add(self.on_warn,'Connect smtpServer fail,exit now...')
                return
                
        else:  #用QQ或其他邮件服务器的情况
            try:
                smtp = smtplib.SMTP(self.mailSvr)
                print 'Connect smtpServer successful...'
            except:
                gobject.idle_add(self.on_warn,'Connect smtpServer fail,exit now...')
                return
           
        smtp.set_debuglevel(1)
        #有些stmp服务器使用“AUTH LOGIN”身份验证
        #所以这里smtplib的login方法可能失效，改成下面四句
        
        smtp.ehlo('localhost') #向服务器打招呼
        smtp.docmd("AUTH","LOGIN")  #发送登陆请求
        smtp.docmd(base64.encodestring(self.user).rstrip())  
        '''将帐号密码加密成base64编码后并发送'''
        smtp.docmd(base64.encodestring(self.pw).rstrip())    
        '''这里即使帐号密码错误也不会返回异常对象，只会在CLI打印认证失败信息'''
        
        try:
            print 'mail sending...'
            smtp.sendmail(self.user, self.toaddr, self.msg)     #发邮件就一句代码。。
            smtp.quit()
            gobject.idle_add(self.on_info,'Congratulations,mail sended successful...')
        except:
            gobject.idle_add(self.on_warn,'Authentication fail,Please reset the password...')
            return
        
        
    def on_about(self,widget):
        '''About Dialog'''
        
        about = gtk.AboutDialog()
        #about.set_icon_from_file('icon.png')    #设置图标
        about.set_position(gtk.WIN_POS_CENTER)  
        about.set_program_name("YuKi - mail")   #程序名称
        #about.set_version("0.1")               #设定版本信息
        about.set_copyright("(c) Shuege Digital Library")
        about.set_comments("YuKi - mail is a simple Communicate tool for Shuge")
        about.set_website("http://linuxtoy.org/archives/shuge.html")
        #about.set_logo(gtk.gdk.pixbuf_new_from_file("icon.png"))
        about.run()
        about.destroy()


    def on_info(self, str):
        '''Infomation Dialog'''
        
        md = gtk.MessageDialog(self, 
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, 
            gtk.BUTTONS_NONE, str)
        #md.set_icon_from_file('icon.png')
        md.set_position(gtk.WIN_POS_CENTER)
        #md.run()
        md.show()
        #md.destroy()
        
      
    def on_warn(self, str):
        '''Warning Dialog'''
        
        md = gtk.MessageDialog(self, 
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING, 
            #gtk.BUTTONS_CLOSE,
            gtk.BUTTONS_NONE, str)
        #md.set_icon_from_file('icon.png')
        md.set_position(gtk.WIN_POS_CENTER)
        #md.run()
        md.show()
        #md.destroy()
        
        '''
        子线程通过idle函数，让主线程在空闲时调用对话框。
        注意，这时如果对话框里有run方法则会发生死锁，所以用show代替。 
        因为run方法是对话框GUI的一个循环，用show代替后，destory函数会受一定影响：
        当对话框show时，调用destory方法，对话框会一闪而过。
        而注释掉destory方法时，点击按钮没有任何效果。
        这时要点右上角的关闭才能关闭了。
        如果把gtk.BUTTONS_CLOSE改成gtk.BUTTONS_NONE，对话框则只剩一个灯泡和自定义的提示
        并且失去按钮，提示文字会变成焦点，默认被全选选中。'''
    


def main():
    gtk.gdk.threads_init()
    # 初始化GUI相关代码
    MyWindow()
    gtk.gdk.threads_enter()
    # 开始进入线程
    # GUI接受响应
    gtk.main()
    gtk.gdk.threads_leave()


if __name__ == '__main__':
    main()

    #
    #    登录QQ邮箱要省去starttls方法,而且要求邮箱要开启smtp/pop服务。
    #    登录Gmail邮箱使用587端口和TLS验证
    #    登录163邮箱(用户被锁定，163服务器限制smtp权限，未解决)
    #
    
