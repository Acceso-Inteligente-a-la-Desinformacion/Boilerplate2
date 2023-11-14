# SEARCH ENGINE WHOOSH

from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, KEYWORD
from whoosh.qparser import QueryParser
from whoosh.index import create_in,open_dir, exists_in
from whoosh import query

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
