#! usr/bin/python
# -*- coding:utf-8 -*-
# Filename: FeiGe-gui.py


from FeiGe import FeiGe

import re
import os
import sys
import time
import socket
import thread
import threading
import gtk, pygtk
pygtk.require('2.0')


class GFeige(gtk.Window):

    def __init__(self):

        gtk.Window.__init__(self)
        self.set_title('Yuki-Share')
        self.connect('destroy', gtk.main_quit)
        self.set_size_request(280, 350)
        self.set_position(gtk.WIN_POS_CENTER)

        '''initialize the basic function'''
        self.fg = FeiGe()
        self.fg.frece_thread()
        self.fg.brc_thread()
        self.fg.reply_thread()        
        #time.sleep(0.1)

        self.list = gtk.ListStore(int, str)
        self.fg.onlineUser = ['192.168.1.101', '172.16.1.10', '10.1.1.1']
        self.freshUser()

        self.treeview = gtk.TreeView()
        model = self.treeview.get_selection()
        model.set_mode(gtk.SELECTION_SINGLE)
        r = gtk.CellRendererText()
        self.treeview.insert_column_with_attributes(-1, "onlineUser", r, text=1)
        #self.treeview.insert_column_with_attributes(-1, "hostname", r, text=1)

        self.treeview.set_model(self.list)
        self.treeview.connect("cursor-changed", self.listSelected)
        self.swindow = gtk.ScrolledWindow()
        self.swindow.add(self.treeview)

        self.count = gtk.Label('User num ' + str(len(self.fg.onlineUser)))
        self.renew = gtk.Button('Renew')
        self.send = gtk.Button('Send File')
        self.renew.connect('clicked', self.freshUser)
        self.send.connect('clicked', self.fileOpen)

        self.table = gtk.Table(20, 20, True)
        self.add(self.table)
        self.table.attach(self.swindow, 0, 20, 0, 15)
        self.table.attach(self.count, 0, 6, 16, 19)
        self.table.attach(self.renew, 7, 12, 16, 19)
        self.table.attach(self.send, 13, 19, 16, 19)

        self.show_all()
        self.fg.onlineUser = ['192.168.1.100']
        

    def freshUser(self, widget=None):
        self.list.clear()
        for user in range(0, len(self.fg.onlineUser)):
            iter = self.list.append( (user, self.fg.onlineUser[user]) )
            self.list.set(iter)


    def listSelected(self, treeview):
            s = treeview.get_selection()
            (ls, iter) = s.get_selected()
            if iter is None:
                    print "nothing selected"
            else:
                    data = ls.get_value(iter, 1)
                    print "Selected:", data


    def fileOpen(self, widget, data=None):
        dialog = gtk.FileChooserDialog('Open',None,
                      gtk.FILE_CHOOSER_ACTION_OPEN,
                                 (gtk.STOCK_CANCEL,
                               gtk.RESPONSE_CANCEL,
                                    gtk.STOCK_OPEN,
                                  gtk.RESPONSE_OK))
        res = dialog.run()
        if res == gtk.RESPONSE_OK:
            print dialog.get_filename()
        dialog.destroy()


if __name__ == '__main__':

    gtk.gdk.threads_init()
    gFeige = GFeige()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()

