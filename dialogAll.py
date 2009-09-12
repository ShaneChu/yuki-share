# -*- coding:utf-8 -*-

import pygtk,gtk

pygtk.require('2.0')

class MyWindow(object):
    def __init__(self,title,width,height):
        self.window = gtk.Window()
        self.window.set_title(title)
        self.window.set_default_size(width,height)
        self.window.connect('destroy',lambda q :gtk.main_quit())

        self.label = gtk.Label(u'标准对话框示例')

        self.button1 = gtk.Button(u'文件选择框')
        self.button1.connect('clicked',self.OnButton1,'FileChooser')

        self.button2 = gtk.Button(u'字体选则框')
        self.button2.connect('clicked',self.OnButton2,'FontChooser')
        
        self.button3 = gtk.Button(u'颜色选择框')
        self.button3.connect('clicked',self.OnButton3,'ColorChooser')

        self.fixed = gtk.Fixed()
        self.fixed.put(self.label,80,40)
        self.fixed.put(self.button1,10,130)
        self.fixed.put(self.button2,100,130)
        self.fixed.put(self.button3,210,130)

        self.window.add(self.fixed)

        self.label.show()
        self.button1.show()
        self.button2.show()
        self.button3.show()
        self.fixed.show()
        self.window.show()

    def OnButton1(self,widget,data):
        dialog = gtk.FileChooserDialog('Open',  # 文件打开对话框
                                       None,    # 父窗口
                  gtk.FILE_CHOOSER_ACTION_OPEN, # 对话框标志
                             (gtk.STOCK_CANCEL, # 添加cancel按钮
                           gtk.RESPONSE_CANCEL, # Cancel按钮的返回值
                               gtk.STOCK_OPEN,  # 添加打开按钮
                              gtk.RESPONSE_OK)) # Open按钮的返回值
        # 用于文件过滤
        filter = gtk.FileFilter()
        filter.set_name('All Files')# 设置文件类型名
        filter.add_pattern('*')     # 所有文件
        dialog.add_filter(filter)   # 添加到dialog中

        # 可以有多个filter对象
        filter = gtk.FileFilter()
        filter.set_name('Python')   # 文件类型名
        filter.add_pattern('*.py')  # 添加文件后缀名
        filter.add_pattern('*.pyw') # 添加文件后缀名
        dialog.add_filter(filter)

        # 跟MessageDialog一样,需要用run方法显示
        res = dialog.run()

        if res == gtk.RESPONSE_OK:
            # 取到的文件名
            print dialog.get_filename()

        # 同MessageDialog
        dialog.destroy()
        
    def OnButton2(self,widget,data):
        fontdlg = gtk.FontSelectionDialog(u'选择字体')
        res = fontdlg.run()

        if res == gtk.RESPONSE_OK:
            # 取到的字体名字
            print fontdlg.get_font_name()
        
        fontdlg.destroy()
        
    def OnButton3(self,widget,data):
        colordlg = gtk.ColorSelectionDialog(u'选择颜色')

        # 显示调色板
        colordlg.colorsel.set_has_palette(True)
        
        res = colordlg.run()

        if res ==gtk.RESPONSE_OK:
            # 取到的颜色
            print colordlg.colorsel.get_current_color()
            
        colordlg.destroy()

    def main(self):
        gtk.main()

if __name__ == '__main__':
    window = MyWindow(u'第十一个PyGTK窗口',300,200)
    window.main()
