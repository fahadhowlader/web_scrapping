#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@title : Scrap Teams and Players Information
@author: pablorr10
"""

import os
root = '/Users/pabloruizruiz/OneDrive/Proyectos/Betcomm'
os.chdir(root)

import cv2
import time
import pandas as pd

from bs4 import BeautifulSoup as BS
from urllib.request import urlopen as uOpen

if os.path.exists(root):
    path_to_data = os.path.join(root, 'Datos/Scrapped')
    path_to_save = os.path.join(root, 'Datos/Created')
    
    
# IMPORT HELPER FUNCTIONS
from Scrapping.utils import limpiar_nombre, buscar_equivalencia, url_to_image


# GLOBAL AND SEASONAL MODELS
######################################################
    
# Open connection, grab the web content and download it
# -----------------------------------------------------
m_url = 'http://www.marca.com/futbol/primera/equipos.html'
client = uOpen(m_url) 
page = client.read()
client.close()

page_soup = BS(page, 'html.parser')
equipos = page_soup.findAll('li', {'id': 'nombreEquipo'})
print('Tenemos %d equipos' % len(equipos))

teams = list()
equipos_df = pd.DataFrame(columns=['Nombre', 'Escudo', 'Es_url'])

jugadores = list()
jugadores_df = pd.DataFrame(columns=['Equipo', 'Jugador', 'Dorsal'])

for equipo in equipos:
    
    # Extraer información global del equipo
    nombre = buscar_equivalencia(limpiar_nombre(equipo.h2.text))
    es_url = equipo.img['src']
    
    start1 = time.time()
    escudo = url_to_image('http:' + es_url)  
    teams.append(nombre)
    nuevo_equipo = pd.DataFrame([[nombre, escudo, es_url]], columns=list(equipos_df))
    equipos_df = equipos_df.append(nuevo_equipo)
    
    # Extraer la plantilla de jugadores
    plantilla = equipo.findAll('li')
    
    # p = plantilla[0]
    for p in plantilla:
        
        dorsal  = p.strong.text
        jugador = p.span.text
        
        jugadores.append(jugador)
        jug = pd.DataFrame([[nombre, jugador, dorsal]], columns=list(jugadores_df))
        jugadores_df = jugadores_df.append(jug)
        
equipos_df = equipos_df.reset_index()
equipos_df.drop('index', axis=1, inplace=True)


# Exportar a Excel
# ----------------

writer_jugadores = pd.ExcelWriter(path_to_save + '/jugadores_df.xlsx', engine='xlsxwriter')
jugadores_df.to_excel(writer_jugadores, sheet_name='Nombre de los jugadores')
writer_jugadores.save()

writer_equipos = pd.ExcelWriter(path_to_save + '/equipos_df.xlsx', engine='xlsxwriter')
equipos_df.to_excel(writer_equipos, sheet_name='Nombre de los jugadores')
writer_equipos.save()


# Comprobar que cada equipo tiene su escudo
for equipo in teams:
    
    escudo = equipos_df.loc[equipos_df['Nombre'] == equipo]['Escudo'][0]
    cv2.imshow(equipo, escudo)
    cv2.waitKey(0)
    
cv2.destroyAllWindows()
    

