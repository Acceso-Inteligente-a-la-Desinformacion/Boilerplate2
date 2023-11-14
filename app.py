from datetime import datetime
from src.lib.appwrapper import *
from whoosh.fields import Schema, TEXT, KEYWORD, DATETIME, ID, STORED, NUMERIC
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup, AndGroup

import locale
locale.setlocale(locale.LC_TIME, "es_ES")

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