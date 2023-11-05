from datetime import datetime
from src.lib.appwrapper import *
from whoosh.fields import Schema, TEXT, KEYWORD, DATETIME, ID, STORED, NUMERIC

class App(AppWrapper):
    def __init__(self):
        self.agenda = {}

        super().__init__(rootDir= os.path.dirname(os.path.abspath(__file__)),
            title="Práctica de Whoosh 2",
            menu=[
                MenuTab(
                    title = 'Datos',
                    items = [
                        MenuTabItem(
                            label = 'Cargar',
                            callback = self.store
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
                            label = 'Detalles',
                            callback = self.searchDetalles
                        ),
                        MenuTabItem(
                            label = 'Temáticas',
                            callback = self.searchTematicas
                        ),
                        MenuTabItem(
                            label = 'Precio',
                            callback = self.searchPrecio
                        ),
                        MenuTabItem(
                            label = 'Jugadores',
                            callback = self.searchJugadores
                        )
                    ]
                )
            ],
            components=[],
            schema=Schema(titulo=TEXT(stored=True, phrase=False), precio=NUMERIC(stored=True, numtype=float), tematicas=KEYWORD(stored=True, commas=True, lowercase=True), complejidad=ID(stored=True), jugadores=KEYWORD(stored=True, commas=True), detalles=TEXT)
        )

    def store(self):
        def addData(writter, docsDir, doc):
            writter.add_document(
                titulo=str(doc[0]),
                precio=float(str(doc[1])),
                tematicas=str(doc[2]),
                jugadores=str(doc[3]),
                complejidad=str(doc[4]),
                detalles=str(doc[5])
            )

        def scrappeData():
            productosArray = []

            for urlPaginacion in range(1, 3):
                scrapper = Scrapper(f'https://zacatrus.es/juegos-de-mesa.html?p={urlPaginacion}').get()

                productos = scrapper.select('ol.products > li')

                for p in productos:
                    titulo = p.select_one('strong.product.name > a').text.strip()
                    precio = scrapper.filterPrice(p.select_one('span.price').text).strip().replace(',', '.')
                    url = p.select_one('strong.product.name > a')['href'].strip()

                    scrapper2 = Scrapper(url).get()
                    tematicas = scrapper2.textIfExists(scrapper2.selectOne('.col[data-th="Temática"]')).strip()
                    jugadores = scrapper2.textIfExists(scrapper2.selectOne('.col[data-th="Núm. jugadores"]'), 'Desconocido').strip()
                    complejidad = scrapper2.textIfExists(scrapper2.selectOne('.col[data-th="Complejidad"]'), 'Desconocido').strip()
                    detalles = scrapper2.textIfExists(scrapper2.selectOne('#description')).strip()

                    productosArray.append((
                        titulo,
                        precio,
                        tematicas,
                        jugadores,
                        complejidad,
                        detalles
                    ))

                    
            res, err = self.whoosh.createIndex(addDoc=addData, docs=productosArray)

            if len(err) == 0:
                messagebox.showinfo("Fin de indexado", "Se han indexado "+str(res)+ " juegos")   
            else:
                messagebox.showerror("Error", err)


        respuesta = messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere recargar los datos. \nEsta operación puede ser lenta")
        if respuesta:
            scrappeData()


    def showList(self, results):
        content = []
        for row in results:
            content.append([
                'TÍTULO: ' + row['titulo'],
                'PRECIO: ' + str(row['precio']),
                'TEMATICAS: ' + row['tematicas'],
                'COMPLEJIDAD: ' + row['complejidad'],
                'JUGADORES: ' + row['jugadores']
            ])

        self.gui.listScrollWindow('Resultados', content)
    
    def searchDetalles(self):
        def search(param, window):
            self.whoosh.query('detalles', param, self.showList, limit=10)

        newWindow = self.gui.formWindow(title="Buscar top 10 juegos según detalles", components = [{
            'type': 'label',
            'text': 'Introduzca consulta en los detalles: ',
            'side': 'left'
        }, {
            'type': 'text',
            'func': search,
            'side': 'left',
            'width': 30
        }])

        newWindow.create()

    def searchTematicas(self):
        def createWindow(values):
            newWindow = self.gui.formWindow(title="Buscar mensajes según cuerpo", components = [{
                'type': 'label',
                'text': 'Introduzca consulta en el cuerpo: ',
                'side': 'left'
            }, {
                'type': 'spinbox',
                'values': values,
                'onChangeEvent': False,
                'func': search,
                'side': 'left',
                'width': 30
            }])

            newWindow.create()

        def search(param, window):
            self.whoosh.query('tematicas', param, self.showList)

        self.whoosh.getValuesList('tematicas', callback=createWindow)

    def searchPrecio(self):
        def search(param, window):
            value = param.strip()
            if not re.match('\d+\.\d+', value) and not re.match('\d+', value):
                messagebox.showinfo("ERROR", "Formato incorrecto (ddd.ddd)")
            else:
                self.whoosh.query('precio', '[TO '+str(value)+'}', self.showList)

        newWindow = self.gui.formWindow(title="Buscar mensajes según precio", components = [{
            'type': 'label',
            'text': 'Introduzca el precio máximo: ',
            'side': 'left'
        }, {
            'type': 'text',
            'func': search,
            'side': 'left',
            'width': 30
        }])

        newWindow.create()

    def searchJugadores(self):
        def createWindow(values):
            newWindow = self.gui.formWindow(title="Buscar juegos según jugadores", components = [{
                'type': 'label',
                'text': 'Número de jugadores: ',
                'side': 'left'
            }, {
                'type': 'spinbox',
                'values': values,
                'onChangeEvent': False,
                'func': search,
                'side': 'left',
                'width': 30
            }])

            newWindow.create()

        def search(param, window):
            value = param.strip()
            if not re.match('\d+', value) and not re.match('Desconocido', value) and not re.match('\+\d+', value):
                messagebox.showinfo("ERROR", "Formato incorrecto (dd)")
            else:
                self.whoosh.query('jugadores', value, self.showList)
     
        self.whoosh.getValuesList('jugadores', callback=createWindow)

# Lanza App
App()