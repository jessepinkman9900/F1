##################################################
# Get std and mean of speeds of each driver for
# each race, speed obtained from laptime and
# circuit length. speed: meters/second [SI]
##################################################
# Author: Saisrinivasa Likhit Kota
# Copyright: Copyright 2020, F1 Data Project
# License: MIT
# Version: 0.0.1
# Email: saisrinivasa.likhit@students.iiit.ac.in
# Status: Dev
##################################################

import pandas as pd
from tqdm import tqdm
import numpy as np


if __name__ == '__main__':

    PITSTOPS_FILE = "./data/base/pit_stops.csv"
    LAPTIMES_FILE = "./data/base/lap_times.csv"
    OVERTAKE_FILE = "./data/derived/overtaking/overtaking.csv"
    RACES_FILE    = "./data/base/races.csv"
    CIRCUITS_FILE = "./data/base/circuits.csv"
    DIR = "./data/derived/speed/"

    pitStopsDf = pd.read_csv(PITSTOPS_FILE)
    lapTimesDf = pd.read_csv(LAPTIMES_FILE)
    overtakeDf = pd.read_csv(OVERTAKE_FILE)
    racesDf    = pd.read_csv(RACES_FILE)
    circuitsDf = pd.read_csv(CIRCUITS_FILE)

    # raceIds = [999]
    raceIds = set(pitStopsDf['raceId'])

    # results dataframe
    columns = ['raceId', 'lap', 'mean', 'std']
    RESULT_DF = pd.DataFrame(columns=columns)

    for race in tqdm(raceIds):

        # filter data for this lap
        raceLapTimes = lapTimesDf[lapTimesDf.raceId == race]
        racePitStops = pitStopsDf[pitStopsDf.raceId == race]
        raceOvertake = overtakeDf[overtakeDf.raceId == race]

        # drivers in this race
        DriverIds = set(raceLapTimes.driverId)

        # laps in this race
        Laps = list(set(raceLapTimes.lap))

        # get them in ascending order
        Laps.sort()

        countedValues = dict() # {driverId: []speed}

        # remove lap times with pitstops
        circuitId  = racesDf[racesDf.raceId == race].circuitId.values[0]
        RACE_DISTANCE_KM = circuitsDf[circuitsDf.circuitId == circuitId].kms.values[0]
        for lap in Laps:
            SPEEDS = []
            for driver in DriverIds:
                # did driver take pit stop
                pitstop_true = (driver in set(racePitStops[racePitStops.lap == lap].driverId))

                # did driver take pit stop
                # uncomment to account for 2 laps due to pitstop
                pitstop_true = (driver in set(racePitStops[racePitStops.lap == lap].driverId)) | (
                            driver in set(racePitStops[racePitStops.lap == (lap + 1)].driverId))
                # driver is out of race
                driver_did_not_do_lap = (lap>max(list(set(raceLapTimes[raceLapTimes.driverId == driver].lap))))

                if pitstop_true | driver_did_not_do_lap:
                    continue

                laptime_ms = raceLapTimes[(raceLapTimes.lap == lap) & (raceLapTimes.driverId == driver)].milliseconds.values[0]

                speed_mps = (RACE_DISTANCE_KM*1000000)/laptime_ms  # km/ms => m/s [SI Units]
                SPEEDS.append(speed_mps)

            if len(SPEEDS)==0:
                continue
            countedValues[lap] = SPEEDS
            # mean and std
            mean = np.mean(SPEEDS)
            std  = np.std(SPEEDS)

            # add to data frame
            ROW = pd.DataFrame({
                'raceId':[race],
                'lap':[lap],
                'mean':[mean],
                'std':[std],
            })

            RESULT_DF = RESULT_DF.append(ROW)

        RESULT_DF.to_csv(DIR + "speed_stats_pitstop_2_lap.csv", index=False)
    # pass