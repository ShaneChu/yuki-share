#! usr/bin/python
# -*- coding:utf-8 -*-
# Filename: gui_release.py

from cli_release import fileShare


import re
import os
import sys
import time
import socket
import thread
import threading
import webbrowser
import gtk, pygtk
pygtk.require('2.0')


class GYuki(gtk.Window):

    def __init__(self):

        gtk.Window.__init__(self)
        self.set_title('Yuki-Share')
        self.connect('destroy', gtk.main_quit)
        self.set_size_request(300, 300)
        self.set_position(gtk.WIN_POS_CENTER)

        # These four lines below should be added to the __init__() function in GUI
        self.fshare = fileShare()
        self.fshare.HTTP_svr_Thread()
        self.fshare.svr_thread()
        self.fshare.reply_thread()
        time.sleep(0.05)
		
        self.table = gtk.Table(20, 20, True)
        self.add(self.table)
        self.addrEntry = gtk.combo_box_entry_new_text()
        self.table.attach(self.addrEntry, 0, 15, 0, 2)

        # put the online users into pull-down lists
        for user in self.fshare.neighbor_list:
            ip = user.keys()[0]
            self.addrEntry.append_text(ip)

        self.open = gtk.Button('Open')
        self.table.attach(self.open, 15, 20, 0, 2)
        self.open.connect('clicked',self.openWeb)

        self.onLab = gtk.Label('Online Users :')
        self.table.attach(self.onLab, 0, 7, 2, 4)
        self.renew = gtk.Button('Renew')
        self.table.attach(self.renew, 15, 20, 2, 4)
        self.renew.connect('clicked', self.renewUser)

        self.swindow = gtk.ScrolledWindow()
        self.text = gtk.TextView()
        self.text.set_editable(False)
        self.textbuffer = self.text.get_buffer()
        self.swindow.add(self.text)
        self.table.attach(self.swindow, 0, 20, 4, 14)

        if self.fshare.neighbor_list != []:
            self.textbuffer.set_text('neighbor users' + '\t\tdirectory\n')
            for user in self.fshare.neighbor_list:
                ip = user.keys()[0]
                dir = user.values()[0]
                iter = self.textbuffer.get_end_iter()
                self.textbuffer.insert(iter, ip + '\t\t' + dir + '\n')
        else:
            self.textbuffer.set_text('There is no any other users online now.')
        
        self.infoLab = gtk.Label('Hostname : '+self.fshare.localName)
        self.infoLab.set_text(self.infoLab.get_text()+'\nOperate System : '+os.sys.platform)
        self.infoLab.set_text(self.infoLab.get_text()+'\nLocalhost IP : '+self.fshare.local_IP)
        self.infoLab.set_text(self.infoLab.get_text()+'\nShare Dir : '+self.fshare.directory)
        self.table.attach(self.infoLab, 0, 18, 14, 20)

        self.show_all()


    def openWeb(self, widget=None):

        ip = self.addrEntry.get_active_text()
        check = re.match(r"^[\d]*[.][\d]*[.][\d]*[.][\d]*$", ip)

        if check != None:
            url = 'http://' + ip + ':8800'
            webbrowser.open_new_tab(url)
        else:
            self.warning('Invalid Address Format')


    def renewUser(self, widget=None):
        self.fshare.boardcast()


    def warning(self, message):
        mydialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK, message)
        t = mydialog.run()
        mydialog.destroy()


if __name__ == '__main__':
    gtk.gdk.threads_init()
    gyuki = GYuki()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()



