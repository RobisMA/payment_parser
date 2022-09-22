# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 11:49:26 2022

@author: m.arkhipkin
"""
from sys import argv
from PIL import Image
import re 
import numpy as np
import cv2
import pytesseract
from pdf2image import convert_from_path
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def converter(filename):
    if filename[-4:]=='.pdf':
        images = convert_from_path(filename,800)
        images[0].save('testfile.jpg', 'JPEG')
 
        


def tablet_deleter(imagePath):
    gray = cv2.imread(imagePath,0)
    _, binary = cv2.threshold(gray, 160, 255, 0)
    inv = 255 - binary
    horizontal_img = inv
    vertical_img = inv
     
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,150))
    horizontal_img = cv2.erode(horizontal_img, kernel, iterations=1)
    horizontal_img = cv2.dilate(horizontal_img, kernel, iterations=1)
     
     
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (150,1))
    vertical_img = cv2.erode(vertical_img, kernel, iterations=1)
    vertical_img = cv2.dilate(vertical_img, kernel, iterations=1)
     
    mask_img = horizontal_img + vertical_img
    no_border = cv2.bitwise_or(binary, mask_img)
    img = cv2.GaussianBlur(no_border,(3,3),0)
    gg = cv2.imwrite('testfile.jpg',img)
    h,w = img.shape
    return(img)


def data_extracter(path):
    ##################
    image = cv2.imread(path,0)
    kernel = np.ones((3,3),'uint8')
    kernel2 = np.ones((2,2),'uint8')
    img = cv2.dilate(image, kernel)
    image = cv2.erode(img, kernel2)
    data = pytesseract.image_to_string(image,lang = 'rus')
    return(data)


def data_processing(data):
    month=['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    done = False
    for i in month:
        if i in data:
            data = data.replace(i,str(month.index(i)+1).rjust(2,'0'))
            done = True
    if done == False:
        for i in month:
            if i.title() in data:
                data = data.replace(i.title(),str(month.index(i)+1).rjust(2,'0'))
                done = True
    data = data.replace('\t',' ')
    data = data.replace('\n\n','\n')
    data = data.replace('\xa0',' ')
    data = data.replace('\n1. ','\n ')
    data = data.replace(' руб.','')
    return(data)


def bik_extracter(text,cor):
    bik_re = '[^\d]\d{6}'+ cor[-3:]+'[^\d]'
    bik = re.search(bik_re, text)
    if type(bik)==re.Match:
        bik = bik.group(0)
        res=''
        for symbol in bik:
            if symbol.isdigit():
                res+=symbol
        return res
    else:
        bik_re = 'ИК\n[^\d]{1,30}\d{9}[^\d]'
        bik = re.search(bik_re, text)
        if type(bik)==re.Match:
            bik = bik.group(0)
            bik += ' '
            bik_re = '[^\d]\d{9}[^\d]'
            bik = re.search(bik_re, bik)
            bik = bik.group(0)
            res=''
            for symbol in bik:
                if symbol.isdigit():
                    res+=symbol
            return res
        else:
            bik_re = 'БИК\s{1,2}.{1,50}\s{1,2}\d{9}[^\d]'
            bik = re.search(bik_re, text)
            if type(bik)==re.Match:
                bik = bik.group(0)
                bik += ' '
                bik_re = '[^\d]\d{9}[^\d]'
                bik = re.search(bik_re, bik)
                bik = bik.group(0)
                res=''
                for symbol in bik:
                    if symbol.isdigit():
                        res+=symbol
                return res
            else:
                res = 'not found'
    return res


def innkpp_extracter(text):
    inn_kpp = '[^\d]\d{10}\W\d{9}'
    inn_solo = 'ИНН[^\d]{1,3}\d{10,12}'
    kpp_solo = 'КПП[^\d]{0,}[^\d]\d{9}[^\d]'
    innkpp = re.search(inn_kpp, text)
    innsolo = re.search(inn_solo, text)
    if type(innkpp)==re.Match and type(innsolo)==re.Match:
        innkpp = innkpp.group(0)
        innsolo = innsolo.group(0)
        resinn=''
        for symbol in innsolo:
            if symbol.isdigit():
                resinn+=symbol
        if text.index(resinn)<text.index(innkpp):
            kpp = re.search(kpp_solo, text)
            if type(kpp)==re.Match:
                kpp = kpp.group(0)
                reskpp=''
                for symbol in kpp:
                    if symbol.isdigit():
                        reskpp+=symbol
            else:
                reskpp = 'not found'
            inn = re.search(inn_solo, text)
            return(resinn,reskpp)
    innkpp = re.search(inn_kpp, text)
    if type(innkpp)==re.Match:
        innkpp = innkpp.group(0)
        resinn = innkpp[1:-10]
        reskpp = innkpp[-9:]
    else:
        inn = re.search(inn_solo, text)
        if type(inn)==re.Match:
            inn = inn.group(0)
            resinn=''
            for symbol in inn:
                if symbol.isdigit():
                    resinn+=symbol
            if len(resinn)==12:
                return(resinn,'-')
        else:
            resinn = 'not found'
        kpp = re.search(kpp_solo, text)
        if type(kpp)==re.Match:
            kpp = kpp.group(0)
            reskpp=''
            for symbol in kpp:
                if symbol.isdigit():
                    reskpp+=symbol
        else:
            reskpp = 'not found'
        inn = re.search(inn_solo, text)
    return(resinn,reskpp)
        
    
def date_extracter(text):
    if "ТК ЭНЕРГИЯ" in text:
        date_re = 'от.{0,3}\d{1,}[^\n]\d{2,}[^\n]\d{2,}\n'
        date = re.search(date_re,text)
        if type(date)==re.Match:
            date = date.group(0)
            date = (date[2:].strip()).replace(' ','.')
            date = date.split('.')
            date[0]=date[0].rjust(2,'0')
            if len(date[2]) == 4:
                date[2]=date[2][2:]
            date = date[0]+'.'+date[1]+'.'+date[2]
            return date
    date_re = 'от.{0,3}\d{1,}[^\n]\d{2,}[^\n]\d{2,}'
    date = re.search(date_re,text)
    if type(date)==re.Match:
        date = date.group(0)
        date = (date[2:].strip()).replace(' ','.')
        date = date.split('.')
        date[0]=date[0].rjust(2,'0')
        if len(date[2]) == 4:
            date[2]=date[2][2:]
        date = date[0]+'.'+date[1]+'.'+date[2]
    else:
        date = 'not found'
    return date

def sum_extracter(text):
    res_nds = 'not_found'
    res_total = 'not_found'
    if "Автопитер" in text or "АВТОПИТЕР" in text:
        sum_nds_re = '\nИтого:\n\d{1,}.{0,}\d{0,2}\nВ том\nчисле\nНДС:\n\d{1,}.{0,}\d{0,2}\n'
        sum_str = re.search(sum_nds_re, text)
        if type(sum_str) == re.Match:
            sum_str = sum_str.group(0)
            sum_str = sum_str.replace('\n','')
            sum_str = sum_str[6:]
            l = sum_str.split('В томчислеНДС:')
            total_amount = l[0]
            total_vat = l[1]
            sum= '-'
            return(sum,total_vat,total_amount)
        sum_nds_re = '\d{1,}.{0,1}\d{0,2}\n\d{1,}.{0,1}\d{0,2}\n\d{1,}.{0,1}\d{0,2}'
        sum_str = re.search(sum_nds_re, text)
        if type(sum_str) == re.Match:
            sum_str = sum_str.group(0)
            l = sum_str.split('\n')
            total_amount = l[1]
            total_vat = l[2]
            sum= '-'
            return(sum,total_vat,total_amount)
        sum_nds_re = '\d{1,}.{0,1}\d{0,2}\n\d{1,}.{0,1}\d{0,2}'
        sum_str = re.findall(sum_nds_re, text)
        if len(sum_str) != 0:
            sum_str = sum_str[-1]
            l = sum_str.split('\n')
            total_amount = l[0]
            total_vat = l[1]
            return('-',total_vat,total_amount)
    if "Деловые Линии" in text:
        sum_nds_re = 'Итого:[^\d]{1,}\d{0,}[^\d]{0,}\d{1,}[^\d]{1,}\d{2}[^\d]{1,}\d{0,}[^\d]{0,}\d{1,}[^\d]{1,}\d{2}[^\d]{1,}\d{0,}[^\d]{0,}\d{1,}[^\d]{1,}\d{2}'
        sum_str = re.search(sum_nds_re, text)
        if type(sum_str) == re.Match:
            sum_str = sum_str.group(0)
            sum_str = sum_str.replace('Итого: ','')
            sum_str = sum_str.replace(' ','')
            sum_str = sum_str.replace(',','.')
            sum_str = sum_str.replace('-','0')
            l = sum_str.split('\n')
            total_amount = l[2]
            total_vat = l[1]
            sum= l[0]
            return(sum,total_vat,total_amount)
    if "ТехСервис" in text or "ГАЗИМПОРТ" in text or "Новэкс" in text:
        sum_nds_re = '\d{0,}[^\d]\d{0,}[^\d]{0,1}\d{1,}[^\d]\d{2}\n..\d{0,}[^\d]{0,1}\d{1,}[^\d]\d{2}\n\d{0,1}[^\d]{4}'
        sum_str = re.findall(sum_nds_re, text)
        if len(sum_str) != 0:
            sum_str = sum_str[-1]
            sum_str = sum_str[:-4]
            sum_str = sum_str.replace(' ','')
            sum_str = sum_str.replace('-','0')
            sum_str = sum_str.replace(',','.')
            sum_str = sum_str.replace("'",'')
            l = sum_str.split('\n')
            if "ГАЗИМПОРТ" in text or "Новэкс" in text:
                total_amount = l[1]
                total_vat = l[2]
            else:
                total_amount = l[0]
                total_vat = l[1]
            return('-',total_vat,total_amount)
    sum_nds_total_re = '[^\d]\d{0,}.\d{1,}[^\d]\d{2}[^\d]\d{0,}.\d{1,}[^\d]\d{2}[^\d]\d{0,}.\d{1,}[^\d]\d{2}[^\d]{2}'
    sum_str = re.findall(sum_nds_total_re, text)
    if len(sum_str) != 0:
        sum_str = sum_str[-1]
        sum_str = sum_str.replace(',','.')
        sum_str = sum_str.replace('-','.')
        temp=''
        for i in sum_str:
            if i.isdigit() or i =='.':
                temp += i 
        sum_str = temp
        ind = sum_str.index('.')
        sm = sum_str[:ind+3]
        sum_str = sum_str[ind+3:]
        ind = sum_str.index('.')
        nds = sum_str[:ind+3]
        total = sum_str[ind+3:]
        return(sm,nds,total)
    else:
        res_total = 'not found'
        total_re = 'того[^\d]{0,}\d{1,3}.\d{1,3}.\d{2}'
        total = re.search(total_re, text)
        if type(total) == re.Match:
            total = total.group(0)
            if "ТК ЭНЕРГИЯ" in text:
                total = total.replace('-','.')
            total = total.replace(',','.')
            if ':' in total:
                total = total[1+total.index(':'):]
            else: 
                total = total[1+total.index('о'):]
            res_total=''
            for i in total:
                if i.isdigit() or i =='.':
                    res_total += i
        else:
            res_nds = 'not found'
        nds_re = '.{1,}ез.{0,}НДС'
        nds = re.search(nds_re, text)
        if type(nds) == re.Match:
            res_nds = '0'
        else:
            nds_re = 'т.{0,3}ч.{0,5}НДС.{0,}\d{1,}'
            nds = re.search(nds_re, text)
            if type(nds) == re.Match:
                nds = nds.group(0)
                if "ТК ЭНЕРГИЯ" in text:
                    nds = nds.replace('-','.')
                if ':' in nds:
                    nds = nds[1+nds.index(':'):].replace(',', '.')
                res_nds = ''
                nds = nds.replace('т.ч.','')
                for i in nds:
                    if i.isdigit() or i == '.':
                        res_nds += i
            else:
                nds_re = 'НДС.{0,}:[^\d]{0,2}\d{1,6}.{0,1}\d{0,2}'
                nds = re.search(nds_re, text)
                if type(nds) == re.Match:
                    nds = nds.group(0)
                    nds = nds[1+nds.index(':'):].replace(',', '.')
                    res_nds = ''
                    for i in nds:
                        if i.isdigit() or i == '.':
                            res_nds += i
                else:
                    nds_re = "числе.\d{1,6}\nНДС"
                    nds = re.search(nds_re, text)
                    if type(nds) == re.Match:
                        nds = nds.group(0)
                        nds = nds[2+nds.index('е'):].replace(',', '.')
                        res_nds = ''
                        for i in nds:
                            if i.isdigit() or i == '.':
                                res_nds += i
        if len(res_total)==0:
            last_chance_re = '\d{1,}.\d{2}\n\d{1,}.\d{2}\n\W'
            text = text.replace(' ','')
            text = text.replace(',','.')
            last = re.search(last_chance_re, text)
            if type(last) == re.Match:
                last = last.group(0)
                res_nds = last.split('\n')[0]
                res_total = last.split('\n')[1]
        return('-',res_nds,res_total)
    
                

def num_extracter(text):
    num_re = 'т[^\d]{1,11}№.{2,40}от'
    num = re.search(num_re, text)
    if type(num)==re.Match:
        num = num.group(0)
        left = num.find('№')
        right = num.find('от')
        return(num[left+1:right].strip())
    num_re = 'Т[^\d]{1,10}№.{2,40}от'
    num = re.search(num_re, text)
    if type(num)==re.Match:
        num = num.group(0)
        left = num.find('№')
        right = num.find('от')
        return(num[left+1:right].strip())
    else:
        return'not found'
        
def accaunt_extracter(text):
    text = text.replace(' ','')
    accaunt_re = '4\d{19}'
    accaunt = re.search(accaunt_re, text)
    if type(accaunt)==re.Match:
        return(accaunt.group(0))
    else:
        return('not found')

def cor_accaunt_extracter(text):
    text = text.replace(' ','')
    accaunt_re = '3\d{19}'
    accaunt = re.search(accaunt_re, text)
    if type(accaunt)==re.Match:
        return(accaunt.group(0))
    else:
        return('not found')

class PDFMiner:
    '''
    PDFMiner wrapper to get PDF Text
    '''

    @classmethod
    def getPDFText(cls,pdfFilenamePath,throwError:bool=True):
        retstr = StringIO()
        parser = PDFParser(open(pdfFilenamePath,'rb'))
        try:
            document = PDFDocument(parser)
            parser.close()
        except Exception as e:
            errMsg=f"error {pdfFilenamePath}:{str(e)}"
            print(errMsg)
            if throwError:
                raise e
            parser.close()
            return ''
        if document.is_extractable:
            rsrcmgr = PDFResourceManager()
            device = TextConverter(rsrcmgr,retstr,  laparams = LAParams())
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            for page in PDFPage.create_pages(document):
                interpreter.process_page(page)
            parser.close()
            return retstr.getvalue()
        else:
            print(pdfFilenamePath,"Warning: could not extract text from pdf file.")
            return ''


    
    
      
    
def key_extracter(file):
    with open ("testfile.pdf", 'wb') as pdf_file:
        pdf_file.write(file)
    converter("testfile.pdf")
    if (PDFMiner.getPDFText("testfile.pdf")=='\x0c'):
        #rotation("testfile.jpg")
        img=tablet_deleter("testfile.jpg")
        text = data_extracter("testfile.jpg")
        text = data_processing(text)
    else:
        text = PDFMiner.getPDFText(file)
        text = data_processing(text)
    #w,h =img.shape
    #img = cv2.resize(img,[h//4,w//4])
    #cv2.imshow('f',img)
    #cv2.waitKey(0)
    innkpp = innkpp_extracter(text)
    inn = innkpp[0]
    kpp= innkpp[1]
    num = num_extracter(text)
    date = date_extracter(text)
    smnds = sum_extracter(text)
    sm = smnds[2]
    nds = smnds[1]
    acc = accaunt_extracter(text)
    cor = cor_accaunt_extracter(text)
    bik = bik_extracter(text,cor)
    data = {'inn': inn, 'kpp': kpp,'bik':bik,'cause':num,'date':date,'total_amount':sm,'total_vat':nds,'account':acc,'corr':cor}
    l = list(data.values())
    if 'not_found' in l or 'not found' in l:
        img=tablet_deleter("testfile.jpg")
        text = data_extracter("testfile.jpg")
        text = data_processing(text)
        innkpp = innkpp_extracter(text)
        inn = innkpp[0]
        kpp= innkpp[1]
        num = num_extracter(text)
        date = date_extracter(text)
        smnds = sum_extracter(text)
        sm = smnds[2]
        nds = smnds[1]
        acc = accaunt_extracter(text)
        cor = cor_accaunt_extracter(text)
        bik = bik_extracter(text,cor)
        data = {'inn': inn, 'kpp': kpp,'bik':bik,'cause':num,'date':date,'total_amount':sm,'total_vat':nds,'account':acc,'corr':cor}
    return(data)

