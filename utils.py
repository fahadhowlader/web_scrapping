# -*- coding: utf-8 -*-

import os
root = '/Users/pabloruizruiz/OneDrive/Proyectos/Betcomm'
os.chdir(root)

import re
import cv2
import numpy as np
# from skimage import io
from urllib.request import urlopen as uOpen

from Data_Handling.patterns import team_stopwords, matches_stopwords
from Data_Handling.patterns import equipos as eq_oficiales


# FUNCTIONS FOR TEXT PROCESSING
# -----------------------------
def comprobar_equivalencia(string, list_ = eq_oficiales):
    '''
    Función que comprueba si la string ya concuerda completamente con uno de 
    los patterns, para devolverla y no seguir con el pre-processing
    '''
    if string in list_:
        return True
    else: 
        return False

def limpiar_nombre(string, list_ = eq_oficiales, stopwords=team_stopwords):
    '''
    Función para establecer los nombres de los equipos en el formato correcto.
    1 - Primero eliminamos las stopwords
    2 - Encontramos su equivalencia en la lista de equipos (FUNCION APARTE?)
    '''
    # Sanity check
    if comprobar_equivalencia(string, list_): return string
    for word in stopwords:
        patron = re.compile(word)
        if re.search(patron, string):
            # Si encuentra la stopword, que la elimine
            string = re.sub(patron, '', string)
            # Busamos el oficial
            #string = buscar_equivalencia(string)
    return string    

def buscar_equivalencia(string, list_ = eq_oficiales):
    '''
    Función complemetaria a limpiar_nombre para asignar el nombre oficial de 
    los equipos tras su limpieza en correspondencia con los equipos oficiales
    '''
    # Sanity check
    if comprobar_equivalencia(string, list_): return string
    # Separarlo y quitar los espacios
    e1 = string.split(' ')   
    # Eliminar los '' creados
    for i, a in enumerate(e1):
        if a == '': del e1[i]

    # e2 = eq_oficiales[5] 
    for e2 in eq_oficiales:
        
        # Encontrar el match para el primero que lo encuentre
        for e3 in e1:
            
            if len(e2) > len(e3):
                # Para el caso en que tenga letras de menos
                if re.search(e3, e2):
                    # Nos quedamos con el oficial
                    return e2
            else:
                # Para el caso en que tenga letras de más
                if re.search(e2, e3):
                    return e2


# FUNCTIONS FOR IMAGE PROCESSING
# ------------------------------
def url_to_image(url):
    '''
    Función para extraer una imagen de una URL
    '''
    resp = uOpen(url)
    image = np.asarray(bytearray(resp.read()), dtype='uint8')
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image