#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@title : Scrap Matches Information
@author: pabloruizruiz
"""

import os
root = '/Users/pabloruizruiz/OneDrive/Proyectos/Betcomm'
os.chdir(root)

if os.path.exists(root):
    path_to_data = os.path.join(root, 'Datos/Scrapped')
    path_to_save = os.path.join(root, 'Datos/Created')


import pandas as pd
from bs4 import BeautifulSoup as BS
from urllib.request import urlopen as uOpen

# IMPORT HELPER FUNCTIONS
from Scrapping.utils import limpiar_nombre, buscar_equivalencia


# MATCH MODELS
#######################################################
partidos_df = pd.DataFrame(columns=['Round', 'Match #', 'Home team', 'Away team'])
    
# Crear Temporadas
# ----------------
m_url = 'http://www.marca.com/futbol/primera-division/calendario.html'


# Crear Partidos
# --------------
def crear_calendario(temp, path):
    
    global partidos_df
    page_soup = BS(uOpen(path).read(), 'html.parser')
    rounds = page_soup.find_all('div',{'class': 'jornada calendarioInternacional'})
    
    for r in rounds:
        
        rnd = r.caption.text        # Get the name of the round i.e. Jornada 1
        matches = r.findAll('tr')   # Find all the matches in that round
        
        for j, match in enumerate(matches[1:]):
            
            loc  = match.find('td', {'class': 'local'}).span.text
            away = match.find('td', {'class': 'visitante'}).span.text
            
            loc, away = limpiar_nombre(loc), limpiar_nombre(away)        
            loc, away = buscar_equivalencia(loc), buscar_equivalencia(away)
            
            res = pd.DataFrame([[rnd, j+1, loc, away]], columns=list(partidos_df))
            partidos_df = partidos_df.append(res)
        
    partidos_df = partidos_df.reset_index()
    partidos_df.drop('index', axis=1, inplace=True)
    

crear_calendario('2018-2019', m_url)



# Exportar a Excel
# ----------------
partidos_writer = pd.ExcelWriter(path_to_save + '/partidos_df.xlsx', engine='xlsxwriter')    
partidos_df.to_excel(partidos_writer, sheet_name='Partidos')
partidos_writer.save()

