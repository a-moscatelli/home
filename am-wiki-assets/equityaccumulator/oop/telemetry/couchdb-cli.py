#!/usr/bin/env python
# coding: utf-8

# In[1]:


# docker pull couchdb:latest
# https://realpython.com/python-requests/
# https://docs.couchdb.org/en/stable/intro/tour.html
# https://docs.couchdb.org/en/stable/intro/security.html
# https://docs.couchdb.org/en/stable/intro/api.html
# https://www.uuidgenerator.net/dev-corner/python
# https://stackoverflow.com/questions/2150739/iso-time-iso-8601-in-python
# https://docs.couchdb.org/en/stable/http-routingtable.html
# https://docs.couchdb.org/en/stable/api/database/find.html#post--db-_find
#
# https://hub.docker.com/_/couchdb/
# ports: - "5984:5984" image: "couchdb:3.3.2"
# environment: COUCHDB_USER: am1   COUCHDB_PASSWORD: ampwd239


# In[2]:


import requests
#import uuid
import datetime
import socket


# In[3]:


class Couchdbcli:
    #urlz = 'http://127.0.0.1:5984/'
    urlc = 'http://am1:ampwd239@127.0.0.1:5984/logdb'
    #logdb = 'logdb'
    partitionid = 'tag'
    def __init__(self,urlc_):
        self.urlc=urlc_
        #devnull = self.getz()
    def getz(self):
        assert False
        # = curl http://127.0.0.1:5984/
        response = requests.get(self.urlz)
        #print(response.status_code)
        if True: response.raise_for_status()
        return response.json()
    def createdb(self,predelete):
        if predelete:
            #DELETE /{db}
            print('predelete',predelete)
            response = requests.delete(self.urlc) # , data={'key':'value'})
            print('predelete',predelete,'response.status_code',response.status_code)
        response = requests.put(self.urlc) # , data={'key':'value'})        
        # = curl -X PUT http://admin:password@127.0.0.1:5984/baseball
        # {"ok":true}
        return (response.status_code,response.json())
    def uuidhex__(self):
        assert False
        # also available: curl -X GET http://127.0.0.1:5984/_uuids
        myuuid = uuid.uuid4()
        if False: myuuids = str(myuuid) # 4aa79f59-4651-41c5-85b1-52adfe9511bc
        myuuidx = myuuid.hex # 4aa79f59465141c585b152adfe9511bc Convert a UUID to a 32-character hexadecimal string
        return myuuidx
    def getnow__(self):
        #Local to ISO 8601:
        localtm = datetime.datetime.now().isoformat() # 2020-03-20T14:28:23.382748
        # UTC to ISO 8601:
        utctm = datetime.datetime.utcnow().isoformat() # 2020-03-20T01:30:08.180856
        return utctm
    def log(self,tag,bodydict):
        # curl -X PUT http://admin:passwd@127.0.0.1:5984/db1/6e1295ed6c29495e54cc05947f18c8af -d '{"T":"There","a":"Foo"}'
        payload = {'datetime':self.getnow__(),self.partitionid:tag,'body':bodydict,'hostname':socket.gethostname()}
        #if False: response = requests.put(self.urlc+'/'+self.uuidhex__(), json=payload)
        #POST /{db}
        #Creates a new document in the specified database, using the supplied JSON document structure.
        #If the JSON structure includes the _id field, then the document will be created with the specified document ID.
        #If the _id field is not specified, a new unique ID will be generated, 
        # following whatever UUID algorithm is configured for that server
        response = requests.post(self.urlc, json=payload)
        return (response.status_code,response.json())
    def getall(self):
        #response = requests.get(self.urlc+'/_all_docs')
        # /{db}/_all_docs
        
        # /movies/_find
        # https://docs.couchdb.org/en/stable/api/database/find.html#post--db-_find
        payload = {"selector":{},
                   "fields": [ "datetime",  self.partitionid ]
                   # , "sort": [{"datetime": "asc"}]
                  }
        response = requests.post(self.urlc+'/_find', json=payload)
        return response.json()['docs']
        #return (response.status_code,response.json())
        #print(response.status_code)
        if False: response.raise_for_status()
        return response.json()
    def get1(self,id):
        assert False
        # GET /{db}/{docid}
        response = requests.get(self.urlc+'/'+id)
        #print(response.status_code)
        if False: response.raise_for_status()
        return response.json()        


# In[4]:


cc = Couchdbcli('http://am1:ampwd239@127.0.0.1:5984/logdb')


# In[5]:


print(cc.createdb(predelete=True))
print(cc.log('tag1',{}))
print(cc.log('tag1',{}))
print(cc.log('tag1',{}))
print(cc.log('tag1',{}))


# In[9]:


docs = cc.getall()
docs


# In[ ]:




