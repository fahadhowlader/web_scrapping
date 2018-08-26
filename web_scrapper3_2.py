#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: pabloruizruiz
"""

import os
root = '/Users/pabloruizruiz/OneDrive/Proyectos/Betcomm'
os.chdir(root)

import re
import pandas as pd
from datetime import datetime

from bs4 import BeautifulSoup as BS
from urllib.request import urlopen as uOpen

#from patterns import stopwords
#from patterns import equipos as eq_oficiales

if os.path.exists(root):
    path_to_data = os.path.join(root, 'Datos/Scrapped')
    path_to_save = os.path.join(root, 'Datos/Created')


# Recoger todas las Url posibles con las combinaciones de los dos dropdowns
# -------------------------------------------------------------------------
base_url = 'http://www.laliga.es/estadisticas-historicas/calendario/primera'

temporadas = list()
url_temporadas = dict()
#url_temporadas.append(('2016-2017', base_url))

def path_temporada(url, extra):
    return os.path.join(url, extra)

# Extraer todas las temporadas posibles
for año in range(2016, 2010, -1):
    temp = str(año) + '-' + str(año+1)
    string = str(año) + '-' + str(año-2000+1)
    temporadas.append(temp)
    url_temporadas[temp] = [path_temporada(base_url, string)]

for temp, url in url_temporadas.items():
    #url = url_temporadas[temporadas[0]]
    page_soup = BS(uOpen(url[0]).read(), 'html.parser')
    
    # Extraer todas las opciones del dropdown de equipos
    op_equipos = list()
    dropdown_equipos = page_soup.find_all('div',{'class': 'select-filtros'})[3]
    for option in dropdown_equipos.find_all('option'):
        if len(option['value']) > 0: op_equipos.append(option['value'])     
    
    for eq in op_equipos:
        url_temporadas[temp].append(path_temporada(url_temporadas[temp][0], eq))

    
# Extraer los jugadores y sus estadisticas de cada tempodada
# ----------------------------------------------------------
temps = list(url_temporadas.keys())
#for temp in temps: 
    
temp = temps[0]    
urls = url_temporadas[temp]
#for url in urls[1:]:
url = urls[1]

page = BS(uOpen(url).read(), 'html.parser')
page.find('main')
stats = page.find('section', {'class': 'box tabla-simple estadisticas-historicas'})
stast = stats.find('table')

### PROBLEMON AQUI ###



    
    
    