# looking for install dir   
import e32
import sys
import os
import appuifw
DEFDIR = u"c:\\python"
for d in e32.drive_list():
    appd = os.path.join(d,u"\\data\\python\\PySyncNotes\\")
    if os.path.exists(os.path.join(appd,u"notes.py")):
        DEFDIR = appd
        break

sys.path.append(DEFDIR)

import notes
t = appuifw.Text()
appuifw.app.body = t
t.add(u'Wait...')

notes.AppNotes().run()
app_lock = e32.Ao_lock()
app_lock.wait()