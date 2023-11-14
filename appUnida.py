from datetime import datetime
from whoosh.index import create_in,open_dir
from whoosh.index import create_in,open_dir, exists_in
from whoosh import query
from whoosh.fields import Schema, TEXT, KEYWORD, DATETIME, ID, STORED, NUMERIC
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup, AndGroup
import re

import sqlite3
import random
import datetime

from tkinter import *
from tkinter import messagebox

from typing import List

import locale
locale.setlocale(locale.LC_TIME, "es_ES")

from bs4 import BeautifulSoup
from urllib import request, parse

import re

import ssl, os
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl,'_create_unverified_context', None)):
    ssl._create_default_https_context=ssl._create_unverified_context

import shutil

import os

class SEW:
    def __init__(self, indexDir: str, schema: type(Schema)):

        self.indexDir = indexDir

        if not os.path.exists(self.indexDir):
            os.mkdir(self.indexDir)

        self.schema = schema

    def createIndex(self, addDoc: callable, docs = [], docsDir: str = None):
        def create():
            ix = create_in(self.indexDir, schema=self.schema)
            writer = ix.writer()

            i=0
            for doc in docs:

                if docsDir != None:
                    docPath = os.path.join(docsDir, doc)

                    if not os.path.isdir(docPath):
                        addDoc(writer, docsDir, doc)
                        i+=1
                else:
                    addDoc(writer, docsDir, doc)
                    i+=1
                    
            writer.commit()

            return i, ""
        
        if len(docs) and docsDir != None:
            docs = os.listdir(docsDir)
        
        if len(docs) == 0:
            return 0, "No hay documentos"
        else:
            if os.path.exists(self.indexDir):
                shutil.rmtree(self.indexDir)
            os.mkdir(self.indexDir)

            return create()
        
    def query(self, parameter, value, callback: callable = None, limit=None):
        ix=open_dir(self.indexDir)    
        with ix.searcher() as searcher:
            myquery = QueryParser(parameter, ix.schema).parse(str(value))
            results = searcher.search(myquery, limit=limit)
            if(callback != None):
                callback(results)
            return results

    def rawQuery(self, query: callable, callback: callable = None, limit=None):
        ix=open_dir(self.indexDir)    
        with ix.searcher() as searcher:
            results = searcher.search(query(ix), limit=limit)
            if(callback != None):
                callback(results)
            return results

    def updateQuery(self, item):
        ix=open_dir(self.indexDir)
        writer = ix.writer()
        writer.update_document(**item)
        writer.commit()
            
    def getAll(self, callback: callable):
        ix=open_dir(self.indexDir)
        with ix.searcher() as searcher:
            callback(searcher.search(query.Every()))

    def getValuesList(self, field, callback: callable):
        ix=open_dir(self.indexDir)   
        with ix.searcher() as searcher:
            results = [i.decode('utf-8') for i in searcher.lexicon(field)]
            callback(results)

class Scrapper:
    def __init__(self, url, type:str = "html.parser"):
        self.url = url
        self.type = type
    
    def post(self, data):
        data = parse.urlencode(data).encode()
        req =  request.Request(self.url, data=data)
        html = request.urlopen(req)
        self.soup = BeautifulSoup(html, self.type)
        return self
        
    def get(self):
        html = request.urlopen(self.url)
        self.soup = BeautifulSoup(html, self.type)
        return self

    def select(self, selector:str):
        return self.soup.select(selector)
    
    def selectOne(self, selector:str):
        return self.soup.select_one(selector)
    
    def find(self, element, className):
        return self.soup.find_all(element, {"class": className})
    
    def findOne(self, element, className):
        return self.soup.find(element, {"class": className})
    
    def filterPrice(self, text: str):
        return re.compile('\d+,\d+').search(text).group()
    
    def textIfExists(self, selector, default="Desconocido"):
        if(selector != None):
            return selector.text
        else:
            return default

class FormWindow:
    def __init__(self, title, components):
        self.components = components

        self.end = END

        self.entryComponents = []

        self.title = title

        self.root = Toplevel()

    def create(self):
        self.root.title(self.title)

        for c in self.components:
            # Parámetros opcionales
            if 'side' not in c.keys():
                c['side'] = LEFT

            if 'width' not in c.keys():
                c['width'] = 30

            if 'onChangeEvent' not in c.keys():
                c['onChangeEvent'] = True

            if 'func' not in c.keys():
                c['func'] = self.nullFunctionality

            # Función que devuelve el parámetro introducido en el input
            def create_func(component, entry, returnsValue=True):
                def func(param=None):
                    if returnsValue:
                        return component['func'](entry.get(), self)
                    else:
                        return component['func'](None, self)
                return func

            # Generador de formulario
            if c['type'] == 'label':
                entry = Label(self.root, text=c['text']).pack(side=c['side'])

            elif c['type'] == 'spinbox':
                entry = Spinbox(self.root, width=c['width'], values=c['values'])

                if c['onChangeEvent'] == True:
                    entry.configure(command=create_func(c, entry))

                entry.bind("<Return>", create_func(c, entry))
                entry.pack(side=LEFT)

            elif c['type'] == 'text':
                entry = Entry(self.root, width=c['width'])

                entry.bind("<Return>", create_func(c, entry))
                entry.pack(side=LEFT)

            elif c['type'] == 'button':
                if 'text' not in c.keys():
                    c['text'] = "Enviar"
            
                entry = Button(self.root, text=c['text'])
                entry.bind("<Button-1>", create_func(c, entry, False))
                entry.pack(side=LEFT)

            self.entryComponents.append(entry)

    def nullFunctionality(param, window):
        print('No has añadido ninguna funcionalidad a este componente')

class Component:
    def __init__(self, type, text, callback):
        self.type = type
        self.text = text
        self.callback = callback

# Elemento dentro de un menu
class MenuTabItem:
    def __init__(self, label, callback=None):
        self.label = label

        if callback == None:
            self.callback = self.showConsoleMessage
        else:
            self.callback = callback

    def showConsoleMessage(self):
        print('Esto es un mensaje en consola')

# Un nuevo apartado dentro del menu
class MenuTab:
    items = []

    def __init__(self, title, items: type(MenuTabItem) = []):
        self.title = title
        self.items = items

    def addTab(self, tab: type(MenuTabItem)):
        self.items.append(tab)

# Interfaz gráfica de la aplicación
class GUI:
    title = 'Untitled'

    def __init__(self):
        self.root = Tk()
        self.menubar = Menu(self.root)

    def addRootComponent(self, component):
        if component.type == 'frame':
            print('aunno')
        elif component.type == 'button':
            button = Button(self.root, text=component.text, command=component.callback)
            button.pack()

    def setTitle(self, title):
        self.title = title

    def addMenuTab(self, menutab: type(MenuTab)):
        menu = Menu(self.menubar)

        for item in menutab.items:
            menu.add_command(label=item.label, command=item.callback)

        self.menubar.add_cascade(label=menutab.title, menu=menu)

    def launch(self):
        self.root.title(self.title)
        self.root.config(menu=self.menubar)
        self.root.mainloop()

    def close(self):
        self.root.quit()

    def message(self, title, message):
        messagebox.showinfo(title, message)

    # Muestra en una nueva ventana con scroll el contenido
    def listScrollWindow(self, title, content: List[List[str]], width=150):
        v = Toplevel()
        v.title(title)
        sc = Scrollbar(v)
        sc.pack(side=RIGHT, fill=Y)
        lb = Listbox(v, width = 150, yscrollcommand=sc.set)

        for row in content:
            for r in row:
                lb.insert(END, r)
            lb.insert(END,"\n\n")

        lb.pack(side=LEFT,fill=BOTH)
        sc.config(command = lb.yview)

    def formWindow(self, title, components):
        return FormWindow(title, components)

class DbField:
    def __init__(self, name: str, type: str, min: int = 0, max: int = 1000):
        self.name = name.replace(' ', '_').upper()
        self.type = type
        self.min = min
        self.max = max
    
    def get(self):
        return f'{self.name.upper()} {self.type.upper()}'
    
    def exampleValue(self):
        if self.type.lower() == 'text':
            value = self.name.capitalize() + ' ' + str(random.randint(self.min, self.max))
        elif self.type.lower() == 'int':
            value = random.randint(self.min, self.max)
        elif self.type.lower() == 'date':
            value = datetime.datetime.now()

        return value
    
class DbTable:
    def __init__(self, name: str, fields: List[DbField]):
        self.name = name.lower().replace(' ', '_')
        self.fields = fields

class DB:
    def __init__(self, dbName: str, tables: List[DbTable] = [], enviorenment: str = 'prod'):

        self.dbName = dbName
        self.tables = tables
        
        self.connection = None

        self.enviorenment = enviorenment

        self.connect()
        self.createSchema()

    def getTable(self, tableName: str):
        for table in self.tables:
            if table.name == tableName:
                return table

    def rebuildSchema(self, env:str = 'dev'):
        for table in self.tables:
            if self.enviorenment == 'dev' and env == 'dev':
                self.dropTable(table.name, 'dev')
                self.createTable(table.name, 'dev')
                self.dummyData(table)

            self.dropTable(table.name)
            self.createTable(table.name)

    def createSchema(self):
        for table in self.tables:
            if self.enviorenment == 'dev':
                self.createTable(table.name, 'dev')
                self.dummyData(table)

            self.createTable(table.name)
        

    def dummyData(self, table: DbTable, quantity: int = 25):
        while(quantity > 0):
            data = []
            for field in table.fields:
                data.append(field.exampleValue())

            t = tuple(e for e in data)

            self.insert(table.name, t, 'dev')

            quantity -= 1

    def connect(self):
        connection = sqlite3.connect(self.dbName+'.db')
        connection.text_factory = str

        self.connection = connection

    def dropTable(self, tableName: str, env: str = 'prod'):
        table = self.getTable(tableName)

        if(env == 'dev'):
            appendName = f'_{env}'
        else:
            appendName = ''

        self.connection.execute("DROP TABLE IF EXISTS "+table.name+appendName)
        self.connection.commit()

    def closeConnection(self, env: str = 'prod'):
        self.connection.close()

    def exec(self, query: str, data: tuple = ()):

        #print(query)
        #print(data)

        if len(data):
            result = self.connection.execute(query, data)
        else:
            result = self.connection.execute(query)

        self.connection.commit()
        return result
    
    def createTable(self, tableName: str, env: str = 'prod'):
        table = self.getTable(tableName)
        
        if(env == 'dev'):
            appendName = f'_{env}'
        else:
            appendName = ''

        fieldsQuery = ""
        i = 1
        for field in table.fields:
            fieldsQuery += field.get() + (', ' if i<len(table.fields) else '')
            i += 1

        return self.exec("CREATE TABLE IF NOT EXISTS "+table.name+appendName+" ("+fieldsQuery+");")
    
    def insert(self, tableName: str, data: tuple, env: str = 'prod'):

        table = self.getTable(tableName)

        if(env == 'dev'):
            appendName = f'_{env}'
        else:
            appendName = ''
    
        variables = ''
        i = 1
        for field in table.fields:
            variables += '?' + (',' if i<len(table.fields) else '')
            i += 1

        return self.exec(f"INSERT INTO {table.name}{appendName} VALUES ({variables})", data)

    def countTable(self, tableName: str):
        return self.exec('SELECT COUNT(*) FROM '+tableName).fetchone()[0]

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


from whoosh.fields import NUMERIC

class App(AppWrapper):
    def __init__(self):
        self.agenda = {}

        super().__init__(rootDir= os.path.dirname(os.path.abspath(__file__)),
            title="Práctica de Whoosh 4",
            menu=[
                MenuTab(
                    title = 'Datos',
                    items = [
                        MenuTabItem(
                            label = 'Cargar',
                            callback = self.store
                        ),
                        MenuTabItem(
                            label = 'Listar',
                            callback = self.list
                        ),
                        MenuTabItem(
                            label = 'Salir',
                            callback = self.close
                        )
                    ]
                ),
                MenuTab(
                    title = 'Buscar',
                    items = [
                        MenuTabItem(
                            label = 'Título o Sinopsis',
                            callback = self.searchTitulo
                        ),
                        MenuTabItem(
                            label = 'Fecha',
                            callback = self.searchFecha
                        ),
                        MenuTabItem(
                            label = 'Buscar título y característica',
                            callback = self.searchCaracteristicasAndTitulo
                        )
                    ]
                )
            ],
            components=[],
            schema=Schema(
                titulo=TEXT(stored=True),
                comensales=NUMERIC(stored=True, numtype=int),
                autor=ID(stored=True),
                fecha=DATETIME(stored=True),
                caracteristicas=KEYWORD(stored=True, commas=True),
                introduccion=TEXT(stored=True)
            )
        )

    def store(self):
        def addData(writter, docsDir, doc):
            writter.add_document(
                titulo=str(doc[0]),
                comensales=str(str(doc[1])),
                autor=str(doc[2]),
                fecha=datetime.datetime.strptime(doc[3], "%d %B %Y"),
                caracteristicas=str(doc[4]),
                introduccion=str(doc[5])
            )

        def scrappeData():
            itemArray = []

            for urlIndex in range(1, 2):
                scrapper = Scrapper(f'https://www.recetasgratis.net/Recetas-de-Aperitivos-tapas-listado_receta-1_1.html').get()

                items = scrapper.select('.header-gap .resultados > div .resultado')

                for i in items:
                    url = i.select_one('.titulo')['href'].strip()

                    titulo = scrapper.textIfExists(i.select_one('.titulo')).strip()
                    comensales = scrapper.textIfExists(i.select_one('.property.comensales')).strip()
                    introduccion = scrapper.textIfExists(i.select_one('.intro')).strip()

                    scrapper2 = Scrapper(url).get()
                    autor = scrapper2.textIfExists(scrapper2.selectOne('.nombre_autor > a')).strip()
                    fecha = scrapper2.selectOne('.date_publish').text.strip().replace('Actualizado: ', '')
                    caracteristicas = scrapper2.textIfExists(scrapper2.selectOne('.recipe-info > .properties:nth-child(2)'), 'sin definir').replace('Características adicionales:', '')
                    caracteristicas = ",".join([c.strip() for c in caracteristicas.split(",")] )

                    itemArray.append((
                        titulo,
                        comensales,
                        autor,
                        fecha,
                        caracteristicas,
                        introduccion
                    ))

            res, err = self.whoosh.createIndex(addDoc=addData, docs=itemArray)

            if len(err) == 0:
                messagebox.showinfo("Fin de indexado", "Se han indexado "+str(res)+ " elementos")   
            else:
                messagebox.showerror("Error", err)


        respuesta = messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere recargar los datos. \nEsta operación puede ser lenta")
        if respuesta:
            scrappeData()

    def list(self):
        def showList(results):
            self.showMapList({
                'TITULO': 'titulo',
                'COMENSALES': 'comensales',
                'AUTOR': 'autor',
                'FECHA': 'fecha',
                'CARACTERISTICAS ADICIONALES': 'caracteristicas'
            }, results)

        self.whoosh.getAll(showList)

    def showMapList(self, mapResult, results):
        content = []
        for row in results:
            result = []

            for key, value in mapResult.items():
                result.append(f'{key}: '+str(row[value]))

            content.append(result)

        self.gui.listScrollWindow('Resultados', content)

    def searchTitulo(self):
        def showList(results):
            self.showMapList({
                "TITULO": 'titulo',
                "INTRODUCCION": 'introduccion'
            }, results)
        
        def search(param, window):
            self.whoosh.query('titulo', str(param), showList)

        newWindow = self.gui.formWindow(title="Buscar top 3 recetas según título", components = [{
            'type': 'label',
            'text': 'Introduzca título: ',
            'side': 'left'
        }, {
            'type': 'text',
            'func': search,
            'side': 'left',
            'width': 30
        }])

        newWindow.create()

    def searchFecha(self):
        def showList(results):
            self.showMapList({
                'TITULO': 'titulo',
                'NUMERO COMENSALES': 'comensales',
                'AUTOR': 'autor',
                'FECHA': 'fecha',
                'CARACTERÍSTICAS ADICIONALES': 'caracteristicas'
            }, results)

        def search(param, window):
            value = param.strip()

            if not re.match("\d{8}\s+\d{8}", value):
                messagebox.showinfo("ERROR", "Formato incorrecto AAAAMMDD AAAAMMDD")
            else:
                splitValue = value.split(' ')
                self.whoosh.query('fecha', '['+str(splitValue[0])+' + TO '+str(splitValue[1])+']', showList)

        newWindow = self.gui.formWindow(title="Buscar mensajes entre dos fechas", components = [{
            'type': 'label',
            'text': 'Introduzca rango de fechas AAAAMMDD AAAAMMDD: ',
            'side': 'left'
        }, {
            'type': 'text',
            'func': search,
            'side': 'left',
            'width': 30
        }])

        newWindow.create()

    def searchCaracteristicasAndTitulo(self):
        def showList(results):
            self.showMapList({
                'TITULO': 'titulo',
                'NUMERO COMENSALES': 'comensales',
                'AUTOR': 'autor',
                'FECHA ACTUALIZACION': 'fecha',
                'CARACTERISTICAS ADICIONALES': 'caracteristicas'
            }, results)

        def createWindow(values):
            def search(param, window):
                caracteristica = '"'+newWindow.entryComponents[1].get().strip()+'"'
                titulo = newWindow.entryComponents[3].get().strip()
                self.whoosh.query('titulo', 'caracteristicas:'+str(caracteristica)+ ' '+titulo, callback=showList, limit=10)

            newWindow = self.gui.formWindow(title="Buscar mensajes según cuerpo", components = [{
                'type': 'label',
                'text': 'Selecciona caracteristica: ',
                'side': 'left'
            }, {
                'type': 'spinbox',
                'values': values,
                'onChangeEvent': False,
                'func': search,
                'side': 'left',
                'width': 30
            }, {
                'type': 'label',
                'text': 'Introduce título: ',
                'side': 'left'
            }, {
                'type': 'text',
                'onChangeEvent': False,
                'width': 30
            }, {
                'type': 'button',
                'text': 'Aceptar',
                'func': search
            }])

            newWindow.create()

        self.whoosh.getValuesList('caracteristicas', createWindow)

# Lanza App
App()