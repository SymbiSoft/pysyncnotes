# -*- coding: utf-8 -*-
import appuifw,e32,e32db,globalui
from keycapture import *
from key_codes import *
from sysinfo import display_pixels
from lang import *
from ConfigParser import ConfigParser
import os, sys
import selectionBox
from graphics import *
from topwindow import *
import time, datetime
from db import *
from nota import *

try:
    # http://discussion.forum.nokia.com/forum/showthread.php?p=575213
    # Try to import 'btsocket' as 'socket' (just for 1.9.x)
    sys.modules['socket'] = __import__('btsocket')
except ImportError:
    pass
import socket

encoding = 'utf-8'
VERSION = '0.1'

class AppNotes:
  version = VERSION
  
  def __init__(self):
    self.notaSel=Notes(id=-1)
    self.colorBlauActual="-1"
    self.colorGrocActual="-1"
    self.colorVerdActual="-1"
    self.colorVermellActual="-1"
    self.ordreActual="-1"
    self.titolActual=""
    
  def update_locale(self,lang2=""):
    self.labels = Locale(lang2)
    
  #metode missatget sobre la versio
  def sobre(self):
    globalui.global_msg_query(u"PySyncNotes\n"+self.labels.loc.versio +self.version+"\n(C) Lluis Danes, 2010",self.labels.loc.sobre_aplicacio)

  #funcio principal del programa
  def run(self):
    appuifw.app.screen="normal"
    appuifw.app.title = u"NOTES"
    appuifw.app.orientation="portrait"
    appuifw.app.exit_key_handler = quit
    self.comprovarDirectori()
    
    #popups
    self.windowColor=TopWindow()
    self.windowVisualitzarTop = TopWindow()
    self.windowVisualitzarBottom = TopWindow()
    self.bgColor=self.bgColor=Image.new((100,30))
    screen_size = display_pixels()
    self.bgColorLinia=self.bgColor=Image.new((screen_size[0],10))
    
    self.refrescar()
    self.lock = e32.Ao_lock()
    self.lock.wait()

  def formAfegir(self):
    self.color=0;
    d = { 0: 0x3588B3, 1: 0xFEC606, 2:0x9BCB66 ,3: 0xDE9277} #colors nota
    
    #LINIA ADALT I ABAIX - PART COMUNA
    screen_size = display_pixels()
    self.height = 2
    self.width = screen_size[0]
    self.left = 0
    self.bgColorLinia=Image.new((screen_size[0],10))
    self.bgColorLinia.clear(d[int(self.color)])
    
    #LINIA ADALT
    alturaIniciPanellSobre = appuifw.app.layout(appuifw.EStatusPane)[0][1]
    self.top = alturaIniciPanellSobre
    self.windowVisualitzarTop.add_image(self.bgColorLinia, (0,0))
    self.windowVisualitzarTop.corner_type = 'square'
    self.windowVisualitzarTop.size = (self.width, self.height)
    self.windowVisualitzarTop.position = (self.left,self.top)
    self.windowVisualitzarTop.show()
    
    #LINIA ABAIX
    alturaIniciPanellSota = appuifw.app.layout(appuifw.EControlPaneTop)[1][1]
    self.height = 4
    self.top = alturaIniciPanellSota -self.height
    self.windowVisualitzarBottom.add_image(self.bgColorLinia, (0,0))
    self.windowVisualitzarBottom.corner_type = 'square'
    self.windowVisualitzarBottom.size = (self.width, self.height)
    self.windowVisualitzarBottom.position = (self.left,self.top)
    self.windowVisualitzarBottom.show()

    #COLOR ETIQUETA
    self.bgColor=Image.new((100,30))
    self.bgColor.clear(d[int(self.color)])
    self.bgColor.text((30,18), self.labels.loc.color, 0x000000, font=(u"Nokia Hindi S60", 16, appuifw.STYLE_BOLD))
    self.windowColor.add_image(self.bgColor, (0,0))
    screen_size = display_pixels()
    
    #sizes & positions
    self.height = 25
    self.width = 100
    self.top = screen_size[1] - self.height - 2
    self.left = int((screen_size[0] - self.width) / 2)
    self.windowColor.shadow=0
    self.windowColor.corner_type = 'corner3'
    self.windowColor.size = (self.width, self.height)
    self.windowColor.position = (self.left,self.top)
    self.windowColor.show()

    self.t = appuifw.Text()
    self.t.bind(key_codes.EKeySelect, lambda:self.formAfegirColor())
    appuifw.app.exit_key_handler = self.run
    appuifw.app.body= self.t
    self.t.color = 0x000000
    self.t.font = (u"Nokia Hindi S60", 18, None)
    self.t.style = 0

    self.color=0;
    appuifw.app.menu = [(self.labels.loc.guardar,self.formAfegirTitol)]
    #el formulari podra ser editable i utiliza 1a sola columna per cada label i text (FFormDoubleSpaced).
    app_lock=e32.Ao_lock()
    app_lock.wait()
    
  def formAfegirColor(self):
    d = { 0: 0x3588B3, 1: 0xFEC606, 2:0x9BCB66 ,3: 0xDE9277}
    colors=[self.labels.loc.blau,self.labels.loc.groc,self.labels.loc.verd,self.labels.loc.vermell]
    colors.sort
    self.color = appuifw.popup_menu(colors, self.labels.loc.seleccionar_color)
    if self.color!=None:
      self.windowColor.remove_image(self.bgColor)
      self.bgColor.clear(d[int(self.color)])
      self.bgColor.text((30,18), self.labels.loc.color, 0x000000, font=(u"Nokia Hindi S60", 16, appuifw.STYLE_BOLD))
      self.windowColor.add_image(self.bgColor, (0,0))
        
      self.windowVisualitzarBottom.remove_image(self.bgColorLinia)
      self.windowVisualitzarTop.remove_image(self.bgColorLinia)
      self.bgColorLinia.clear(d[int(self.color)])
      self.windowVisualitzarBottom.add_image(self.bgColorLinia,(0,0))
      self.windowVisualitzarTop.add_image(self.bgColorLinia,(0,0))
    
  def formEditarTtitol(self):
    self.titol= appuifw.query(self.labels.loc.titol,"text")
    
  def formEditar(self):
    self.nota = self.resultat[self.lb.current()]
    d = { 16384: 0, 16386: 1, 16388:2 ,16390: 3}
    a = { 0: 0x3588B3, 1: 0xFEC606, 2:0x9BCB66 ,3: 0xDE9277}
    
    #LINIA ADALT I ABAIX - COMU
    screen_size = display_pixels()
    self.height = 2
    self.width = screen_size[0]
    self.left = 0
    self.bgColorLinia=Image.new((screen_size[0],10))
    self.bgColorLinia.clear(a[int(d[int(self.nota.get_color())])])
    
    #LINIA ADALT
    alturaIniciPanellSobre = appuifw.app.layout(appuifw.EStatusPane)[0][1]
    self.top = alturaIniciPanellSobre
    self.windowVisualitzarTop.add_image(self.bgColorLinia, (0,0))
    self.windowVisualitzarTop.corner_type = 'square'
    self.windowVisualitzarTop.size = (self.width, self.height)
    self.windowVisualitzarTop.position = (self.left,self.top)
    self.windowVisualitzarTop.show()
    
    #LINIA ABAIX
    alturaIniciPanellSota = appuifw.app.layout(appuifw.EControlPaneTop)[1][1]
    self.height = 4
    self.top = alturaIniciPanellSota -self.height
    self.windowVisualitzarBottom.add_image(self.bgColorLinia, (0,0))
    self.windowVisualitzarBottom.corner_type = 'square'
    self.windowVisualitzarBottom.size = (self.width, self.height)
    self.windowVisualitzarBottom.position = (self.left,self.top)
    self.windowVisualitzarBottom.show()
    
    self.color=d[int(self.nota.get_color())]
    self.titol= self.nota.get_titol()
    
    self.bgColor=Image.new((100,30))
    self.bgColor.clear(a[int(self.color)])
    self.bgColor.text((30,18), self.labels.loc.color, 0x000000, font=(u"Nokia Hindi S60", 16, appuifw.STYLE_BOLD))
    self.windowColor.add_image(self.bgColor, (0,0))
    screen_size = display_pixels()
    #sizes & positions
    self.height = 25
    self.width = 100
    self.top = screen_size[1] - self.height - 2
    self.left = int((screen_size[0] - self.width) / 2)
    self.windowColor.shadow=0
    self.windowColor.corner_type = 'corner3'
    self.windowColor.size = (self.width, self.height)
    self.windowColor.position = (self.left,self.top)
    self.windowColor.show()
    
    
    self.t = appuifw.Text()
    self.t.bind(key_codes.EKeySelect, lambda: self.formAfegirColor())
    appuifw.app.exit_key_handler = self.run
    appuifw.app.body= self.t
    self.t.color = 0x000000
    self.t.font = (u"Nokia Hindi S60", 18, None)
    self.t.style = 0
    
    f = open(DATA_PATH+"\\files\\"+str(self.nota.get_id()), "rb")
    self.nota.set_desc(f.read().decode("utf-8"))
    f.close()
    
    self.t.add(unicode(self.nota.get_desc()))
    appuifw.app.menu = [(self.labels.loc.guardar,self.editar),(self.labels.loc.canviar_titol,self.formEditarTtitol)]
    #el formulari podra ser editable i utiliza 1a sola columna per cada label i text (FFormDoubleSpaced).
    self.lock = e32.Ao_lock()
    self.lock.wait()

  def visualitzar(self):
    nota = self.resultat[self.lb.current()]
    
    d = { 16384: 0, 16386: 1, 16388:2 ,16390: 3}
    a = { 0: 0x3588B3, 1: 0xFEC606, 2:0x9BCB66 ,3: 0xDE9277}
    
    #LINIA ADALT I ABAIX - COMU
    screen_size = display_pixels()
    self.height = 10
    self.width = screen_size[0]
    self.left = 0
    
    self.bgColor=Image.new((screen_size[0],10))
    self.bgColor.clear(a[int(d[int(nota.get_color())])])
    
    #LINIA ADALT
    self.top = 0
    self.windowVisualitzarTop.add_image(self.bgColor, (0,0))
    self.windowVisualitzarTop.corner_type = 'square'
    self.windowVisualitzarTop.size = (self.width, self.height)
    self.windowVisualitzarTop.position = (self.left,self.top)
    self.windowVisualitzarTop.show()
    
    #LINIA ABAIX
    alturaIniciPanellSota = appuifw.app.layout(appuifw.EControlPaneTop)[1][1]
    self.top = alturaIniciPanellSota -10
    self.windowVisualitzarBottom.add_image(self.bgColor, (0,0))
    self.windowVisualitzarBottom.corner_type = 'square'
    self.windowVisualitzarBottom.size = (self.width, self.height)
    self.windowVisualitzarBottom.position = (self.left,self.top)
    self.windowVisualitzarBottom.show()
    
    appuifw.app.exit_key_handler = self.run
    appuifw.app.screen="large"
    self.t = appuifw.Text()
    appuifw.app.body = self.t
    #Set the color of the text
    self.t.color = 0x000080
    self.t.set_pos(3)
    self.t.add(u"\n")
    self.t.font = (u"Nokia Hindi S60", 25, None)
    self.t.style = (appuifw.STYLE_BOLD | appuifw.STYLE_BOLD) #STYLE_UNDERLINE
    self.t.add(nota.get_titol())
   
    f = open(DATA_PATH+"\\files\\"+str(nota.get_id()), "rb")
    nota.set_desc(f.read().decode("utf-8"))
    f.close()
    
    self.t.color = 0x000000
    self.t.font = (u"Nokia Hindi S60", 18, None)
    self.t.style = 0
    self.t.add("\n\n"+unicode(nota.get_desc()))
   
    self.t.set_pos(0)
    self.notaSel=nota

    #capturar quasevol tecla
    global capturer
    capturer=KeyCapturer(self.cb_capture)
    capturer.keys=(all_keys)
    capturer.start()
    self.lock = e32.Ao_lock()
    self.lock.wait()

  def sortirVisualitzar(self):
     capturer.stop()
     self.run()

  def cb_capture(self,key):
        self.allowed_keys=[EKeyUpArrow,EKeyDownArrow,EKeyDevice1,EKeyDevice0]
	if(key not in self.allowed_keys):pass
        elif(key==EKeyDevice1):self.sortirVisualitzar()
	elif(key==EKeyUpArrow):self.t.set_pos(self.t.get_pos()-50)  #Move the cursor up by 50 characters (adjust the value to what suits your needs)
	elif(key==EKeyDownArrow):self.t.set_pos(self.t.get_pos()+50)

  #afegir nova nota
  def formAfegirTitol(self):
    titol= appuifw.query(self.labels.loc.titol,"text")
    if titol:
      self.afegir(titol)
  
  def eliminar(self):
    if appuifw.query(self.labels.loc.eliminar_nota+self.resultat[appuifw.app.body.current()].get_titol(), "query"):
      self.resultat[appuifw.app.body.current()].eliminar()
    self.refrescar()
      
  def afegir(self,titol):
    self.windowColor.remove_image(self.bgColor)
    self.windowVisualitzarBottom.remove_image(self.bgColorLinia)
    self.windowVisualitzarTop.remove_image(self.bgColorLinia)
    self.windowVisualitzarBottom.hide()
    self.windowVisualitzarTop.hide()
    d = { 0: 16384, 1: 16386, 2:16388 ,3: 16390}
    desc=appuifw.app.body.get()
    nota = Notes(0,titol,desc,color=d[int(self.color)])
    nota.inserir()
    self.notaSel=nota
    #nota.guardar()
    self.refrescar()
    
  #modificar nova nota
  def editar(self):
    self.windowColor.remove_image(self.bgColor)
    self.windowVisualitzarBottom.remove_image(self.bgColorLinia)
    self.windowVisualitzarTop.remove_image(self.bgColorLinia)
    self.windowVisualitzarBottom.hide()
    self.windowVisualitzarTop.hide()
    desc=appuifw.app.body.get()
    d = { 0: 16384, 1: 16386, 2:16388 ,3: 16390}
    
    nota2 = Notes(self.nota.get_id(),self.titol,desc,color=d[int(self.color)])
    nota2.editar()
    self.notaSel=nota2
    self.run()
    
    
  def llistar(self,tipus,where="",order=""): #seleccionada es per tenir seleccionada
    self.resultat = []
    dbn = db.db(DB_FILE)
    dbn.query("SELECT id,titol,data_modificacio,color FROM notes "+where+" "+order)
    for row in dbn:
       self.resultat.append(Notes(id=row[0],titol=row[1],datam=row[2],color=row[3]))
    self.ls =[]
    current=0 #item seleccionat en la llista
    cont=0 #contador pel for
    for e in self.resultat: 
      icon = appuifw.Icon(unicode(DATA_PATH)+'\\iconescolors1.mif',int(e.get_color()),int(e.get_color()))
      if tipus=="rapid":   
        if self.notaSel.get_id()==e.get_id():
          current=cont
        t = (unicode(e),  icon)   
      if tipus=="detall":
        if time.localtime()[0] == 12 and time.localtime()[1]==12 and time.localtime()[2]:
           a=1
        #data i hora actual, paso de timestamp a datetime.
        diaActual = datetime.datetime.fromtimestamp(time.time())
        #data i hora de la nota, tambe estava en timestamp (que es un float)
        diaNota = datetime.datetime.fromtimestamp(e.dataModificacio)
        #si es del mateix dia mostro hh:mm
        if diaActual.year == diaNota.year and diaActual.month == diaNota.month and diaActual.day == diaNota.day:
          dia = str(diaNota.hour)+":"+str(diaNota.minute)
        #si no es davui mostro dd/mm/aaaa
        else:
          dia = str(diaNota.day)+"/"+str(diaNota.month)+"/"+str(diaNota.year)
        if self.notaSel.get_id()==e.get_id():
          current=cont
        t = (unicode(e), unicode(dia), icon)   
      self.ls.append(t)
      cont=cont+1
    #MENUS
    menuBuit = [(self.labels.loc.nova_nota,self.formAfegir)]
    menuNormal = [(self.labels.loc.visualitzar,self.visualitzar),(self.labels.loc.nova_nota,self.formAfegir),
      (self.labels.loc.editar,self.formEditar),(self.labels.loc.eliminar,self.eliminar)]
    menuOpcions = [(self.labels.loc.opcions,self.llistatOpcions)]
    menuSobre = [(self.labels.loc.sobre,self.sobre)]
    menuSincronitzar = [(self.labels.loc.sincronitzar,self.sincronitzar),(self.labels.loc.reset,self.resetSinc)]
    menuOrder=[(self.labels.loc.ordenar,(
        (self.labels.loc.color, lambda:self.ordenar('color')),
        (self.labels.loc.titol, lambda:self.ordenar('titol')),
        (self.labels.loc.data, lambda:self.ordenar('data'))))]
    menuFiltrar=[(self.labels.loc.filtrar,(
        (self.labels.loc.titol,lambda:self.buscarTitol()),
        (self.labels.loc.color,lambda:self.filtrarColors()),
        ))]
    menuDesFiltrar=[(self.labels.loc.desfiltrar,self.desfiltrarTitol)]

    if not self.ls:
      self.lb = appuifw.Listbox([self.labels.loc.buit])
      if self.titolActual:
        appuifw.app.menu = menuBuit+menuDesFiltrar+menuOpcions+menuFiltrar+menuFiltrar+menuSincronitzar+menuSobre
      else:
        appuifw.app.menu = menuBuit+menuOpcions+menuFiltrar+menuSincronitzar+menuSobre    
    else:
      self.lb = appuifw.Listbox(self.ls)
      self.lb.set_list(self.ls,current)
      self.lb.bind(key_codes.EKeySelect, lambda: self.visualitzar())
      self.lb.bind(key_codes.EKeyBackspace, lambda: self.eliminar())
      if self.titolActual:
        appuifw.app.menu = menuNormal+menuFiltrar+menuDesFiltrar+menuOrder+menuOpcions+menuSincronitzar+menuSobre
      else:
        appuifw.app.menu = menuNormal+menuFiltrar+menuOrder+menuOpcions+menuSincronitzar+menuSobre
    appuifw.app.body = self.lb
    
  def desfiltrarTitol(self):
    self.titolActual= ""
    self.refrescar()
    
  def ordenar(self,campOrdre):
    self.ordreActual=campOrdre
    self.refrescar()
  def buscarTitol(self):
    self.titolActual = appuifw.query(self.labels.loc.buscar_titol, "text")
    self.refrescar()
  
  def llegirOpcionsGenerals(self):
    config = ConfigParser()
    config.read(DATA_PATH+"\\general.cfg")
    self.llistat = int(config.get("interficie", "llistat"))
    self.idioma = config.get("interficie","idioma")
    self.orderc = config.get("interficie","ordre")
    self.blau = config.get("interficie","blau")
    self.groc = config.get("interficie","groc")
    self.verd = config.get("interficie","verd")
    self.vermell = config.get("interficie","vermell")
    self.update_locale(self.idioma)
    
  def refrescar(self):
    #self.windowVisualitzarBottom.remove_image(self.bgColor)
    #self.windowVisualitzarTop.remove_image(self.bgColor)
    self.windowVisualitzarBottom.hide()
    self.windowVisualitzarTop.hide()
    self.windowColor.hide()
    self.llegirOpcionsGenerals()
    if self.ordreActual=="-1":
      self.ordreActual=self.orderc
    
    #ORDER de la consulta sql
    if self.ordreActual=="color":
      self.order=u' order by color '
    elif self.ordreActual =="titol":
      self.order =u' order by titol '
    elif self.ordreActual =="data":
      self.order=u' order by data_modificacio DESC'
     
    #WHERE de la consulta sql
    e1 = []    
    where="where ("
    #colors
    if self.colorBlauActual=="-1" and self.blau=='1':
      where=where+" color=16384 OR"
      self.colorBlauActual="1"
      e1.append(0)
    elif self.colorBlauActual=='1' and self.colorBlauActual!='0':
      where=where+" color=16384 OR"
      e1.append(0)
      self.colorBlauActual="1"
    else:
      self.colorBlauActual="0"
      
    if self.colorGrocActual=="-1" and self.groc=='1':
      where=where+" color=16386 OR"
      e1.append(1)
      self.colorGrocActual="1"
    elif self.colorGrocActual=='1' and self.colorGrocActual!='0':
      where=where+" color=16386 OR"
      e1.append(1)
      self.colorGrocActual="1"
    else:
      self.colorGrocActual="0"
    
    if self.colorVerdActual=="-1" and self.verd=='1':
      where=where+" color=16388 OR"
      e1.append(2)
      self.colorVerdActual="1"
    elif self.colorVerdActual=='1' and self.colorVerdActual!='0':
      where=where+" color=16388 OR"
      e1.append(2)
      self.colorVerdActual="1"
    else:
      self.colorVerdActual="0"
    
    if self.colorVermellActual=="-1" and self.vermell=='1':
      where=where+" color=16390 OR"
      e1.append(3)
      self.colorVermellActual="1"
    elif self.colorVermellActual=='1' and self.colorVermellActual!='0':
      where=where+" color=16390 OR"
      e1.append(3)
      self.colorVermellActual="1"
    else:
      self.colorVermellActual="0"
    
    if len(e1)==0:
      self.where=" where color=0 "
    else:
      self.where=where[:-2]+") "
    
    #titol
    if self.titolActual:
          self.where=self.where+" AND titol like '*"+self.titolActual+"*'"
    
    #tupla de colors actius
    self.tuplaColorsActius=e1
    
    if self.llistat == 0:
      self.llistar('rapid', where=self.where, order=self.order)
    if self.llistat == 1:
      self.llistar('detall',where=self.where, order=self.order)
    appuifw.app.exit_key_handler = quit
   
  #editar configuracio
  def llistatOpcions(self):
    self.llegirOpcionsGenerals() #obtenir opcions de la interficie (colors i ordre)
    self.colorBlauActual=self.blau
    self.colorGrocActual=self.groc
    self.colorVerdActual=self.verd
    self.colorVermellActual=self.vermell
    self.ordreActual=self.orderc
    
    appuifw.app.exit_key_handler = lambda:self.refrescar()
    opcions= [self.labels.loc.generals,self.labels.loc.sincronitzacio]
    self.lbOpcions=appuifw.Listbox(opcions)
    self.lbOpcions.bind(key_codes.EKeySelect, lambda: self.opcions())
    appuifw.app.menu = [(self.labels.loc.obrir,self.opcions),(self.labels.loc.tancar,self.refrescar)]
    appuifw.app.body=self.lbOpcions
    
    
  def opcions(self):
    opcio = self.lbOpcions.current()
    if opcio==0:
      self.editarOpcionsGenerals() 
    if opcio==1:
      self.editarOpcionsSincronitzacio()  
    else:
      self.llistatOpcions()
    
  def editarOpcionsGenerals(self):
    config = ConfigParser()
    config.read(DATA_PATH+"\\general.cfg")
    llistat = config.get("interficie", "llistat")
    idioma = config.get("interficie","idioma")
    ordre = config.get("interficie","ordre")
    blau = config.get("interficie","blau")
    groc = config.get("interficie","groc")
    verd = config.get("interficie","verd")
    vermell = config.get("interficie","vermell")
    
    ordresCodiEnum = { 'data': 0, 'titol': 1, 'color':2}
    ordres=[self.labels.loc.order_data,self.labels.loc.order_titol,self.labels.loc.order_color]
    
    tipus=[self.labels.loc.rapid,self.labels.loc.detallat]
    
    idiomesCodiEnum = { 'ca': 0, 'es': 1, 'en':2}
    idiomes=[self.labels.loc.catala,self.labels.loc.castella,self.labels.loc.angles]
    
    colorsSiNo = [self.labels.loc.no,self.labels.loc.si]
    
    data=[(self.labels.loc.tipus,'combo',
           (tipus,int(llistat)))
          ,(self.labels.loc.idioma,'combo'
            ,(idiomes,idiomesCodiEnum[str(idioma)])),
            (self.labels.loc.ordre,'combo'
            ,(ordres,ordresCodiEnum[str(ordre)])),
            (self.labels.loc.blau,'combo'
            ,(colorsSiNo,int(blau))),
            (self.labels.loc.groc,'combo'
            ,(colorsSiNo,int(groc))),
            (self.labels.loc.verd,'combo'
            ,(colorsSiNo,int(verd))),
            (self.labels.loc.vermell,'combo'
            ,(colorsSiNo,int(vermell)))
            ]
    flags=appuifw.FFormEditModeOnly
    form=appuifw.Form(data, flags)
    form.save_hook=self.guardarOpcionsGenerals
    form.execute()
    return True
      
  def guardarOpcionsGenerals(self,form):
    config = ConfigParser()
    config.add_section("interficie")
    config.set("interficie", "llistat", form[0][2][1])
    idiomesCodi= { 0: 'ca', 1: 'es', 2:'en'}
    ordresCodi = { 0: 'data', 1: 'titol', 2:'color'}
    config.set("interficie", "idioma", idiomesCodi[int(form[1][2][1])])
    config.set("interficie", "ordre", ordresCodi[int(form[2][2][1])])
    config.set("interficie", "blau", (form[3][2][1]))
    config.set("interficie", "groc", (form[4][2][1]))
    config.set("interficie", "verd", (form[5][2][1]))
    config.set("interficie", "vermell", (form[6][2][1]))
    f = open(DATA_PATH+'\\general.cfg', 'wb')
    config.write(f)
    f.close()
      
  def editarOpcionsSincronitzacio(self):
    config = ConfigParser()
    config.read(DATA_PATH+"\\sincronitzacio.cfg")
    usuari = config.get("sincronitzacio", "usuari")
    password = config.get("sincronitzacio", "password")
    host = config.get("sincronitzacio", "host")
    #mostro el camp del password en ***** si no esta buit,
    #ja que no suporta camps de tipus password.
    if password=="":
      campPassword=""
    else:
      campPassword="*****"   
    data=[(self.labels.loc.usuari,'text', unicode(usuari)),(self.labels.loc.password,'text', unicode(campPassword)),
    (self.labels.loc.host,'text',unicode(host))]
    flags=appuifw.FFormEditModeOnly+appuifw.FFormDoubleSpaced
    form=appuifw.Form(data, flags)
    form.save_hook=self.guardarOpcionsSincronitzacio
    form.execute()
    return True

  def guardarOpcionsSincronitzacio(self,form):
    config = ConfigParser()
    #si es canvia el password sagafa el nou, sino es deixa el mateix
    if unicode(form[1][2])!="*****":
      campPassword= form[1][2]
    else:
      configObtenir = ConfigParser()
      configObtenir.read(DATA_PATH+"\\sincronitzacio.cfg")
      campPassword = configObtenir.get("sincronitzacio", "password")
    config.add_section("sincronitzacio")
    config.set("sincronitzacio", "usuari", form[0][2])
    config.set("sincronitzacio", "password", unicode(str(campPassword)))
    config.set("sincronitzacio", "host", form[2][2])
    f = open(DATA_PATH+'\\sincronitzacio.cfg', 'wb')
    config.write(f)
    f.close()

  def agafarColors(self):
    colorsSeleccionats = self.selBox.cb_return()
    #color blau
    self.colorBlauActual="0"
    self.colorGrocActual="0"
    self.colorVerdActual="0"
    self.colorVermellActual="0"
    for i in range(len(colorsSeleccionats)):
      if colorsSeleccionats[i]==0:
        self.colorBlauActual="1"
      if colorsSeleccionats[i]==1:
        self.colorGrocActual="1"
      if colorsSeleccionats[i]==2:
        self.colorVerdActual="1"
      if colorsSeleccionats[i]==3:
        self.colorVermellActual="1"
    self.refrescar()
    
  def filtrarColors(self):
    applock=e32.Ao_lock()   
        
    colors = [self.labels.loc.blau, self.labels.loc.groc, self.labels.loc.verd, self.labels.loc.vermell]
    self.selBox = selectionBox.selectbox(colors,self.tuplaColorsActius)
    self.selBox.menu_list3()
    appuifw.app.menu =  [(u"Seleccionar", self.selBox.cb_select),(u"Enrera", self.agafarColors)]
    appuifw.app.exit_key_handler = self.agafarColors
    applock.wait() 
  def llegirOpcionsSincronitzacio(self):
    config = ConfigParser()
    config.read(DATA_PATH+"\\sincronitzacio.cfg")
    self.password = config.get("sincronitzacio", "password")
    self.usuari = config.get("sincronitzacio","usuari")
    self.host = config.get("sincronitzacio","host")
  def sel_access_point(self):
    """ Select the default access point.
        Return True if the selection was done or False if not
    """
    aps = socket.access_points()
    if not aps:
        note(u"No access points available","error")
        return None
 
    ap_labels = map(lambda x: x['name'], aps)
    item = appuifw.popup_menu(ap_labels,u"Access points:")
    if item is None:
        return None
 
    apo = socket.access_point(aps[item]['iapid'])
    socket.set_default_access_point(apo)
    return apo

  def resetSinc(self):
    llistaResetSinc = [self.labels.loc.reset_client, self.labels.loc.reset_server]
    opcioResetSinc = appuifw.selection_list(choices=llistaResetSinc , search_field=0)
    #server to client
    if opcioResetSinc == 0:
      self.sincronitzar("client")
    #client to server
    elif opcioResetSinc ==1:
      self.sincronitzar("server")
      
  def sincronitzar(self,reset=""):
   
    import sincronitzar
    self.apo = self.sel_access_point()
    if self.apo:
      self.apo.start()
      self.llegirOpcionsSincronitzacio()
      #ENVIAR peticio, esperar resposta servidor
      sync = sincronitzar.sincronitzar(self.usuari,self.password,self.host)
      #Solicitud de sincronitzacio
      resposta = sync.solicitudEstat()
      
      #usuari no autentificat correctament
      if resposta['sync']['cos']['accions']['codi']==10:
        sync.finalitzarError(u"Bad Credentials")
      #url incorrecte
      if resposta['sync']['cos']['accions']['codi']==11:
        sync.finalitzarError(u"Incorrect Host")
      
      if reset!="":
        if reset=="client":
          resposta = sync.solicitudCosResetClient()
          resposta = sync.solicitudMapa(resposta)
          sync.guardarUltimaSinc(resposta['guardarSyncClient'])
        elif reset=="server":
          
            resposta = sync.solicitudCosResetServer()
            resposta = sync.solicitudMapa(resposta)
            sync.guardarUltimaSinc(resposta['guardarSyncClient'])
      else:
        #sinc inicial  
        if resposta['sync']['cos']['accions']['codi']==101:
          resposta = sync.solicitudCosSyncInicial()
          resposta = sync.solicitudMapa(resposta)
          sync.guardarUltimaSinc(resposta['guardarSyncClient'])
        #sinc normal
        elif resposta['sync']['cos']['accions']['codi']==102:
          resposta = sync.solicitudCos()
          resposta = sync.solicitudMapa(resposta)
          sync.guardarUltimaSinc(resposta['guardarSyncClient'])
      self.refrescar()

  #sortir del programa
  def quit(self):
    app_lock.signal()

  #crear directori de fitxers
  def comprovarDirectori(self):
    global DATA_PATH;
    global DB_FILE;
    if e32.in_emulator():
      if e32.pys60_version_info[0] == 1 and e32.pys60_version_info[1] < 5:
        DATA_PATH = 'c:\\python\\PySyncNotes'
        DB_FILE = 'c:\\python\\PySyncNotes\\fitxers.db'
      else:
        DATA_PATH = 'c:\\Data\\python\\PySyncNotes'
        DB_FILE = 'c:\\Data\\python\\PySyncNotes\\fitxers.db'
    else:
      activat=1
      #crea base de dades on hi ha fitxers instalació
      if activat==1:
        DEFDIR = u"c:\\python"
        for d in e32.drive_list():
          appd = os.path.join(d,u"\\data\\python\\PySyncNotes")
          if os.path.exists(os.path.join(appd,u"notes.py")):
            DATA_PATH = appd
            DB_FILE = appd+"\\fitxers.db"
            break
      #crea base de dades en la targeta memoria si pot ser.
      else:
        drive = 'e'
        if os.path.exists('e:'):
          drive = 'e'
          DATA_PATH = 'e:\\Data\\python\\PySyncNotes\\'
          DB_FILE = 'e:\\Data\\python\\PySyncNotes\\fitxers.db'
        elif os.path.exists('c:'):
          drive = 'c'
          DATA_PATH = 'c:\\Data\\python\\PySyncNotes\\'
          DB_FILE = 'C:\\Data\\python\\PySyncNotes\\fitxers.db'
        try:
          os.makedirs('%s:\\Data\\python\\PySyncNotes' % drive)
        except: pass
      #also add current script path (if we are running from a sis file)
      sys.path.insert(0,os.getcwd()) #not 100% sure this is needed
    sys.path = sys.path + [DATA_PATH]
    if not os.path.exists(DATA_PATH+'\\files'):
      os.mkdir(DATA_PATH+'\\files')
    if not os.path.exists(DB_FILE):
      #file(DB_FILE, "w+")
      
      dbn = db.db(DB_FILE)
      dbn.query("create table notes (id counter, titol varchar, text LONG VARCHAR,color INTEGER,data_modificacio DATE)")
      dbn.query("create table sync_contingut (id_sync_contingut	counter, apli_db varchar, uid_contingut	INTEGER, data_creacio DATE, data_modificacio DATE,data_esborrat DATE)")
      dbn.query("create table sync_resum (apli_db varchar, last_sync date,error INTEGER)")

      #fitxer configuracio sinc
      config = ConfigParser()
      config.add_section("sincronitzacio")
      config.set("sincronitzacio", "usuari", "")
      d = { 2: 'en', 1: 'es', 0:'ca'}
      idiomes=[u"Catala",u"Espanol",u"English"]
      idiomes.sort
      self.idiomaSel = appuifw.popup_menu(idiomes, u"Select language:")
      if self.idiomaSel!=None:
        self.idioma=d[int(self.idiomaSel)]
      else:
        self.idioma=d[0]
      config.set("sincronitzacio", "password", "")
      config.set("sincronitzacio", "host", "http://pysyncnotes.tk/sync.php")
      f = open(DATA_PATH+'\\sincronitzacio.cfg', 'wb')
      config.write(f)
      f.close()
      
      #fitxer configuracio general
      config = ConfigParser()
      config.add_section("interficie")
      config.set("interficie", "llistat", "0")
      config.set("interficie","idioma",str(self.idioma))
      config.set("interficie","ordre","data")
      config.set("interficie","blau","1")
      config.set("interficie","groc","1")
      config.set("interficie","verd","1")
      config.set("interficie","vermell","1")
      f = open(DATA_PATH+'\\general.cfg', 'wb')
      config.write(f)
      f.close()