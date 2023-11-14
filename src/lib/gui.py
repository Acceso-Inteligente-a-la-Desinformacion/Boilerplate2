from tkinter import *
from tkinter import messagebox

from typing import List

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