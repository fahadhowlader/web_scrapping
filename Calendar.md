
# Web scrapping the footbal calendar to a custom Excel file

<img src='https://github.com/PabloRR100/Betcomm/blob/master/Scrapping/images/title.png?raw=true' style='width:50%'>
    <br>
<div class='text-justify'>

In this post I will make use of the Python library, <a href=''> Beautiful Soap 4</a>, to scrap content on the web to build an excel with all the footbal matches of the <a href='https://www.laliga.es'> Spanish Football League</a>.
</div><br>

Because some of the function names have been implemented in spanish, I introduced comments for the translation.

This demo is quite simple, and is ment to just go over the functionalities of Beatiful Soap.  
In my [GitHub repository](https://github.com/PabloRR100/Betcomm/tree/master/Scrapping) there are scripts for going a step further and create a complete statistics database: 
- Save the teams and players for every season in the history
- Save the matches, results and statistics of every match in the history


## Plan of attack
  
&emsp; 1 - **Source**: Analyze the platform from where we will extract the data  
&emsp; 2 - **Exploration**: Analyze how the information is structured on that platforms - the ```html body```  
&emsp; 3 - **Extraction**: Retrieve the data using ```Beatiful Soap 4```  
&emsp; 4 - **Export**: save the resulting ```pandas Dataframe``` object into an Excel file  


---
---


## 1 - Source    
<br>
<div class='text-justify'>
The first thing to look at, is the source where we will get the data from. In this case, we will make use of one of the most popular spanish football newspapers, <a href='www.marca.com'> Marca</a>.
</div><br>

<img src='https://github.com/PabloRR100/Betcomm/blob/master/Scrapping/images/source.png?raw=true'><br>

<div class='text-justify'>
    In this picture, we see how we can make use of the <a href='https://cs.brown.edu/courses/cs132/resources/inspector/'> inspector</a> to understand how the content of that particular website is organized. This is a mandatory step, since we are going to make use of that structure to navigate over it and extract the information in the order we want.  
</div><br>

<div class='text-justify'>
Another possible way to do what we are going to achieve is by using graphical interfaces, but I find them even less intuitive and less flexible than using beautifulsoap and define you behavior on your scripts. However, here is a screenshot of <a href='https://www.parsehub.com/'> ParseHub</a>, that I believe helps to understand what we want to achieve later on.
</div><br>

<img src='https://github.com/PabloRR100/Betcomm/blob/master/Images/web_scrapping_screenshots/Screen%20Shot%202018-05-02%20at%2018.44.24.png?raw=true'><br>


<div class='text-justify'>
    <br>
    Intuitively, we can see how we are mapping the different <i>html</i> pieces in a hierarchical order. The headers of each column whithin the big table will represent the round on the calendar and every row within that column contains the information of the whole match.  
Obviously, it is required also a high text processing to define how exactly you want your final output to be.

</div><br>

## 2 - Explore data    
<br>
<div class='text-justify'>
We are now ready to explore the website according to the observed structure. 
The very first thing, like in any other data science project, is to import the necessary libraries. We will import all of them now and then explain when each one is used an how.   
   
</div><br>

By now, the important thing to know is that we need to import ```bs4```, ```urllib``` and ```utils.py```.
- bs4 is the Beautiful Soap 4 module itself
- urrlib will help us to access website and parse its ```html``` content
- [```utils.py```](https://github.com/PabloRR100/Betcomm/blob/master/Scrapping/Utils.ipynb) contains functions for the mentions text processing
- [```patterns```](https://github.com/PabloRR100/Betcomm/blob/master/Scrapping/Utils.ipynb) is called from the ```utils.py```. It contains information about the names of the teams and stopwords we want to get rid of. These are, for instance: FC, SD, CA, RC, Club...


```python
import os
root = './'
os.chdir(root)

if os.path.exists(root):
    path_to_data = os.path.join(root, 'Datos/Scrapped')
    path_to_save = os.path.join(root, 'Datos/Created')


import pandas as pd
from datetime import datetime

from bs4 import BeautifulSoup as BS
from urllib.request import urlopen as uOpen

# IMPORT HELPER FUNCTIONS
from utils import limpiar_nombre, buscar_equivalencia
```

### Define how we will store the data
We create an empty ```pandas dataframe``` to define how we want to store the information


```python
# MATCH MODELS
partidos_df = pd.DataFrame(columns=['Round', 'Match #', 'Home team', 'Away team'])
```

## 3 - Retrieve the html content from the source


```python
m_url = 'http://www.marca.com/futbol/primera-division/calendario.html'
page_soup = BS(uOpen(m_url).read(), 'html.parser')
```

```python
page_soup = BS(uOpen(m_url).read(), 'html.parser')
```  
We are telling ```BS``` to read the content open by ```urlope``` from ```urllib.request```. This brings all the html content of the page.  

Then, we are interested in retrieve each of the rounds. If we take a look at the html again to see what are we looking for: 
<img src='https://github.com/PabloRR100/Betcomm/blob/master/Scrapping/images/rounds.png?raw=true'>

We see how each of the rounds is defined inside a ```div``` element which ```class```is: jornada calendarioInternacional  

Therefore, we use the BS method ```find_all()```:


```python
rounds = page_soup.find_all('div',{'class': 'jornada calendarioInternacional'})
print(len(rounds))
```

    38


We check that there are indeed 38 rounds. And if we take a look at the content of any of them, for instance the first one, we could see the retreived html and check Girona - Valladolid is the first of the matches of the first round


```python
rounds[0]
```




    <div class="jornada calendarioInternacional">
    <div class="cal-agendas calendario">
    <div class="jornada datos-jornada">
    <a class="ir-arriba" href="#top">Ir arriba</a>
    <table cellpadding="0" cellspacing="0" class="jor agendas" id="jornada1" summary="Todos los resultados de la jornada">
    <caption>Jornada 1</caption>
    <thead>
    <tr>
    <th scope="col">Equipo local</th>
    <th scope="col">Resultado</th>
    <th scope="col">Equipo visitante</th>
    </tr>
    </thead>
    <tbody>
    <tr>
    <td class="local">
    <figure>
    <img alt="Girona" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/2893.png">
    </img></figure>
    <span class="equipo_t2893">Girona</span>
    </td>
    <td class="resultado"><span class="resultado-partido">0-0</span></td>
    <td class="visitante">
    <span class="equipo_t192">Valladolid</span>
    <figure>
    <img alt="Valladolid" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/192.png"/>
    </figure>
    </td>
    </tr>
    <tr>
    <td class="local">
    <figure>
    <img alt="Betis" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/185.png"/>
    </figure>
    <span class="equipo_t185">Betis</span>
    </td>
    <td class="resultado"><span class="resultado-partido">0-3</span></td>
    <td class="visitante">
    <span class="equipo_t855">Levante</span>
    <figure>
    <img alt="Levante" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/855.png"/>
    </figure>
    </td>
    </tr>
    <tr>
    <td class="local">
    <figure>
    <img alt="Celta" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/176.png"/>
    </figure>
    <span class="equipo_t176">Celta</span>
    </td>
    <td class="resultado"><span class="resultado-partido">1-1</span></td>
    <td class="visitante">
    <span class="equipo_t177">Espanyol</span>
    <figure>
    <img alt="Espanyol" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/177.png"/>
    </figure>
    </td>
    </tr>
    <tr>
    <td class="local">
    <figure>
    <img alt="Villarreal" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/449.png"/>
    </figure>
    <span class="equipo_t449">Villarreal</span>
    </td>
    <td class="resultado"><span class="resultado-partido">1-2</span></td>
    <td class="visitante">
    <span class="equipo_t188">R. Sociedad</span>
    <figure>
    <img alt="R. Sociedad" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/188.png"/>
    </figure>
    </td>
    </tr>
    <tr>
    <td class="local">
    <figure>
    <img alt="Barcelona" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/178.png"/>
    </figure>
    <span class="equipo_t178">Barcelona</span>
    </td>
    <td class="resultado"><span class="resultado-partido">3-0</span></td>
    <td class="visitante">
    <span class="equipo_t173">Alavés</span>
    <figure>
    <img alt="Alavés" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/173.png"/>
    </figure>
    </td>
    </tr>
    <tr>
    <td class="local">
    <figure>
    <img alt="Eibar" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/953.png"/>
    </figure>
    <span class="equipo_t953">Eibar</span>
    </td>
    <td class="resultado"><span class="resultado-partido">1-2</span></td>
    <td class="visitante">
    <span class="equipo_t2894">Huesca</span>
    <figure>
    <img alt="Huesca" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/2894.png"/>
    </figure>
    </td>
    </tr>
    <tr>
    <td class="local">
    <figure>
    <img alt="Rayo" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/184.png"/>
    </figure>
    <span class="equipo_t184">Rayo</span>
    </td>
    <td class="resultado"><span class="resultado-partido">1-4</span></td>
    <td class="visitante">
    <span class="equipo_t179">Sevilla</span>
    <figure>
    <img alt="Sevilla" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/179.png"/>
    </figure>
    </td>
    </tr>
    <tr>
    <td class="local">
    <figure>
    <img alt="Real Madrid" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/186.png"/>
    </figure>
    <span class="equipo_t186">Real Madrid</span>
    </td>
    <td class="resultado"><span class="resultado-partido">2-0</span></td>
    <td class="visitante">
    <span class="equipo_t1450">Getafe</span>
    <figure>
    <img alt="Getafe" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/1450.png"/>
    </figure>
    </td>
    </tr>
    <tr>
    <td class="local">
    <figure>
    <img alt="Valencia" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/191.png"/>
    </figure>
    <span class="equipo_t191">Valencia</span>
    </td>
    <td class="resultado"><span class="resultado-partido">1-1</span></td>
    <td class="visitante">
    <span class="equipo_t175">Atlético</span>
    <figure>
    <img alt="Atlético" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/175.png"/>
    </figure>
    </td>
    </tr>
    <tr>
    <td class="local">
    <figure>
    <img alt="Athletic" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/174.png"/>
    </figure>
    <span class="equipo_t174">Athletic</span>
    </td>
    <td class="resultado"><span class="resultado-partido">2-1</span></td>
    <td class="visitante">
    <span class="equipo_t957">Leganés</span>
    <figure>
    <img alt="Leganés" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/957.png"/>
    </figure>
    </td>
    </tr>
    </tbody>
    </table>
    </div>
    </div>
    </div>



We see how the round number is stored within the ```<caption>``` element.  
We can then store this first piece of information as:


```python
rounds[0].caption.text
```




    'Jornada 1'



And we can also check that the information for the particular round is contain in the ```round -> table -> tbody``` element:


```python
rounds[0].table.tbody
```




    <tbody>
    <tr>
    <td class="local">
    <figure>
    <img alt="Girona" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/2893.png">
    </img></figure>
    <span class="equipo_t2893">Girona</span>
    </td>
    <td class="resultado"><span class="resultado-partido">0-0</span></td>
    <td class="visitante">
    <span class="equipo_t192">Valladolid</span>
    <figure>
    <img alt="Valladolid" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/192.png"/>
    </figure>
    </td>
    </tr>
    <tr>
    <td class="local">
    <figure>
    <img alt="Betis" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/185.png"/>
    </figure>
    <span class="equipo_t185">Betis</span>
    </td>
    <td class="resultado"><span class="resultado-partido">0-3</span></td>
    <td class="visitante">
    <span class="equipo_t855">Levante</span>
    <figure>
    <img alt="Levante" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/855.png"/>
    </figure>
    </td>
    </tr>
    <tr>
    <td class="local">
    <figure>
    <img alt="Celta" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/176.png"/>
    </figure>
    <span class="equipo_t176">Celta</span>
    </td>
    <td class="resultado"><span class="resultado-partido">1-1</span></td>
    <td class="visitante">
    <span class="equipo_t177">Espanyol</span>
    <figure>
    <img alt="Espanyol" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/177.png"/>
    </figure>
    </td>
    </tr>
    <tr>
    <td class="local">
    <figure>
    <img alt="Villarreal" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/449.png"/>
    </figure>
    <span class="equipo_t449">Villarreal</span>
    </td>
    <td class="resultado"><span class="resultado-partido">1-2</span></td>
    <td class="visitante">
    <span class="equipo_t188">R. Sociedad</span>
    <figure>
    <img alt="R. Sociedad" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/188.png"/>
    </figure>
    </td>
    </tr>
    <tr>
    <td class="local">
    <figure>
    <img alt="Barcelona" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/178.png"/>
    </figure>
    <span class="equipo_t178">Barcelona</span>
    </td>
    <td class="resultado"><span class="resultado-partido">3-0</span></td>
    <td class="visitante">
    <span class="equipo_t173">Alavés</span>
    <figure>
    <img alt="Alavés" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/173.png"/>
    </figure>
    </td>
    </tr>
    <tr>
    <td class="local">
    <figure>
    <img alt="Eibar" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/953.png"/>
    </figure>
    <span class="equipo_t953">Eibar</span>
    </td>
    <td class="resultado"><span class="resultado-partido">1-2</span></td>
    <td class="visitante">
    <span class="equipo_t2894">Huesca</span>
    <figure>
    <img alt="Huesca" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/2894.png"/>
    </figure>
    </td>
    </tr>
    <tr>
    <td class="local">
    <figure>
    <img alt="Rayo" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/184.png"/>
    </figure>
    <span class="equipo_t184">Rayo</span>
    </td>
    <td class="resultado"><span class="resultado-partido">1-4</span></td>
    <td class="visitante">
    <span class="equipo_t179">Sevilla</span>
    <figure>
    <img alt="Sevilla" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/179.png"/>
    </figure>
    </td>
    </tr>
    <tr>
    <td class="local">
    <figure>
    <img alt="Real Madrid" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/186.png"/>
    </figure>
    <span class="equipo_t186">Real Madrid</span>
    </td>
    <td class="resultado"><span class="resultado-partido">2-0</span></td>
    <td class="visitante">
    <span class="equipo_t1450">Getafe</span>
    <figure>
    <img alt="Getafe" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/1450.png"/>
    </figure>
    </td>
    </tr>
    <tr>
    <td class="local">
    <figure>
    <img alt="Valencia" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/191.png"/>
    </figure>
    <span class="equipo_t191">Valencia</span>
    </td>
    <td class="resultado"><span class="resultado-partido">1-1</span></td>
    <td class="visitante">
    <span class="equipo_t175">Atlético</span>
    <figure>
    <img alt="Atlético" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/175.png"/>
    </figure>
    </td>
    </tr>
    <tr>
    <td class="local">
    <figure>
    <img alt="Athletic" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/174.png"/>
    </figure>
    <span class="equipo_t174">Athletic</span>
    </td>
    <td class="resultado"><span class="resultado-partido">2-1</span></td>
    <td class="visitante">
    <span class="equipo_t957">Leganés</span>
    <figure>
    <img alt="Leganés" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/957.png"/>
    </figure>
    </td>
    </tr>
    </tbody>



Where the matches will be inside each ```td``` element of the body of the table


```python
rounds[0].table.tbody.td
```




    <td class="local">
    <figure>
    <img alt="Girona" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/2893.png">
    </img></figure>
    <span class="equipo_t2893">Girona</span>
    </td>



Then, we can catch all the matches within a round by:


```python
r = rounds[0]
matches = r.findAll('tr')
matches[1]
```




    <tr>
    <td class="local">
    <figure>
    <img alt="Girona" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/2893.png">
    </img></figure>
    <span class="equipo_t2893">Girona</span>
    </td>
    <td class="resultado"><span class="resultado-partido">0-0</span></td>
    <td class="visitante">
    <span class="equipo_t192">Valladolid</span>
    <figure>
    <img alt="Valladolid" src="https://e00-marca.uecdn.es/assets/sports/logos/football/png/72x72/192.png"/>
    </figure>
    </td>
    </tr>



To capture now the names of the local team and the away team, as we did for the round number:


```python
match = matches[1]
loc  = match.find('td', {'class': 'local'}).span.text
away = match.find('td', {'class': 'visitante'}).span.text
print(loc)
print(away)
```

    Girona
    Valladolid


If we define this in a loop of matches inside a loop of rounds, we can retreive the entire site!


```python
def crear_calendario(temp, path):
    
    global partidos_df # Use the defined empty dataframe
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
```


```python
partidos_df.head(5)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Round</th>
      <th>Match #</th>
      <th>Home team</th>
      <th>Away team</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Jornada 1</td>
      <td>1</td>
      <td>Girona</td>
      <td>Valladolid</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Jornada 1</td>
      <td>2</td>
      <td>Betis</td>
      <td>Levante</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Jornada 1</td>
      <td>3</td>
      <td>Celta</td>
      <td>Espanyol</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Jornada 1</td>
      <td>4</td>
      <td>Villarreal</td>
      <td>Real Sociedad</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Jornada 1</td>
      <td>5</td>
      <td>Barcelona</td>
      <td>Alavés</td>
    </tr>
  </tbody>
</table>
</div>




```python
partidos_df.tail()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Round</th>
      <th>Match #</th>
      <th>Home team</th>
      <th>Away team</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>375</th>
      <td>Jornada 38</td>
      <td>6</td>
      <td>Huesca</td>
      <td>Leganés</td>
    </tr>
    <tr>
      <th>376</th>
      <td>Jornada 38</td>
      <td>7</td>
      <td>Levante</td>
      <td>Atlético</td>
    </tr>
    <tr>
      <th>377</th>
      <td>Jornada 38</td>
      <td>8</td>
      <td>Real Madrid</td>
      <td>Betis</td>
    </tr>
    <tr>
      <th>378</th>
      <td>Jornada 38</td>
      <td>9</td>
      <td>Valladolid</td>
      <td>Valencia</td>
    </tr>
    <tr>
      <th>379</th>
      <td>Jornada 38</td>
      <td>10</td>
      <td>Sevilla</td>
      <td>Athletic</td>
    </tr>
  </tbody>
</table>
</div>



## 4 - Export to Excel



```python
# Export to Excel
# ---------------
partidos_writer = pd.ExcelWriter(path_to_save + '/matches_df.xlsx', engine='xlsxwriter')    
partidos_df.to_excel(partidos_writer, sheet_name='Matches_2018_2019')
partidos_writer.save()
```
