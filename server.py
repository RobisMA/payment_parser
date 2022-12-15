# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 12:44:50 2022

@author: m.arkhipkin
"""

from fastapi import FastAPI, File, Response, Request, UploadFile
import parser_payment
import json
import http.client
import uuid
import random

app = FastAPI()

with open('refresh.txt','r') as file:
    refresh_token = file.read().replace('\n','')

@app.post('/files/')
def home(file: bytes = File(...)):
    return(parser_payment.key_extracter(file))

@app.post('/payment/')
async def payment(request:Request):
    global refresh_token 
    refresh_token, access_token = token_refresh(refresh_token)
    conn = http.client.HTTPSConnection("edupirfintech.sberbank.ru", 9443,cert_file='certs/SberBusinessAPI.pem')
    data = await request.json()
    id = data['externalId']
    print("kavo")
    print(str(data))
    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': 'Bearer ' + access_token
    }
    data['externalId']=str(uuid.uuid4())
    data['number']=str(random.randint(100000,999999))
    data = json.dumps(data)
    conn.request("POST", "/fintech/api/v1/payments", data, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    link = pdf_writer('3965685','pdf.pdf',access_token)
    return(link)

def token_refresh(refresh_token):
    conn = http.client.HTTPSConnection("edupirfintech.sberbank.ru", 9443,cert_file='certs/SberBusinessAPI.pem')
    payload = ''
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json'
    }
    conn.request("POST", "/ic/sso/api/oauth/token?grant_type=refresh_token&client_id=10213&redirect_uri=https%253A%252F%252Frobis-m.com%252F&refresh_token="+refresh_token+"&client_secret=10213", payload, headers)
    res = conn.getresponse()   
    data = res.read()
    data = data.decode("utf-8")
    print(data)
    data = json.loads(data)
    access_token = data['access_token']
    refresh_token = data['refresh_token']
    with open('refresh.txt','w') as file:
        file.write(str(refresh_token))
    return(refresh_token,access_token)

def pdf_writer(id,name,access_token):
    conn = http.client.HTTPSConnection("edupirfintech.sberbank.ru",9443,cert_file='certs/SberBusinessAPI.pem')
    payload = ''
    headers = {
    	'Accept': 'application/json',
    	'Authorization': 'Bearer ' + access_token,
    }
    conn.request("GET","/fintech/api/v1/statement/transactions/"+str(id)+"/print?format=PDF",payload,headers)
    res = conn.getresponse()
    data = res.read()
    with open('/var/www/html/shared_files/'+name, 'wb') as file:
        file.write(data)
    return('http://46.243.201.66/shared_files/'+name)
