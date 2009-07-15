# -*- coding:utf-8 -*-

import win32api
import win32con

def setSysEnvir(Var_Name,Var_Value):
    """set the windows system environment. """
    
    # open the position where system stores system environment.
    pathInReg = 'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment'
    
    key = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, \
                              pathInReg, 0, win32con.KEY_ALL_ACCESS)
    
    win32api.RegSetValueEx(key, Var_Name, 0, win32con.REG_SZ, Var_Value)
    win32api.RegCloseKey(key)

if __name__ == "__main__":
    setSysEnvir('Shane','Chu')
    print 'great!'

'''可能不会立即生效，不然得重启'''