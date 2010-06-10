import db
import e32,os,os.path,e32db
import time
DEFDIR = u"c:\\python"
for d in e32.drive_list():
  appd = os.path.join(d,u"\\data\\python\\PySyncNotes")
  if os.path.exists(os.path.join(appd,u"notes.py")):
    DATA_PATH = appd
    DB_FILE = appd+"\\fitxers.db"
    
class Notes:
  #inicialitzador
  
  def __init__(self,id=0,titol="",desc="",datam="",color=16388):
    self.id = id
    self.titol = titol
    self.desc  = desc
    self.dataModificacio = datam
    self.color=color

  #cadena de text que representa l'objecte, mostrara el titul en fer str(obj)
  def __str__(self):
    return self.titol
  
  def get_color(self):
    return self.color
  #get titol
  def get_id(self):
    return self.id

  def get_dataModificacio(self):
    return self.dataModificacio

  #get titol
  def get_titol(self):
    return self.titol

  #get descripcio
  def get_desc(self):
    return self.desc

  def set_id(self, idn):
    self.id = idn

  def set_color(self,colorn):
    self.color=colorn
    
  def set_titol(self, titoln):
    self.titol = titoln

  def set_desc(self, descn):
    self.desc = descn


  def select_desc(self):
    dbn = db(DB_FILE)
    dbn.query("SELECT text from notes where  id = "+str(self.id))
    for row in dbn:
      self.desc= row[0]
    dbn.tancar()
  def inserir(self):
    np = NotesPersistent()
    np.write_db(self)
  def editar(self):
    np = NotesPersistent()
    np.update_db(self)
  def eliminar(self):
    np = NotesPersistent()
    np.delete_db(self)

  def ultimaSincronitzacio(self,dbsync):
    data= 0
    dbn = db.db(DB_FILE)
    dbn.query("SELECT last_sync FROM sync_resum where apli_db='"+dbsync+"'")
    for row in dbn:
      data =  row[0]
    return data

class NotesPersistent:
  def write_db(self,nota):
    dbn = db.db(DB_FILE)
    dbn.begin()
    existeixId=0;
    dbn.query("SELECT uid_contingut from sync_contingut where  apli_db = 'notes' ORDER BY uid_contingut ASC")
    for row in dbn:
      id= row[0]+1
      existeixId=1
    if existeixId==0:
      id=0
    dbn.query("INSERT INTO notes (id,titol,color, data_modificacio)"+
      "VALUES("+str(id)+",'"+nota.get_titol()+"',"+str(nota.get_color())+",#"+e32db.format_time(time.time())+"#)")
    dbn.query("SELECT id FROM notes ORDER BY id ASC")
    f = open(DATA_PATH+"\\files\\"+str(id), "wb")
    f.write(nota.get_desc().encode("utf-8"))
    f.close()
    for row in dbn:
      a= row[0]
    nota.set_id(a)
    dbn.query("INSERT INTO sync_contingut (apli_db, uid_contingut, data_creacio)"+
      "VALUES('notes',"+str(nota.get_id())+",#"+e32db.format_time(time.time())+"#)")
    dbn.commit()
    dbn.tancar()

  def update_db(self,nota):
    dbn = db.db(DB_FILE)
    dbn.begin()
    dbn.query("UPDATE notes SET titol = '"+nota.get_titol()+"', color="+str(nota.get_color())+
    ", data_modificacio=#"+e32db.format_time(time.time())+"#  WHERE "+
     " id = "+str(nota.get_id()))
    f = open(DATA_PATH+"\\files\\"+str(nota.get_id()), "wb")
    f.write(nota.get_desc().encode("utf-8"))
    f.close()
    dbn.query("UPDATE sync_contingut SET data_modificacio = #"+e32db.format_time(time.time())+"#"+
    " WHERE uid_contingut = "+str(nota.get_id())+" AND apli_db='notes'")
    dbn.commit()
    dbn.tancar()

  def delete_db(self,nota):
    dbn = db.db(DB_FILE)
    dbn.begin()
    dbn.query("DELETE FROM notes WHERE id="+str(nota.get_id())) 
    try:
      os.remove(DATA_PATH+"\\files\\"+str(nota.get_id())) 
    except os.error:
      pass
    dbn.query("SELECT data_creacio from sync_contingut where uid_contingut="+str(nota.get_id())+
    " AND  apli_db = 'notes'")
    for row in dbn:
      self.ultimaSincronitzacio('notes')
      data_creacio= row[0]
    #esborrar registres ja que encara no existeixen al servidor
    if int(data_creacio)>int(self.ultimaSincronitzacio('notes')):
      dbn.query("DELETE from sync_contingut where uid_contingut="+str(nota.get_id())+" AND apli_db='notes'")
    else:
      dbn.query("UPDATE sync_contingut SET data_esborrat = #"+e32db.format_time(time.time())+"#"+
      " WHERE uid_contingut = "+str(nota.get_id())+" AND apli_db='notes'")
    dbn.commit()
    dbn.tancar()
    
  def ultimaSincronitzacio(self,dbsync):
    data= 0
    dbn = db.db(DB_FILE)
    dbn.query("SELECT last_sync FROM sync_resum where apli_db='"+dbsync+"'")
    for row in dbn:
      data =  row[0]
    return data