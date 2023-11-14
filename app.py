from datetime import datetime
from src.lib.appwrapper import *
from whoosh.fields import Schema, TEXT, KEYWORD, DATETIME, ID, STORED, NUMERIC
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup

class App(AppWrapper):
    def __init__(self):
        self.agenda = {}

        super().__init__(rootDir= os.path.dirname(os.path.abspath(__file__)),
            title="Práctica de Whoosh 3",
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
                            label = 'Título o Sinopsis',
                            callback = self.searchTitulo
                        ),
                        MenuTabItem(
                            label = 'Géneros',
                            callback = self.searchGenero
                        ),
                        MenuTabItem(
                            label = 'Fecha',
                            callback = self.searchFecha
                        ),
                        MenuTabItem(
                            label = 'Modificar fecha',
                            callback = self.searchModifyFecha
                        )
                    ]
                )
            ],
            components=[],
            schema=Schema(
                titulo=TEXT(stored=True, phrase=False),
                titulo_original=TEXT(stored=True, phrase=False),
                fecha_estreno=DATETIME(stored=True),
                paises=KEYWORD(stored=True, commas=True, lowercase=True),
                generos=KEYWORD(stored=True, commas=True, lowercase=True),
                directores=KEYWORD(stored=True, commas=True, lowercase=True),
                sinopsis=TEXT(stored=True, phrase=False),
                url=ID(stored=True, unique=True)
            )
        )

    def store(self):
        def addData(writter, docsDir, doc):
            writter.add_document(
                titulo=str(doc[0]),
                titulo_original=str(str(doc[1])),
                fecha_estreno=datetime.datetime.strptime(doc[2], '%d/%m/%Y'),
                paises=str(doc[3]),
                generos=str(doc[4]),
                directores=str(doc[5]),
                sinopsis=str(doc[6]),
                url=str(doc[6])
            )

        def scrappeData():
            baseUrl = 'https://www.elseptimoarte.net'
            itemArray = []

            for urlIndex in range(1, 2):
                scrapper = Scrapper(f'https://www.elseptimoarte.net/estrenos/{urlIndex}/').get()

                items = scrapper.select('#collections > ul.elements > li')

                for i in items:
                    url = i.select_one('h3 > a')['href'].strip()

                    scrapper2 = Scrapper(baseUrl + url).get()
                    titulo = scrapper2.textIfExists(scrapper2.selectOne('#content > section.highlight:nth-child(2) dl > dd:nth-child(2)')).strip()
                    titulo_original = scrapper2.textIfExists(scrapper2.selectOne('#content > section.highlight:nth-child(2) dl > dd:nth-child(4)')).strip()
                    titulo_original = scrapper2.textIfExists(scrapper2.selectOne('#content > section.highlight:nth-child(2) dl > dd:nth-child(4)')).strip()
                    fecha_estreno = scrapper2.textIfExists(scrapper2.selectOne('#content > section.highlight:nth-child(2) dl > dd:nth-child(8)')).strip()
                    paises = scrapper2.textIfExists(scrapper2.selectOne('#content > section.highlight:nth-child(2) dl > dd:nth-child(6)')).strip()
                    generos = scrapper2.textIfExists(scrapper2.selectOne('#datos_pelicula > .categorias')).strip()
                    directores = scrapper2.textIfExists(scrapper2.selectOne('#content > section.highlight:nth-child(2) dl > dd:nth-child(18)')).strip()
                    sinopsis = scrapper2.textIfExists(scrapper2.selectOne('#content > section.highlight:nth-child(3) .info')).strip()

                    itemArray.append((
                        titulo,
                        titulo_original,
                        fecha_estreno,
                        paises,
                        generos,
                        directores,
                        sinopsis
                    ))

            res, err = self.whoosh.createIndex(addDoc=addData, docs=itemArray)

            if len(err) == 0:
                messagebox.showinfo("Fin de indexado", "Se han indexado "+str(res)+ " elementos")   
            else:
                messagebox.showerror("Error", err)


        respuesta = messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere recargar los datos. \nEsta operación puede ser lenta")
        if respuesta:
            scrappeData()

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
                "TITULO ORIGINAL": 'titulo_original',
                "DIRECTOR": 'directores'
            }, results)

        def search(param, window):
            def query(ix):
                return MultifieldParser(['titulo', 'sinopsis'], ix.schema, group=OrGroup).parse(str(param))
            
            self.whoosh.rawQuery(query=query, callback=showList)

        newWindow = self.gui.formWindow(title="Buscar top 10 películas según título o sinopsis", components = [{
            'type': 'label',
            'text': 'Introduzca consulta: ',
            'side': 'left'
        }, {
            'type': 'text',
            'func': search,
            'side': 'left',
            'width': 30
        }])

        newWindow.create()

    def searchGenero(self):
        def showList(results):
            self.showMapList({
                "TITULO": 'titulo',
                "TITULO ORIGINAL": 'titulo_original',
                "PAISES": 'paises'
            }, results)
    
        def createWindow(values):
            newWindow = self.gui.formWindow(title="Buscar mensajes según cuerpo", components = [{
                'type': 'label',
                'text': 'Selecciona género: ',
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
            self.whoosh.query('generos', param, showList, 20)

        self.whoosh.getValuesList('generos', callback=createWindow)

    def searchFecha(self):
        def showList(results):
            self.showMapList({
                "TITULO": 'titulo',
                "FECHA": 'fecha_estreno'
            }, results, )

        def search(param, window):
            value = param.strip()

            if not re.match("\d{8}\s+\d{8}", value):
                messagebox.showinfo("ERROR", "Formato incorrecto AAAAMMDD")
            else:
                splitValue = value.split(' ')
                self.whoosh.query('fecha_estreno', '['+str(splitValue[0])+' + TO '+str(splitValue[1])+']', showList)

        newWindow = self.gui.formWindow(title="Buscar mensajes según precio", components = [{
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

    def searchModifyFecha(self):
        def searchModify(param, window):
            def showModifyList(values):
                listValues = []

                if len(values):
                    if messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere modificar las fechas de estrenos de estas peliculas?"):
                        for v in values:
                            newValue = {
                                'url': v['url'],
                                'titulo': v['titulo'],
                                'titulo_original': v['titulo_original'],
                                'fecha_estreno': datetime.datetime.strptime(str(fecha),'%Y%m%d'),
                                'paises': v['paises'],
                                'generos': v['generos'],
                                'directores': v['directores'],
                                'sinopsis': v['sinopsis']
                            }
                            self.whoosh.updateQuery(newValue)
                            listValues.append(newValue)

                self.showMapList({
                    'TITULO': 'titulo',
                    'FECHA DE ESTRENO': 'fecha_estreno'
                }, listValues)
        
            titulo = window.entryComponents[1].get().strip()
            fecha = window.entryComponents[3].get().strip()

            if not re.match("\d{8}", fecha):
                messagebox.showinfo("ERROR", "Formato incorrecto AAAAMMDD")
            else:
                self.whoosh.query('titulo', titulo, showModifyList)
     
        newWindow = self.gui.formWindow(title="Buscar juegos según jugadores", components = [{
            'type': 'label',
            'text': 'Título: ',
            'side': 'left'
        }, {
            'type': 'text',
            'side': 'left',
            'width': 30
        }, {
            'type': 'label',
            'text': 'Fecha AAAAMMDD:',
            'side': 'left'
        }, {
            'type': 'text',
            'side': 'left',
            'width': 15
        }, {
            'type': 'button',
            'func': searchModify
        }])

        newWindow.create()

# Lanza App
App()