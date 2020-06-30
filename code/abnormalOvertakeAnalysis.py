##################################################
## Infer the abnormal overtake values in data 
## generated from overtaking.py
##################################################
## Author: Saisrinivasa Likhit Kota
## Copyright: Copyright 2020, F1 Data Project
## Credits: [Saisrinivasa Likhit Kota]
## License: MIT
## Version: 0.1.1
## Mmaintainer: Saisrinivasa Likhit Kota
## Email: saisrinivasa.likhit@students.iiit.ac.in
## Status: Dev
##################################################

import pandas as pd
from tqdm import tqdm

if __name__ == "__main__":
    PITSTOPS_FILE = "./data/base/pitstops.csv"
    DIR = "./data/derived/overtaking/overtaking_race_"
    pitstops_df = pd.read_csv(PITSTOPS_FILE)
    raceIds = set(pitstops_df['raceId'])
    # raceIds = set([107])

    abnormal_races = set()
    start = 4
    end = 17
    freq = []
    for _ in range(0,18):
      freq.append(0)
    deets = pd.DataFrame(columns=['raceId','laps','numberOvertaken'])
    for raceId in tqdm(raceIds):
      overtakes_df = pd.read_csv(DIR + str(raceId) + ".csv")

      laps = overtakes_df.columns[2:]
      for i, data in overtakes_df.iterrows():
        for lap in laps:
          # finding the abnormal instances
          element = data[lap]
          tmp = list(set(element[1:-1].split(',')))
          if len(tmp) >= start and len(tmp) <= end:
            abnormal_races.add(raceId)
            tmpDf = pd.DataFrame({
              "raceId":[raceId],
              "laps":[lap],
              "numberOvertaken":[len(tmp)]
            })
            deets = deets.append(tmpDf)

          # calculating freq for overtaking statistics
          ind = len(tmp)
          if len(tmp[0])==0:
            ind = 0
          freq[ind]+=1

    
    print(abnormal_races)
    print(len(abnormal_races))
    deets.to_csv("abnormalOvertakeValues.csv",index=False)
    # print(deets)

    # calculating overtake statistics
    overtaken = [i for i in range(0,18)]
    total = 0
    for i in range(0,18):
      total+=freq[i]
    percentages = [round((freq[i]*100)/total,3) for i in range(0,18)]
    overtakeStatistics = pd.DataFrame({
      "driversOvertaken":overtaken,
      "count":freq,
      "percentage":percentages
    })
    overtakeStatistics.to_csv("overtakeStatistics.csv", index=False)