##################################################
## Infer the abnormal overtake values in data 
## generated from overtaking.py
##################################################
## Author: Saisrinivasa Likhit Kota
## Copyright: Copyright 2020, F1 Data Project
## Credits: [Saisrinivasa Likhit Kota]
## License: MIT
## Version: 0.1.0
## Mmaintainer: Saisrinivasa Likhit Kota
## Email: saisrinivasa.likhit@students.iiit.ac.in
## Status: Dev
##################################################

import pandas as pd
from tqdm import tqdm

if __name__ == "__main__":
    LAPTIMES_FILE = "./data/base/laptimes.csv"
    DIR = "./data/derived/overtaking/overtaking_race_"
    laptimes_df = pd.read_csv(LAPTIMES_FILE)
    raceIds = set(laptimes_df['raceId'])
    # raceIds = set([107])

    abnormal_races = set()
    start = 5
    end = 10
    deets = pd.DataFrame(columns=['raceId','laps','numberOvertaken'])
    for raceId in tqdm(raceIds):
      overtakes_df = pd.read_csv(DIR + str(raceId) + ".csv")

      laps = overtakes_df.columns[2:]
      for i, data in overtakes_df.iterrows():
        for lap in laps:
          element = data[lap]
          tmp = set(element[1:-1].split(','))
          if len(tmp) >= start and len(tmp) <= end:
            abnormal_races.add(raceId)
            tmpDf = pd.DataFrame({
              "raceId":[raceId],
              "laps":[lap],
              "numberOvertaken":[len(tmp)]
            })
            deets = deets.append(tmpDf)
    print(abnormal_races)
    print(deets)
    deets.to_csv("abnormalOvertakeValues.csv",index=False)

