#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: FeiGe-gui.py


from FeiGe import FeiGe

import re
import os
import sys
import time
import socket
import thread
import gobject
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
        gobject.idle_add(self.fg.frece_thread)
        #gobject.idle_add(self.fg.fileRec, self.confirm, 'receive a file, download or not?')
        gobject.idle_add(self.fg.brc_thread)
        gobject.idle_add(self.fg.reply_thread)

        '''the destination where the file would be sended'''
        self.dest = ''
        self.list = gtk.ListStore(str, str)

        self.treeview = gtk.TreeView(self.list)
        model = self.treeview.get_selection()
        model.set_mode(gtk.SELECTION_SINGLE)
        self.user_column = gtk.TreeViewColumn('在线用户')
        self.host_column = gtk.TreeViewColumn('主机名')
        self.treeview.append_column(self.user_column)
        self.treeview.append_column(self.host_column)

        self.user_cell = gtk.CellRendererText()
        self.host_cell = gtk.CellRendererText()
        self.user_column.pack_start(self.user_cell, True)
        self.host_column.pack_start(self.host_cell, True)
        self.user_column.set_attributes(self.user_cell, text=0)
        self.host_column.set_attributes(self.host_cell, text=1)

        self.user_column.set_sort_column_id(0)
        self.treeview.set_reorderable(True)

        '''the fifth line below is to use auto scrollbar policy for ScrolledWindow'''
        self.treeview.set_model(self.list)
        self.treeview.connect("cursor-changed", self.listSelected)
        self.swindow = gtk.ScrolledWindow()
        self.swindow.add(self.treeview)
        self.swindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.count = gtk.Label('用户数 \n    ' + str(len(self.fg.onlineUser)))
        self.renew = gtk.Button('刷新')
        self.about = gtk.Button('关于')
        self.send = gtk.Button('发送文件')
        self.sendDir = gtk.Button('发送文件夹')
        self.renew.connect('clicked', self.ButtonEvent)
        self.about.connect('clicked', self.on_about)
        self.send.connect('clicked', self.fileOpen, self.dest)
        self.sendDir.connect('clicked', self.folderOpen, self.dest)

        self.table = gtk.Table(20, 20, True)
        self.add(self.table)
        self.table.attach(self.swindow, 0, 14, 0, 14)
        self.table.attach(self.count, 14, 20, 2, 5)
        self.table.attach(self.renew, 15, 19, 6, 9)
        self.table.attach(self.about, 15, 19, 9, 12)
        self.table.attach(self.send, 13, 19, 16, 19)
        self.table.attach(self.sendDir, 6, 12, 16, 19)

        self.show_all()
        gobject.idle_add(self.freUser_thr)
        

    def freshUser(self, widget=None):
        self.fg.broadcast()
        time.sleep(1)
        self.list.clear()
        for user in range(0, len(self.fg.onlineUser)):
            iter = self.list.append(self.fg.onlineUser[user])
            self.list.set(iter)
        self.count.set_text('用户数 \n    ' + str(len(self.fg.onlineUser)))
        print "self.fg.onlineUser:", self.fg.onlineUser


    def freUser_thr(self):
        fre_thr = mythread(self.freshUser)
        fre_thr.setDaemon(True)
        fre_thr.start()


    def ButtonEvent(self, widget=None):
        gobject.idle_add(self.freUser_thr)


    def listSelected(self, treeview):
            s = treeview.get_selection()
            (ls, iter) = s.get_selected()
            if iter is None:
                    print "nothing selected"
            else:
                    data = ls.get_value(iter, 0)
                    self.dest = data


    def fileOpen(self, widget, dest=None):
        dialog = gtk.FileChooserDialog('Open',None,
                      gtk.FILE_CHOOSER_ACTION_OPEN,
                                 (gtk.STOCK_CANCEL,
                               gtk.RESPONSE_CANCEL,
                                    gtk.STOCK_OPEN,
                                  gtk.RESPONSE_OK))
        dialog.set_select_multiple(True)
        if self.dest == '':
            self.warnDia('Please select a user.')
        else:
            res = dialog.run()
            if res == gtk.RESPONSE_OK:
                filenames = dialog.get_filenames()
                for file in filenames[0:-1]:
                    gobject.idle_add(self.fg.fileTransfer, self.dest, file)
                gobject.idle_add(self.fg.fileTransfer, self.dest, filenames[-1], self.infoDia, 'Files has been sended.')
            dialog.destroy()


    def folderOpen(self, widget, dest=None):
        dialog = gtk.FileChooserDialog('Open',None,
             gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                 (gtk.STOCK_CANCEL,
                               gtk.RESPONSE_CANCEL,
                                      gtk.STOCK_OK,
                                  gtk.RESPONSE_OK))
        if self.dest == '':
            self.warnDia('Please select a user.')
        else:
            res = dialog.run()
            if res == gtk.RESPONSE_OK:
                folderName = dialog.get_current_folder()
                if os.name == 'nt':
                    folderName = folderName.decode('utf-8').encode('936')
                print folderName
                #gobject.idle_add(self.fg.fileTransfer, self.dest, filename, self.infoDia, 'File has been sended.')
            dialog.destroy()
            

    def confirm(self, message):
        mydialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_YES_NO, message)
        mydialog.set_title('Choose Dialog')
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


    def infoDia(self, str):
        md = gtk.MessageDialog(self, 
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, 
            gtk.BUTTONS_OK, str)
        md.set_position(gtk.WIN_POS_CENTER)
        md.set_title('Information')
        md.run()
        md.destroy()


    def on_about(self, data=None):

        about = gtk.AboutDialog()
        about.set_name('Yuki-Feige')
        about.set_version('1.0')
        about.set_website('https://code.google.com/p/shuge/issues')
        about.set_website_label('Shuge Group')
        about.set_comments('Yuki-Feige is a GUI interface of File Transfer')
        about.set_authors(['Shane Chu, Shane_Chu@qq.com'])
        about.set_copyright('Copyright © 2009 Shane Chu')
        about.set_position(gtk.WIN_POS_CENTER)

        about.set_wrap_license(True)
        about.set_license('Yuki-Feige is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.\n\
Yuki-Feige is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.\n\
You should have received a copy of the GNU General Public License along with Yuki-Feige; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA')
        about.set_translator_credits('translator-credits')
        about.set_artists(['Shane Chu, Shane_Chu@qq.com'])

        about.run()
        about.destroy()        


if __name__ == '__main__':

    gobject.threads_init()
    gFeige = GFeige()
    gtk.main()




