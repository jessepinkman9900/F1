##################################################
## Get racer statistics from laptimes.csv and pitstops.csv
## 1. get number of racers racing per lap
## 2. get avg number of racers racing per race
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
from tqdm import tqdm

if __name__ == "__main__":
    PITSTOPS_FILE = "./data/base/pit_stops.csv"
    LAPTIMES_FILE = "./data/base/lap_times.csv"
    DIR = "./data/derived/racers/"

    pitstops_df = pd.read_csv(PITSTOPS_FILE)
    laptimes_df = pd.read_csv(LAPTIMES_FILE)

    # raceIds = set([845])
    raceIds = set(pitstops_df['raceId'])

    racersPerLapColumns = ['raceId','lap','racersRacingThisLap']
    racersPerLap_df = pd.DataFrame(columns=racersPerLapColumns)

    racersPerRaceColumns = ['raceId','racersPerRace']
    racersPerRace_df = pd.DataFrame(columns=racersPerRaceColumns)

    for raceId in tqdm(raceIds):
      raceLaptimes = laptimes_df[laptimes_df.raceId==raceId]
      racePitstops = pitstops_df[pitstops_df.raceId==raceId]
      
      racersRacingThisRace = 0

      raceLaps = list(set(raceLaptimes.lap))
      for lap in raceLaps:
        racersRacingThisLap = set(raceLaptimes[raceLaptimes.lap==lap].driverId)
        pitstopsThisLap = racePitstops[racePitstops.lap==lap]
        pittedRacers = set(pitstopsThisLap.driverId)

        # remove those who took pitstop
        # finalListOfRacers = []
        # for driver in racersRacingThisLap:
        #   pitstop_true = driver in pittedRacers
        #   if pitstop_true:
        #     continue
        #   finalListOfRacers.append(driver)

        # add them to the racersPerLap_df
        numberOfRacersThisLap = len(racersRacingThisLap)
        tmpDf = tmpDf = pd.DataFrame({
              "raceId":[raceId],
              "lap":[lap],
              "racersRacingThisLap":[numberOfRacersThisLap]
            })
        racersPerLap_df = racersPerLap_df.append(tmpDf)

        # cumulative sum
        racersRacingThisRace += numberOfRacersThisLap

      # calculate avg racers per race and add them to racersPerRace_df
      avgRacersThisRace = racersRacingThisRace/len(raceLaps)
      tmpDf = pd.DataFrame({
        "raceId":[raceId],
        "racersPerRace":[avgRacersThisRace]
      })
      racersPerRace_df = racersPerRace_df.append(tmpDf)

    # sort by raceId
    racersPerLap_df.sort_values(['raceId'],ascending=True, inplace=True)
    racersPerRace_df.sort_values(['raceId'],ascending=True, inplace=True)

    # save as .csv file
    racersPerRace_df.to_csv(DIR + "racersPerRace.csv",index=False)
    racersPerLap_df.to_csv(DIR + "racersPerLap.csv", index=False)
        
          

