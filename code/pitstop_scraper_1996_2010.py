##################################################
## Scrape pitstop data for seasons 1996-2010
##################################################
## Author: Saisrinivasa Likhit Kota
## Copyright: Copyright 2020, F1 Data Project
## Credits: [Saisrinivasa Likhit Kota]
## License: MIT
## Version: 0.0.1
## Mmaintainer: Saisrinivasa Likhit Kota
## Email: saisrinivasa.likhit@students.iiit.ac.in
## Status: Dev
##################################################

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from tqdm import tqdm
import numpy as np

def CreateLinks():
  def twoD_to_oneD(links):
    final = []
    for link in links:
      for lin in link:
        final.append(lin)
    return final

  LINKS = []
  for YEAR in tqdm(range(1996,2011)):
    BASE = f'https://www.formula1.com'
    URL = f'https://www.formula1.com/en/results.html/{YEAR}/races.html'
    
    races_page = requests.get(URL)
    soup = bs(races_page.content, 'html.parser')
    
    races_this_year_scroll = soup.findAll('ul',attrs={'class':"resultsarchive-filter ResultFilterScrollable"})[2]
    races_this_year_links = races_this_year_scroll.findAll('li')
    LINKS_for_year = []
    for race_link in races_this_year_links:

      link_to_page = race_link.find('a',href=True)
      link_to_page = link_to_page['href']
      LINKS_for_year.append(link_to_page)
    # print(YEAR)
    LINKS_for_year = LINKS_for_year[1:] # remove /en/results.html/1996/races.html
    # print(LINKS_for_year)
    LINKS.append(LINKS_for_year)
    # print(LINKS)
      
  LINKS = twoD_to_oneD(LINKS)

  # replace 'race-result.html' with 'pit-stop-summary.html'
  for index in range(len(LINKS)):
    LINKS[index] = BASE + LINKS[index].replace('race-result.html','pit-stop-summary.html')

  # print(LINKS)
  linksDf = pd.DataFrame(columns=['link'])
  linksDf.link = LINKS
  linksDf.to_csv('./data/1996-2010/links_1996_2010.csv',index=False)

  return linksDf

def getLinks():
  return pd.read_csv("./data/1996-2010/links_1996_2010.csv")

def getRaceId(url):
  split = url.split("/")
  raceid_tmp = split[5]+":"+split[8]
  return raceid_tmp

def getPitstops(link):
  # print(link)
  columns = ['raceId','driverId','stop','lap','time','duration','milliseconds']
  pitstopsDf = pd.DataFrame(columns=columns)

  raceId = getRaceId(link)
  # break
  page = requests.get(link)
  soup = bs(page.content,'html.parser')
  table = soup.find('table')
  tb = table.find('tbody')

  values = []
  for cur in tb.select('tr'):
      stop = cur.find('td',attrs={'class':'dark'}).text
      driver = cur.find('td',attrs={'class':'dark bold'}).text.split("\n")[-2] # use this code to find driverId
      lap = cur.find('td',attrs={'class':'bold hide-for-mobile'}).text
      timeOfDay = cur.find('td',attrs={'class':'dark bold hide-for-mobile'}).text
      time = cur.findAll('td',attrs={'class':'dark bold'})[-2].text
      

      into_sec = time.split(':')
      if len(into_sec)==1:
        ms = int(float(into_sec[0])*1000)
      elif len(into_sec)==2:
        ms = int((60000*float(into_sec[0]))+(1000*float(into_sec[1])))
      tmp = {'raceId':raceId, 'driverId':driver, 'stop':stop, 'lap':lap, 'duration':time,'time':timeOfDay, 'milliseconds':ms} 
      values.append(tmp)

  for c in values:
    driverIds = driverDf[driverDf.code==c['driverId']].driverId.values
    if len(driverIds)==0:
      driverId = c['driverId']
    else:
      driverId = driverIds[0]

    tmpdf = pd.DataFrame({
      "raceId" : [c['raceId']],
      "stop" : [c["stop"]],
      "driverId" : [driverId],
      "lap" : [c['lap']],
      "time" : [c['time']],
      "duration" : [c['duration']],
      'milliseconds' : [c['milliseconds']]
    })
    pitstopsDf = pitstopsDf.append(tmpdf)

  return pitstopsDf

def convertRaceId():
  pitstopsDf = pd.read_csv('./data/1996-2010/pitstops_1996_2010.csv')

  gp_dict = {
    'san-marino':'San Marino Grand Prix',
    'malaysia':'Malaysian Grand Prix',
    'great-britain':'British Grand Prix', 
    'germany':'German Grand Prix', 
    'europe':'European Grand Prix', 
    'turkey':'Turkish Grand Prix', 
    'singapore':'Singapore Grand Prix', 
    'argentina':'Argentine Grand Prix', 
    'spain':'Spanish Grand Prix', 
    'brazil':'Brazilian Grand Prix', 
    'italy':'Italian Grand Prix', 
    'south-korea':'Korean Grand Prix', 
    'japan':'Japanese Grand Prix', 
    'abu-dhabi':'Abu Dhabi Grand Prix', 
    'monaco':'Monaco Grand Prix', 
    'portugal':'Portuguese Grand Prix', 
    'canada':'Canadian Grand Prix', 
    'luxembourg':'Luxembourg Grand Prix', 
    'china':'Chinese Grand Prix', 
    'bahrain':'Bahrain Grand Prix', 
    'united-states':'United States Grand Prix', 
    'france':'French Grand Prix', 
    'belgium':'Belgian Grand Prix', 
    'hungary':'Hungarian Grand Prix', 
    'austria':'Austrian Grand Prix', 
    'australia':'Australian Grand Prix'
  }

  racesDf = pd.read_csv('./data/base/races.csv')

  for index, row in tqdm(pitstopsDf.iterrows()):
    cur_raceid = row.raceId
    split = cur_raceid.split(":")
    year, gp = int(split[0]),gp_dict[split[1]]

    real_raceId = racesDf[(racesDf.year==year)&(racesDf.name==gp)].raceId.values
    if len(real_raceId)==0:
      update_val = cur_raceid
      print(update_val)
    else:
      update_val = real_raceId[0]

    pitstopsDf.at[index,'raceId'] = update_val

  pitstopsDf.to_csv("./data/1996-2010/pitstops_1996_2010.csv",index=False)


if __name__ == "__main__":

  driverDf = pd.read_csv('./data/base/drivers.csv')
  columns = ['raceId','driverId','stop','lap','time','duration','milliseconds']
  ResultDf = pd.DataFrame(columns=columns)

  # scrape links for pitsop data
  # NOTE: if not scraped use function CreateLinks() instead
  LinksDf = getLinks()

  # scrape the pitstop data
  # NOTE: if already scraped comment till 190
  for link in tqdm(LinksDf.link):
    pitstopsDf = pd.DataFrame(columns=columns)

    pitstopsDf = getPitstops(link)

    ResultDf = ResultDf.append(pitstopsDf)

  ResultDf.to_csv("./data/1996-2010/pitstops_1996_2010.csv",index=False)
  
  # convert raceIds from year:race into raceId from races.csv
  convertRaceId()
  