##################################################
## Scrape 2010 pitstop data
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

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs

if __name__ == "__main__":
  columns = ['raceId','driverId','stop','lap','time','duration','milliseconds']
  pitstopsDf = pd.DataFrame(columns=columns)
  driverDf = pd.read_csv('./data/base/drivers.csv')

  venues = ['bahrain','australia','malaysia','china','spain',
  'monaco','turkey','canada','europe', 'greatbritain','german',
  'hungary', 'belgium','italy','singapore','japan','korea',
  'brazil','abudhabi']

  raceIds = {
    'bahrain':337,
    'australia':338,
    'malaysia':339,
    'china':340,
    'spain':341,
    'monaco':342,
    'turkey':343,
    'canada':344,
    'europe':345,
    'greatbritain':346,
    'german':347,
    'hungary':348,
    'belgium':349,
    'italy':350,
    'singapore':351,
    'japan':352,
    'korea':353,
    'brazil':354,
    'abudhabi':355
  }
  
  links = {
    'german':'https://www.formula1.com/en/results.html/2010/races/870/germany/pit-stop-summary.html',
    'hungary':'https://www.formula1.com/en/results.html/2010/races/871/hungary/pit-stop-summary.html',
    'belgium':'https://www.formula1.com/en/results.html/2010/races/872/belgium/pit-stop-summary.html',
    'italy':'https://www.formula1.com/en/results.html/2010/races/873/italy/pit-stop-summary.html',
    'singapore':'https://www.formula1.com/en/results.html/2010/races/874/singapore/pit-stop-summary.html',
    'japan':'https://www.formula1.com/en/results.html/2010/races/875/japan/pit-stop-summary.html',
    'korea':'https://www.formula1.com/en/results.html/2010/races/876/south-korea/pit-stop-summary.html',
    'brazil':'https://www.formula1.com/en/results.html/2010/races/877/brazil/pit-stop-summary.html',
    'abudhabi':'https://www.formula1.com/en/results.html/2010/races/878/abu-dhabi/pit-stop-summary.html',
    'greatbritain':'https://www.formula1.com/en/results.html/2010/races/869/great-britain/pit-stop-summary.html',
    'europe':'https://www.formula1.com/en/results.html/2010/races/868/europe/pit-stop-summary.html',
    'canada':"https://www.formula1.com/en/results.html/2010/races/867/canada/pit-stop-summary.html",
    'turkey':"https://www.formula1.com/en/results.html/2010/races/866/turkey/pit-stop-summary.html",
    'monaco':"https://www.formula1.com/en/results.html/2010/races/865/monaco/pit-stop-summary.html",
    'spain':"https://www.formula1.com/en/results.html/2010/races/864/spain/pit-stop-summary.html",
    'china':"https://www.formula1.com/en/results.html/2010/races/863/china/pit-stop-summary.html",
    'malaysia':"https://www.formula1.com/en/results.html/2010/races/862/malaysia/pit-stop-summary.html",
    'australia':"https://www.formula1.com/en/results.html/2010/races/861/australia/pit-stop-summary.html",
    'bahrain':"https://www.formula1.com/en/results.html/2010/races/860/bahrain/pit-stop-summary.html"
  }


  for venue in venues:
    print(venue)

    raceId = raceIds[venue]
    link = links[venue]
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

  # print(pitstopsDf)
  pitstopsDf.to_csv("2010_pits.csv",index=False)