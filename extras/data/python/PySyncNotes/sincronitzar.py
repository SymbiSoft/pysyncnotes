# -*- coding: utf-8 -*-
import urllib,httplib,appuifw,e32db,time,sys,os.path
import simplejson as json
import sysinfo
import e32
from urlparse import urlparse
from db import db
from nota import *
from TWProgressBar import TWProgressBar


DEFDIR = u"c:\\python"
for d in e32.drive_list():
  appd = os.path.join(d,u"\\data\\python\\PySyncNotes")
  if os.path.exists(os.path.join(appd,u"notes.py")):
    DATA_PATH = appd
    DB_FILE = appd+"\\fitxers.db"


class sincronitzar:
    
  def checkURL(self,url):
    p = urlparse(url)
    h = httplib.HTTPConnection(p[1])
    try:
      h.request('HEAD', p[2])
      res=h.getresponse()
      if res.status == 200: 
          return 1
      else: 
        return 0
    except:
      return 0
  
  def checkURL2(self,url):
    p = urlparse(url)
    h = httplib.HTTPConnection(p[1])
    h.request("GET", p[2])
    r1 = h.getresponse()
    data1 = r1.read()
    if data1=="Sync Activat":
      return 1
    else:
      return 0

  def __init__(self,usuari,password,host):
    self.comprovarUltimaSinc()
    self.usuari=usuari
    self.password=password
    self.host = host
    parts = urlparse(self.host)
    
    self.netloc=parts[1]
    self.path=parts[2]
    
    self.pb = TWProgressBar()
    self.pb.set_text(u"Initializing...")
    global i
    i = 0
    for i in range(5):
      self.pb.set_value(i)
    
  def ultimaSincronitzacio(self,dbsync):
    data= 0
    dbn = db.db(DB_FILE)
    dbn.query("SELECT last_sync FROM sync_resum where apli_db='"+self.dbsync+"'")
    for row in dbn:
      data =  row[0]
    return data
  def ultimaSincronitzacioExisteix(self,dbsync):
    data= -1
    dbn = db.db(DB_FILE)
    dbn.query("SELECT last_sync FROM sync_resum where apli_db='"+self.dbsync+"'")
    for row in dbn:
      data =  row[0]
    return data

  def capcalera(self):
    self.dbsync = "notes"
    self.servidor = self.host
    self.clientImei = sysinfo.imei()
    self.clientSw = sysinfo.sw_version()
    self.clientOs = sysinfo.os_version()

    capcalera = {}
    capcalera['msg'] = 1
    capcalera['auth'] = { 'usuari': self.usuari, 'password': self.password}
    capcalera['origen'] = self.clientImei
    capcalera['desti'] = self.servidor
    capcalera['sw'] = self.clientSw
    capcalera['os'] = self.clientOs

    return capcalera
  
  def solicitudMapa(self,resposta):
    #capcalera
    dadescon = {}
    dadescon['sync'] = {}
    dadescon['sync']['capcalera'] = self.capcalera()

    #cos
    dadescon['sync']['cos'] = {}
    dadescon['sync']['cos']['accions'] = self.accionsSincMapa()
    dadescon['sync']['cos']['mapa'] = self.crearMapa(resposta['sync']['cos']['sinc'],'notes');

    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    headers = {"Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
               "Accept": "text/plain"} 
    h= httplib.HTTPConnection(self.netloc)
    
    params = urllib.urlencode({'peticio'   : json.dumps(dadescon)})
    h.request("POST", self.path, params, headers)

    self.pb.set_text(u"Reciving...")
    for i in xrange(51,80):
      self.pb.set_value(i)
      i=i+1

    response = h.getresponse()
    resposta = json.loads(response.read());
    return resposta
  
  #Sync inicial
  def solicitudCosSyncInicial(self):
    self.resetUltimaSinc()
    #capcalera
    dadescon = {}
    dadescon['sync'] = {}
    dadescon['sync']['capcalera'] = self.capcalera()
    
    #cos
    dadescon['sync']['cos'] = {}
    dadescon['sync']['cos']['accions'] = self.accionsSincInicial()
    dadescon['sync']['cos']['sinc'] = self.construirSinc()

    headers = {"Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
               "Accept": "text/plain"}         
               
    h= httplib.HTTPConnection(self.netloc)
    params = urllib.urlencode({'peticio'   : json.dumps(dadescon)})
    h.request("POST", self.path, params, headers)

    self.pb.set_text(u"Sending...")
    for i in xrange(31,50):
      self.pb.set_value(i)
      i=i+1

    response = h.getresponse()
    resposta = json.loads(response.read());
    return resposta

  #Envia canvis del client al servidor i rebra la resposta dels canvis del servidor
  def solicitudCos(self):
    #poso a 0 ultima Sincronitzacio client.
    self.resetUltimaSinc()
   #capcalera
    dadescon = {}
    dadescon['sync'] = {}
    dadescon['sync']['capcalera'] = self.capcalera()
    
    #cos
    dadescon['sync']['cos'] = {}
    dadescon['sync']['cos']['accions'] = self.accionsSinc()
    dadescon['sync']['cos']['sinc'] = self.construirSinc()

    headers = {"Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
               "Accept": "text/plain"}         
               
    h= httplib.HTTPConnection(self.netloc)
    params = urllib.urlencode({'peticio'   : json.dumps(dadescon)})
    h.request("POST", self.path, params, headers)

    self.pb.set_text(u"Sending..")
    for i in xrange(31,50):
      self.pb.set_value(i)
      i=i+1

    response = h.getresponse()
    resposta = json.loads(response.read());
    return resposta

  #Envia canvis del client al servidor i rebra la resposta dels canvis del servidor
  def solicitudCosResetClient(self):
    self.resetUltimaSinc()
    #capcalera
    dadescon = {}
    dadescon['sync'] = {}
    dadescon['sync']['capcalera'] = self.capcalera()
    
    #cos
    dadescon['sync']['cos'] = {}
    dadescon['sync']['cos']['accions'] = self.accionsSincResetClient()
    dadescon['sync']['cos']['sinc'] = self.construirSinc()

    headers = {"Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
               "Accept": "text/plain"}            
    h= httplib.HTTPConnection(self.netloc)
    params = urllib.urlencode({'peticio'   : json.dumps(dadescon)})
    h.request("POST", self.path, params, headers)

    self.pb.set_text(u"Sending...")
    for i in xrange(31,50):
      self.pb.set_value(i)
      i=i+1

    response = h.getresponse()
    resposta = json.loads(response.read());
    return resposta

  def solicitudCosResetServer(self):
    self.resetUltimaSinc()
    #capcalera
    dadescon = {}
    dadescon['sync'] = {}
    dadescon['sync']['capcalera'] = self.capcalera()
    
    #cos
    dadescon['sync']['cos'] = {}
    dadescon['sync']['cos']['accions'] = self.accionsSincResetServer()
    dadescon['sync']['cos']['sinc'] = self.construirSinc()

    headers = {"Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
               "Accept": "text/plain"}         
               
    h= httplib.HTTPConnection(self.netloc)
    params = urllib.urlencode({'peticio'   : json.dumps(dadescon)})
    h.request("POST", self.path, params, headers)

    self.pb.set_text(u"Sending...")
    for i in xrange(31,50):
      self.pb.set_value(i)
      i=i+1

    response = h.getresponse()
    resposta = json.loads(response.read());
    return resposta

  def solicitudEstat(self):
    #capcalera
    dadescon = {}
    dadescon['sync'] = {}
    dadescon['sync']['capcalera'] = self.capcalera()

    #cos
    dadescon['sync']['cos'] = {}
    dadescon['sync']['cos']['accions'] = self.accionsEstat()

    headers = {"Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
               "Accept": "text/plain"} 
    if self.checkURL(self.host)==0 or self.checkURL2(self.host)==0:
      resposta = {}
      resposta['sync'] = {}
      resposta['sync']['cos']={}
      resposta['sync']['cos']['accions'] = {}
      resposta['sync']['cos']['accions']['codi']=11 
      
    else:
      h= httplib.HTTPConnection(self.netloc)
      params = urllib.urlencode({'peticio'   : json.dumps(dadescon)})
      h.request("POST", self.path, params, headers)
    
      self.pb.set_text(u"Authentication...")
      for i in xrange(6,30):
        self.pb.set_value(i)
        i=i+1

      response = h.getresponse()
      resposta = json.loads(response.read());
    return resposta

  def accionsEstat(self):
    accions = {}
    accions['codi']=50 #50 peticio
    accions['ultimaSync']=self.ultimaSincronitzacio(self.dbsync) #ultima sync
    accions['proximaSync']=time.time()  #sync actual
    self.proximaSinc = accions['proximaSync']
    accions['dbsync'] = self.dbsync
    return accions

  def accionsSinc(self):
    accions = {}
    self.codi=102
    accions['codi']=self.codi #102 sync normal
    accions['dbsync'] = self.dbsync
    return accions

  def accionsSincInicial(self):
    accions = {}
    self.codi=101
    accions['codi']=self.codi #101 sync inicial
    accions['dbsync'] = self.dbsync
    return accions
  
  def accionsSincResetClient(self):
    accions = {}
    self.codi=103 
    accions['codi']=self.codi #103 servidor sinc reset client
    accions['dbsync'] = self.dbsync
    return accions
  
  def accionsSincResetServer(self):
    accions = {}
    self.codi=104 
    accions['codi']=self.codi #104 client sinc reset server
    accions['dbsync'] = self.dbsync
    return accions

  def accionsSincMapa(self):
    accions = {}
    accions['codi']=150 #150 mapa
    accions['dbsync'] = self.dbsync
    return accions

  def afegirRegistre(self,dbName,id,titol,desc,color,dataCreacio):
    data = {}
    dbn = db.db(DB_FILE)
    idNota=0
    dbn.query("Select uid_contingut from sync_contingut where apli_db = '"+dbName+ "' ORDER BY uid_contingut ASC")
    for row in dbn:
      idNota=row[0]+1
    dbn.query("INSERT INTO notes (id,titol,color, data_modificacio)"+
    "VALUES("+str(idNota)+",'"+unicode(titol)+"',"+str(color)+",#"+e32db.format_time(float(dataCreacio))+"#)")
    f = open(DATA_PATH+"\\files\\"+str(idNota), "wb")
    f.write(desc.encode("utf-8"))
    f.close()
    dbn.query("INSERT INTO sync_contingut (apli_db, uid_contingut, data_creacio)"+
      "VALUES('"+dbName+"',"+str(idNota)+",#"+e32db.format_time(float(dataCreacio))+"#)")
    dbn.tancar()
    data['guid'] = id
    data['luid']=idNota
    return data
  
  def modificarRegistre(self,dbName,id,titol,desc,color,dataModificacio):
    dbn = db.db(DB_FILE)
    dbn.query("UPDATE notes SET titol = '"+unicode(titol)+"', color="+str(color)+
    ", data_modificacio=#"+e32db.format_time(float(dataModificacio))+"#  WHERE "+
     " id = "+str(id))
    f = open(DATA_PATH+"\\files\\"+str(id), "wb")
    f.write(desc.encode("utf-8"))
    f.close()
    dbn.query("UPDATE sync_contingut SET data_modificacio = #"+e32db.format_time(float(dataModificacio))+"#"+
    " WHERE uid_contingut = "+str(id)+" AND apli_db='notes'")
    dbn.tancar()
  def eliminarRegistre(self,dbName,id):
    dbn = db.db(DB_FILE)
    dbn.query("DELETE FROM notes WHERE id="+str(id))
    try:
      os.remove(DATA_PATH+"\\files\\"+str(id))
    except os.error:
      pass
    dbn.query("DELETE from sync_contingut where uid_contingut="+str(id)+" AND apli_db='notes'")
    dbn.tancar()
      

  def obtenirRegistresAfegits(self,ultimaSincServidor):
    canvis = []
    dbn = db.db(DB_FILE)
    #sinc inicial agafo tots
    if self.codi==101 or self.codi==104:
      dbn.query("Select uid_contingut from sync_contingut where data_esborrat IS NULL")
    elif self.codi==102:
      dbn.query("Select uid_contingut from sync_contingut where data_creacio > #"+e32db.format_time(float(ultimaSincServidor))+"#")  
    for row in dbn:
      id=row[0]
      dbn2 = db.db(DB_FILE)
      dbn2.query("Select titol,color from notes where id = "+str(id))
      f = open(DATA_PATH+"\\files\\"+str(id), "rb")
      descrow=f.read().decode("utf-8")
      f.close()
      
      for row2 in dbn2:
        canvis.append(Notes(id=id,titol=row2[0],desc=descrow,color=row2[1]))
     
    #sinc inicial, esborro tot
    if self.codi==101:
      dbn.query("Delete from sync_contingut")
      dbn.query("Delete from notes")
    return canvis

  def obtenirRegistresModificats(self,ultimaSincServidor):
    canvis = []
    dbn = db.db(DB_FILE)
    dbn.query("Select uid_contingut from sync_contingut where data_modificacio > #"+e32db.format_time(float(ultimaSincServidor))+
    "# AND data_creacio <= #"+e32db.format_time(float(ultimaSincServidor))+"#")
    for row in dbn:
      id=row[0]
      dbn2 = db.db(DB_FILE)
      dbn2.query("Select titol,color from notes where id = "+str(id))
      f = open(DATA_PATH+"\\files\\"+str(id), "rb")
      descrow=f.read().decode("utf-8")
      f.close()
      for row2 in dbn2:
        canvis.append(Notes(id=id,titol=row2[0],desc=descrow,color=row2[1]))
    return canvis

  def obtenirRegistresEliminats(self,ultimaSincServidor):
    canvis = []
    dbn = db.db(DB_FILE)
    dbn.query("Select uid_contingut from sync_contingut where data_esborrat > #"+e32db.format_time(float(ultimaSincServidor))+"# ")
    for row in dbn:
      id=row[0]
      canvis.append(Notes(id=id))
    dbn.query("delete from sync_contingut where data_esborrat > #"+e32db.format_time(float(ultimaSincServidor))+"# ")
    return canvis

  def construirSinc(self):
    sinc = {}
    sinc['afegir'] = []
    sinc['modificar'] = []
    sinc['eliminar'] = []
    if self.codi==103: #reset client, esborro tot el client
      dbn = db.db(DB_FILE)
      dbn.query("DELETE FROM notes")

      for the_file in os.listdir(DATA_PATH+"\\files"):
        file_path = os.path.join(DATA_PATH+"\\files", the_file)
        if os.path.isfile(file_path):
            os.remove(file_path)
      dbn.query("DELETE from sync_contingut where apli_db='notes'")
      dbn.tancar()
    else: #normal, inicil
      ultimaSincServidor = self.ultimaSincronitzacio(self.dbsync)
      afegits = []
      eliminats = []
      modificats = []
      afegits = self.obtenirRegistresAfegits(ultimaSincServidor)
      for reg in afegits:
        #diccionari que inclou la data de la nota
        data={}
        data['id'] = reg.get_id()
        data['titol']=reg.get_titol()
        data['color']=reg.get_color()
        data['desc'] = reg.get_desc().encode('utf-8')
        #afegir diccionari data a la llista afegir
        sinc['afegir'].append(data)
      if self.codi==102:
        eliminats = self.obtenirRegistresEliminats(ultimaSincServidor)
        for reg in eliminats:
          #diccionari que inclou nomes id de la nota ja que nomes sha desborrar del servidor
          data={}
          data['id'] = reg.get_id()
          #afegir diccionari 'data' a la llista 'eliminar'
          sinc['eliminar'].append(data)
        modificats=    self.obtenirRegistresModificats(ultimaSincServidor)
        for reg in modificats:
          #diccionari que inclou nomes lid de la nota ja que nomes sha desborrar del servidor
          data={}
          data['id'] = reg.get_id()
          data['titol']=reg.get_titol()
          data['color']=reg.get_color()
          data['desc'] = reg.get_desc()
          #afegir diccionari data a la llista eliminar
          sinc['modificar'].append(data)
    return sinc

  def crearMapa(self, elementsSinc,dbName):
    mapa = {}
    mapa['afegir'] = []
    for key in elementsSinc.iterkeys():
      if key=='afegir':
        for reg2 in elementsSinc[key]:
          data = self.afegirRegistre(dbName,reg2['id'],reg2['titol'],reg2['desc'],reg2['color'],self.proximaSinc)
          mapa['afegir'].append(data)
      elif key=='modificar':
        for reg2 in elementsSinc[key]:
           self.modificarRegistre(dbName,reg2['id'],reg2['titol'],reg2['desc'],reg2['color'],self.proximaSinc)
      elif key=='eliminar':
        for reg2 in elementsSinc[key]:
          self.eliminarRegistre(dbName,reg2['id'])
    return mapa
        
  def guardarUltimaSinc(self,ultimaSinc):
    if self.ultimaSincronitzacioExisteix('notes')==-1:
      dbn = db.db(DB_FILE)
      dbn.query("INSERT INTO sync_resum  (apli_db , last_sync,error ) values('notes',#"+e32db.format_time(float(ultimaSinc))+"#,0)") 
    else:
      dbn = db.db(DB_FILE)
      dbn.query("UPDATE sync_resum SET last_sync=#"+e32db.format_time(float(ultimaSinc))+"#, error=0 where apli_db='notes'")
    dbn.tancar()
    self.pb.set_text(u"Finishing...")
    for i in xrange(81,100):
      self.pb.set_value(i)
      i=i+1
    self.pb.close()
    del self.pb
   
  def resetUltimaSinc(self):
    if self.ultimaSincronitzacioExisteix('notes')==-1:
      dbn = db.db(DB_FILE)
      dbn.query("INSERT INTO sync_resum  (apli_db , last_sync, error ) values('notes',#"+e32db.format_time(float(0))+"#,1)") 
    else:
      dbn = db.db(DB_FILE)
      dbn.query("UPDATE sync_resum SET error=1 where apli_db='notes'")
    dbn.tancar()
    
  def comprovarUltimaSinc(self):
    data = 0
    dbn = db.db(DB_FILE)
    dbn.query("SELECT error FROM sync_resum where apli_db='notes'")
    for row in dbn:
      data =  row[0]
    if data==1:
      dbn.query("UPDATE sync_resum SET last_sync=#"+e32db.format_time(float(0))+"#, error=0 where apli_db='notes'")
    dbn.tancar()

  def finalitzarError(self,missatge):
     self.pb.set_text(unicode(missatge))
     e32.ao_sleep(5)
     self.pb.close()
     del self.pb