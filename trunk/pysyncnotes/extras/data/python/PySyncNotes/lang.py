# -*- coding: utf-8 -*-

__all__ = [ "Locale" ]
 
class Loc_Data(object):
    "Translation data holder"
    pass
 
class Default(object):
    "Default language support"
    def __init__(self):
        self.loc = Loc_Data()
        self.loc.nova_nota = u'Nova nota'
        self.loc.visualitzar = u'Visualitzar'
        self.loc.editar = u'Editar'
        self.loc.eliminar = u'Eliminar'
        self.loc.opcions = u'Opcions'
        self.loc.sobre = u'Sobre..'
        self.loc.ordenar = u'Ordenar per..'
        self.loc.color = u'Color'
        self.loc.titol = u'Titol'
        self.loc.data = u'Data'
        self.loc.filtrar = u'Filtrar..'
        self.loc.desfiltrar = u'Treure filtre titol'
        self.loc.usuari = u'Usuari'
        self.loc.password = u'Password'
        self.loc.host = u'Host'
        self.loc.tipus = u'Tipus'
        self.loc.idioma = u'Idioma'
        self.loc.buscar_titol = u'Buscar per titol:'
        self.loc.filtrat = u'Titol Filtrat'
        self.loc.sobre_aplicacio = u'Sobre la aplicacio'
        self.loc.seleccionar_color = u'Selecciona color:'
        self.loc.blau = u'Blau'
        self.loc.verd = u'Verd'
        self.loc.groc = u'Groc'
        self.loc.vermell = u'Vermell'
        self.loc.eliminar_nota =u'Vols eliminar la nota: '
        self.loc.catala = u'Catala'
        self.loc.castella = u'Espanol'
        self.loc.angles = u'English'
        self.loc.guardar= u'Guardar'
        self.loc.canviar_titol= u'Canviar titol'
        self.loc.buit = u'<buit>'
        self.loc.data_modificacio= u'\nData Modificacio: '
        self.loc.seleccionar_idioma = u'Select language:'
        self.loc.rapid = u'rapid'
        self.loc.detallat= u'detallat'
        self.loc.obrir = u'Obrir'
        self.loc.tancar = u'Tancar'
        self.loc.generals = u'Generals'
        self.loc.sincronitzacio = u'Sincronitzacio'
        self.loc.versio = u'Versio'
        self.loc.order_color = u'Color'
        self.loc.order_titol = u'Titol'
        self.loc.order_data = u'Data'
        self.loc.ordre = u'Ordenar per'
        self.loc.si = u'Si'
        self.loc.no = u'No'
        self.loc.sincronitzar=u'Sincronitzar'
        self.loc.reset = u'Reset Sinc'
        self.loc.reset_client =u'Del servidor al client'
        self.loc.reset_server =u'Del client al servidor'
        
class Locale(Default):
    "Multiple language support class"
    
    LOC_MODULE = "lang_%s"
    
    def __init__(self,lang = ""):
        "Load all locale strings for one specific language or default if empty"        
        self.set_locale(lang)
 
    def set_locale(self,lang = ""):
        "Load all locale strings for one specific language or default if empty"
        Default.__init__(self)
 
        try:
            lang_mod = __import__( self.LOC_MODULE % ( lang ) )
        except ImportError:
            pass
        else:
            self.merge_locale(lang_mod)
        
    def merge_locale(self, lang_mod):
        "Merge new location string into default locale"
 
        # replace existing strings and keep old ones
        # if it is missing in the locale module
        for k,v in self.loc.__dict__.iteritems():
            if hasattr(lang_mod,k):
                nv = lang_mod.__getattribute__(k)
                self.loc.__setattr__(k,nv)
