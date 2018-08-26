#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@title : Scrap Detailed Match Information -- IN PROGRESS
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
from Scrapping.utils import limpiar_nombre, buscar_equivalencia

from Data_Handling.patterns import matches_stopwords


# Páginas Utilizadas
# ------------------
'''
Vamos a utilizar Marca.com porque en un principio solo estamos interesados en 
los goles y las estadísiticos y parece más fácil de loopear y extraer.

Sin embargo, en dbfutbol están las estadísiticas completas de cada partido que
podemos extraer para un proyecto más ambicioso.
'''
acciones = pd.DataFrame(columns=['Temporada', 'Jornada', 'Equipos', 'Goleador', 'Minuto'])
partidos_df = pd.DataFrame(columns=['Temporada', 'Jornada', 'Num_partido', 'Local', 'Visitante', 
                                    'Gol local', 'Gol visitante'])
    


# Recoger todas las Url posibles con las combinaciones de los dos dropdowns
# -------------------------------------------------------------------------
base_url = 'http://www.marca.com/estadisticas/futbol/primera'
#base_url = 'https://www.bdfutbol.com/en/t/t2016-172.html?tab=partits'

temporadas = list()
url_temporadas = dict()
#url_temporadas.append(('2016-2017', base_url))

def path_temporada(url, extra):
    return os.path.join(url, extra)

# Extraer todas las temporadas posibles
for año in range(2016, 2010, -1):
    temp = str(año) + '_' + str(año+1)
    string = str(año) + '_' + str(año-2000+1)
    temporadas.append(temp)
    url_temporadas[temp] = [path_temporada(base_url, string)]
    
    for jornada in range(1,39):
        
        url_temporadas[temp].append(path_temporada(url_temporadas[temp][0], 'jornada_' + str(jornada)))
    del url_temporadas[temp][0]


    
# Extraer los jugadores y sus estadisticas de cada tempodada
# ----------------------------------------------------------

# HELPER FUNCIONS
def limpiar_accion(minuto, jugador):

    mi = minuto.replace('Min. ', '')
    ju = jugador.replace(minuto, '')
    ju = limpiar_nombre(ju, [], stopwords=matches_stopwords)
    ju = ju.replace('()', '').rstrip()
    return mi, ju

temps = list(url_temporadas.keys())

for temp in temps: 
#temp = temps[0]
    url_jornadas = url_temporadas[temp]
    
    for jor, url in enumerate(url_jornadas):
        
        url = url_jornadas[0]
        
        page = BS(uOpen(url).read(), 'html.parser')
        page.find('main')
        
        partidos = page.find('div', {'class': 'resultados borde-caja'})
        partidos = partidos.find('table')
        partidos = partidos.findAll('tr')    
        
        for n, partido in enumerate(partidos):
         
            eq_loc = partido.find('td', {'class':'equipo-local'}).text
            eq_vis = partido.find('td', {'class':'equipo-visitante'}).text
            
            eq_loc, eq_vis = limpiar_nombre(eq_loc), limpiar_nombre(eq_vis)        
            eq_loc, eq_vis = buscar_equivalencia(eq_loc), buscar_equivalencia(eq_vis)
            
            resultado = partido.find('td', {'class':'resultado'}).text
            gol_loc, gol_vis = resultado.split('-')
            
            link_a_stats = partido.attrs['onclick'].split('/')[-2]
            url_stats = url + '/' + link_a_stats
            
            try:
                
                stats_page = BS(uOpen(url_stats).read(), 'html.parser')
            
                INFO_PARTIDO = {'class': 'partido borde-caja'}
                INFO_ESTADIS = {'table'}
                INFO_ARBITRO = {'class': 'col-der'}
                
                # Informacion de las acciones
                info_partido = stats_page.find('div', INFO_PARTIDO).findAll('ul')
                info_loc = info_partido[0].findAll('li')
                for inf in info_loc:
        
                    jugador, minuto = limpiar_accion(inf.strong.text, inf.text)
                    accion = pd.DataFrame([[temp, jor, eq_loc, jugador, minuto]], columns=list(acciones))
                    acciones = acciones.append(accion)   
        
                info_vis = info_partido[1].findAll('li')
                for inf in info_vis:
        
                    jugador, minuto = limpiar_accion(inf.strong.text, inf.text)
                    accion = pd.DataFrame([[temp, jor+1, eq_vis, jugador, minuto]], columns=list(acciones))
                    acciones = acciones.append(accion) 
                    
                # Informaciones generales
                info_general = stats_page.find(INFO_ESTADIS).findAll('tr')
                poss_loc = float(info_general[1].findAll('td')[0].text[:-1].replace(',', '.'))
                poss_loc = float(info_general[1].findAll('td')[2].text[:-1].replace(',', '.'))
                
                # Información del árbitro
                info_arbi = stats_page.find('div', INFO_ARBITRO)
                nombre_arbi = info_arbi.find('div', {'class': 'arbitro-info'}).h5.text
                
                
                # Guardar Partido
                partido = pd.DataFrame([[temp, jor+1, n+1, eq_loc, eq_vis, gol_loc, gol_vis]], columns=list(partidos_df))
                partidos_df = partidos_df.append(partido)
            
            except: print('No encuentro el partido %i de la jorndad %i' % (n+1, jor+1))

partidos_df = partidos_df.reset_index()
partidos_df.drop('index', axis=1, inplace=True)    
    
    
partidos_writer = pd.ExcelWriter(path_to_save + '/partidos_df_sc3.xlsx', engine='xlsxwriter')    
partidos_df.to_excel(partidos_writer, sheet_name='Partidos')
partidos_writer.save()


