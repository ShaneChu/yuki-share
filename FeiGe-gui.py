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

        '''the destination where the file would be sended'''
        self.dest = ''
        self.list = gtk.ListStore(int, str)

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
        self.send.connect('clicked', self.fileOpen, self.dest)

        self.table = gtk.Table(20, 20, True)
        self.add(self.table)
        self.table.attach(self.swindow, 0, 20, 0, 15)
        self.table.attach(self.count, 0, 6, 16, 19)
        self.table.attach(self.renew, 7, 12, 16, 19)
        self.table.attach(self.send, 13, 19, 16, 19)

        self.freshUser()
        self.show_all()
        

    def freshUser(self, widget=None):
        self.list.clear()
        self.fg.broadcast()
        time.sleep(0.5)
        for user in range(0, len(self.fg.onlineUser)):
            iter = self.list.append( (user, self.fg.onlineUser[user]) )
            self.list.set(iter)
        self.count.set_text('User num ' + str(len(self.fg.onlineUser)))
        print "self.fg.onlineUser:", self.fg.onlineUser


    def listSelected(self, treeview):
            s = treeview.get_selection()
            (ls, iter) = s.get_selected()
            if iter is None:
                    print "nothing selected"
            else:
                    data = ls.get_value(iter, 1)
                    self.dest = data


    def fileOpen(self, widget, dest=None):
        dialog = gtk.FileChooserDialog('Open',None,
                      gtk.FILE_CHOOSER_ACTION_OPEN,
                                 (gtk.STOCK_CANCEL,
                               gtk.RESPONSE_CANCEL,
                                    gtk.STOCK_OPEN,
                                  gtk.RESPONSE_OK))
        #dialog.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        if self.dest == '':
            self.warnDia('Please select a user.')
        else:
            res = dialog.run()
            if res == gtk.RESPONSE_OK:
                filename = dialog.get_filename()
                print 'file: %s to %s' % (filename, self.dest)
                self.fg.send_thr(self.dest, filename)
            dialog.destroy()


    def confirm(self, message):
        mydialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_YES_NO, message)
        t = mydialog.run()
        mydialog.destroy()
        if t == -8:
            return True
        return False


    def warnDia(self, str):
        md = gtk.MessageDialog(self, 
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING, 
            gtk.BUTTONS_CLOSE, str)
        md.set_position(gtk.WIN_POS_CENTER)
        md.set_title('Warning')
        md.run()
        md.destroy()


if __name__ == '__main__':

    gtk.gdk.threads_init()
    gFeige = GFeige()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()

