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
from datetime import datetime

from bs4 import BeautifulSoup as BS
from urllib.request import urlopen as uOpen

# IMPORT HELPER FUNCTIONS
from Scrapping.utils import limpiar_nombre, buscar_equivalencia


# MATCH MODELS
#######################################################

# FUNCTIONS FOR TEXT PROCESSING
# -----------------------------
def filtrar_jornada(string):
    '''
    Función para cortar el string que llega del scrapping y obtener el número
    de jornada, y la fecha del partido en el formato deseado
    '''    
    jor, fecha = string.split(' - ')
    jor = int(jor[-2:])
    fecha = datetime.strptime(fecha, '%d/%m/%Y').date()
    return jor, fecha

def filtrar_resultado(string):
    '''
    Función para cortar el string que llega del scrapping y obtener el equipo
    local, el equipo resultante y el resultado del encuentro
    '''
    eq_local, por_separar, gol_visitante = string.split(': ')
    gol_local, eq_visitante = por_separar[0], por_separar[1:]
    return eq_local, eq_visitante, int(gol_local), int(gol_visitante)


partidos_df = pd.DataFrame(columns=['Temporada', 'Jornada', 'Num_partido', 'Fecha', 'Local', 'Visitante', 
                                    'Gol local', 'Gol visitante'])
    
# Crear Temporadas
# ----------------
m_url = 'http://www.laliga.es/estadisticas-historicas/calendario'
m_url2 = 'http://www.laliga.es/estadisticas-historicas/calendario/primera'

url_temporadas = list()
url_temporadas.append(('2016-2017', m_url))

def path_temporada(base, temp):
    return os.path.join(base, temp)

for año in range(2015, 2010, -1):
    temp = str(año) + '-' + str(año+1)
    string = str(año) + '-' + str(año-2000+1)
    url_temporadas.append((temp, path_temporada(m_url2, string)))


# Crear Partidos
# --------------
def crear_calendario(temp, path):
    
    global partidos_df
    page_soup = BS(uOpen(path).read(), 'html.parser')
    jornadas = page_soup.find_all('div',{'class': 'jornada-calendario-historico'})
    
    for jornada in jornadas:

        numero_jornada_y_fecha = jornada.div.text
        jor, fecha = filtrar_jornada(numero_jornada_y_fecha)
        partidos = jornada.findAll('td')
        
        for j, partido in enumerate(partidos):
            
            resultado = partido.text
            eq_loc, eq_vis, gol_loc, gol_vis = filtrar_resultado(resultado)
            eq_loc, eq_vis = limpiar_nombre(eq_loc), limpiar_nombre(eq_vis)        
            eq_loc, eq_vis = buscar_equivalencia(eq_loc), buscar_equivalencia(eq_vis)
            
            res = pd.DataFrame([[temp, jor, j+1, fecha, eq_loc, eq_vis, gol_loc, gol_vis]], 
                               columns=list(partidos_df))
            partidos_df = partidos_df.append(res)
        
    partidos_df = partidos_df.reset_index()
    partidos_df.drop('index', axis=1, inplace=True)
    

for temp, path in url_temporadas:
    crear_calendario(temp, path)


# Crear Árbitros
# --------------
refs_url = 'http://www.livefutbol.com/arbitro/esp-primera-division-'
url_refs = list()
arbitros_df = pd.DataFrame(columns=['Temporada', 'Nombre', 'Partidos', 'Amarillas', 'Rojas'])

for año in range(2017, 2010, -1):
    temp = str(año) + '-' + str(año+1)
    string = str(año) + '-' + str(año+1) + '/1/'
    url_refs.append(refs_url + string)

# url_refs[1] = 'http://www.livefutbol.com/arbitro/esp-primera-division-2016-2017_2/1/'

for url_ref in url_refs:
  
    try: 
        refs_page = BS(uOpen(url_ref).read(), 'html.parser')

        tabla = refs_page.find('table', {'class': 'standard_tabelle'})
        filas = tabla.findAll('tr')[1:-1]
        
        for fila in filas:
            
            #fila = filas[0]
            temporada = url_ref[-12:-3]
            datos = fila.findAll('td')
            nombre = datos[0].text    
            partidos = int(datos[4].text)
            amarillas = int(datos[5].text)
            rojas = datos[6].text
            if rojas == '-': rojas = int(0)
            else: rojas = int(rojas)
            
            arbitro = pd.DataFrame([[temporada, nombre, partidos, amarillas, rojas]], columns=list(arbitros_df))
            arbitros_df = arbitros_df.append(arbitro)
            
    except: print('Error para url: ' + url_ref)
             
arbitros_df = arbitros_df.reset_index()
arbitros_df.drop('index', axis=1, inplace=True)


# Crear Estadios
# --------------
stads_url = 'http://www.livefutbol.com/estadios/esp-primera-division-'
url_stads = list()
estadios_df = pd.DataFrame(columns=['Temporada', 'Nombre', 'Equipo', 'Capacidad'])

for año in range(2017, 2010, -1):
    
    temp = str(año) + '-' + str(año+1)
    string = str(año) + '-' + str(año+1)
    
    url_std = stads_url + string

    try: 
        refs_page = BS(uOpen(url_std).read(), 'html.parser')

        tabla = refs_page.find('table', {'class': 'standard_tabelle'})
        filas = tabla.findAll('tr')[1:-1]
        
        for fila in filas:
            
            #fila = filas[0]
            temporada = temp
            datos = fila.findAll('td')
            nombre = datos[1].text    
            
            sub_url = datos[1].a['href']
            sub_page = BS(uOpen('http://www.livefutbol.com' + sub_url).read(), 'html.parser')
            cuadro = sub_page.find('table', {'class': 'standard_tabelle yellow'})
            equipo = buscar_equivalencia(limpiar_nombre(cuadro.findAll('a')[-1].text))
            
            capacidad = int(datos[5].text.replace('.', ''))
            
            estadio = pd.DataFrame([[temporada, nombre, equipo, capacidad]], columns=list(estadios_df))
            estadios_df = estadios_df.append(estadio)
            
    except: print('Error para url: ' + url_std)
         
estadios_df = estadios_df.reset_index()
estadios_df.drop('index', axis=1, inplace=True)




# Exportar a Excel
# ----------------
arbis_writer = pd.ExcelWriter(path_to_save + '/arbitros_df.xlsx', engine='xlsxwriter')    
arbitros_df.to_excel(arbis_writer, sheet_name='Arbitros')
arbis_writer.save()


estadios_writer = pd.ExcelWriter(path_to_save + '/estadios_df.xlsx', engine='xlsxwriter')    
estadios_df.to_excel(estadios_writer, sheet_name='Estadios')
estadios_writer.save()


partidos_writer = pd.ExcelWriter(path_to_save + '/partidos_df.xlsx', engine='xlsxwriter')    
partidos_df.to_excel(partidos_writer, sheet_name='Partidos')
partidos_writer.save()






#def comprobar_equivalencia(string):
#    '''
#    Función que comprueba si la string ya concuerda completamente con uno de 
#    los patterns, para devolverla y no seguir con el pre-processing
#    '''
#    global eq_oficiales
#    if string in eq_oficiales:
#        return True
#    else: 
#        return False
#
#def limpiar_nombre(string):
#    '''
#    Función para establecer los nombres de los equipos en el formato correcto.
#    1 - Primero eliminamos las stopwords
#    2 - Encontramos su equivalencia en la lista de equipos (FUNCION APARTE?)
#    '''
#    # Sanity check
#    if comprobar_equivalencia(string): return string
#    for word in stopwords:
#        patron = re.compile(word)
#        if re.search(patron, string):
#            # Si encuentra la stopword, que la elimine
#            string = re.sub(patron, '', string)
#            # Busamos el oficial
#            #string = buscar_equivalencia(string)
#    return string    
#
#def buscar_equivalencia(string):
#    '''
#    Función complemetaria a limpiar_nombre para asignar el nombre oficial de 
#    los equipos tras su limpieza en correspondencia con los equipos oficiales
#    '''
#    # Sanity check
#    if comprobar_equivalencia(string): return string
#    # Separarlo y quitar los espacios
#    e1 = string.split(' ')   
#    # Eliminar los '' creados
#    for i, a in enumerate(e1):
#        if a == '': del e1[i]
#
#    # e2 = eq_oficiales[5] 
#    for e2 in eq_oficiales:
#        
#        # Encontrar el match para el primero que lo encuentre
#        for e3 in e1:
#            
#            if len(e2) > len(e3):
#                # Para el caso en que tenga letras de menos
#                if re.search(e3, e2):
#                    # Nos quedamos con el oficial
#                    return e2
#            else:
#                # Para el caso en que tenga letras de más
#                if re.search(e2, e3):
#                    return e2