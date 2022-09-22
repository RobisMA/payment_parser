# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 12:44:50 2022

@author: m.arkhipkin
"""

from fastapi import FastAPI, File
import parser_payment

app = FastAPI()

@app.post('/files/')
def home(file: bytes = File(...)):
    return(parser_payment.key_extracter(file))