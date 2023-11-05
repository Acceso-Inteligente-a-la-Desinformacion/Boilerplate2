from .gui import *
from .scrapper import *
from .db import *

from .sew import *

import re

class AppWrapper:
    def __init__(self, rootDir, title='Título de la interfaz gráfica', menu = [], components = [], schema=None):
        self.db = None

        self.dirs = {}
        self.dirs['root'] = rootDir
        self.dirs['data'] = os.path.join(self.dirs['root'], 'data')
        self.dirs['index'] = os.path.join(self.dirs['data'], 'Index')

        if schema:
            self.whoosh = SEW(indexDir=self.dirs['index'], schema=schema)

        self.gui = GUI() # Inicializa la interfaz gráfica
        self.gui.setTitle(title) # Asigna un título a la interfaz gráfica
        
        # Por cada elemento del menú en el método getMenu lo añade a la MenuBar de la interfaz gráfica
        for menutab in menu:
            self.gui.addMenuTab(menutab)

        # Por cada elemento definido en getMainComponents se añade un componente dentro de la ventana principal
        for component in components:
            self.gui.addRootComponent(component)

        self.gui.launch() # Lanza la interfaz gráfica

    def createIndex(self, docsDir: str, addDoc: callable):
        docsPath = os.path.join(self.dirs['data'], docsDir)

        if not len(os.listdir(self.dirs['index']))==0:
            respuesta = messagebox.askyesno("Confirmar","Indice no vacÃ­o. Desea reindexar?") 

            if respuesta:                
                res, err = self.whoosh.createIndex(docsDir=docsPath, addDoc=addDoc)
        else:
            res, err = self.whoosh.createIndex(docsDir=docsPath, addDoc=addDoc)

        if len(err):
            messagebox.showerror(err)
        else:
            messagebox.showinfo('Completado', f'Se han indexado {res} archivos.')

    def close(self):
        self.db.closeConnection() # Cierra la conexión con la base de datos
        self.gui.close() # Cierra la interfaz gráfica