# -*- coding:utf-8 -*-

import win32api
import win32con
import os

def setSysEnvir(Var_Value):
    """set the windows system environment. """
    
    # open the position where system stores system environment.
    pathInReg = 'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment'
    key = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, pathInReg, 0, win32con.KEY_ALL_ACCESS)
    
    #先读取path的值，追加路径后再覆盖原来的path。
    value = win32api.RegQueryValueEx(key, 'path')
    newValue = value[0] + ";" + Var_Value
    win32api.RegSetValueEx(key, 'path', 0, win32con.REG_SZ, newValue)
    win32api.RegCloseKey(key)

if __name__ == "__main__":
    setSysEnvir('E:\\testdir')
    print 'great!'

#不会立即生效，需要重启

