##################################################
# Get the laps that were slower than usual and
# classify as yellow flagged laps based on
# predesigned conditions
##################################################
# Author: Saisrinivasa Likhit Kota
# Copyright: Copyright 2020, F1 Data Project
# License: MIT
# Version: 0.0.1
# Email: saisrinivasa.likhit@students.iiit.ac.in
# Status: Dev
##################################################

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

def globalStat(countedValues):
  # make into 1d array
  Laptimes1D = []
  for laptimes in countedValues.values():
    for times in laptimes:
      Laptimes1D.append(times)
  
  global_mean = np.mean(Laptimes1D)
  global_std = np.std(Laptimes1D)

  return global_mean, global_std

def lapwiseStat(countedValues):
  lapwiseMean = dict()
  lapwiseStd = dict()

  for lap, laptimes in countedValues.items():
    lapwiseMean[lap] = np.mean(laptimes)
    lapwiseStd[lap] = np.std(laptimes)

  return lapwiseMean, lapwiseStd

def changeStat(countedValues):
  # calculating lapwise mean
  lapwiseMean = dict()
  for lap, laptimes in countedValues.items():
    lapwiseMean[lap] = np.mean(laptimes)

  # calculating lapwise change in mean
  change = dict()
  prev = 0
  for lap, laptimes in lapwiseMean.items():
    if prev == 0:
      prev = laptimes
      continue
    dm = (laptimes - prev)/prev
    prev = laptimes
    change[lap] = dm

  # cacluating mean and std of change of mean
  values = list(change.values())
  mean_change = np.mean(values)
  std_change = np.std(values)

  return change, mean_change, std_change

def lapwise_deviations(mean_lapwise, std_lapwise):
  p165, m165 = dict(),dict()

  for lap, _ in mean_lapwise.items():
    p165[lap] = mean_lapwise[lap] + (1.65*std_lapwise[lap])
    m165[lap] = mean_lapwise[lap] - (1.65*std_lapwise[lap])

  return m165, p165

def plot_t_statistic(countedValues):
  mean_lapwise, std_lapwise = lapwiseStat(countedValues)
  plt.figure("T-statistic")

  lists = sorted(mean_lapwise.items())
  x,y = zip(*lists)
  mean_of_all_times, std_of_all_times = globalStat(countedValues)
  t_stat = ((np.array(y)-mean_of_all_times)/std_of_all_times)
  plt.plot(x, t_stat, label="t-statistic")

  plt.axhline(y=2,color='red', linestyle='dashed')
  plt.axhline(y=1,color='green', linestyle='dashed')

  plt.xticks(x)
  plt.grid()
  plt.legend(loc='upper right')

  plt.show()

def plot_change(countedValues):
  change, mean_change, std_change = changeStat(countedValues)
  CHANGE_P165_LINE = mean_change + (1.65*std_change)
  CHANGE_M165_LINE = mean_change - (1.65*std_change)

  plt.figure("Change in Mean")

  lists = sorted(change.items())
  x,y = zip(*lists)
  plt.plot(x,y,label="change in mean")

  plt.axhline(y=CHANGE_P165_LINE, label="+1.65", color='red', linestyle='dashed')
  plt.axhline(y=CHANGE_M165_LINE, label="-1.65", color='green', linestyle='dashed')

  plt.xticks(x)
  plt.grid()
  plt.legend(loc='upper right')

def plot_mean_laptimes(countedValues):
  mean_of_all_times, std_of_all_times = globalStat(countedValues)
  RACETIME_MEAN = mean_of_all_times
  RACETIME_P165_LINE = mean_of_all_times + (1.65*std_of_all_times)
  RACETIME_M165_LINE = mean_of_all_times - (1.65*std_of_all_times)

  mean_lapwise, std_lapwise = lapwiseStat(countedValues)
  LAPWISE_M165_LINE, LAPWISE_P165_LINE = lapwise_deviations(mean_lapwise, std_lapwise)
  
  plt.figure("Mean Laptimes")
  
  lists = sorted(LAPWISE_P165_LINE.items())
  x,y = zip(*lists)
  plt.plot(x,y,label="+1.65 mean")

  lists = sorted(LAPWISE_M165_LINE.items())
  x,y = zip(*lists)
  plt.plot(x,y,label="-1.65 mean")

  lists = sorted(mean_lapwise.items())
  x,y = zip(*lists)
  plt.plot(x,y,label="test")

  plt.axhline(y=RACETIME_P165_LINE, label="+1.65 race", color='red', linestyle='dashed')
  plt.axhline(y=RACETIME_M165_LINE, label="-1.65 race", color='green', linestyle='dashed')
  plt.axhline(y=RACETIME_MEAN, label="mean",color='orange', linestyle='dashed')

  plt.xticks(x)
  plt.grid()
  plt.legend(loc='upper right')

def get_yellow_flag_laps_using_t_statistic(countedValues):
  mean_lapwise, std_lapwise = lapwiseStat(countedValues)

  lists = sorted(mean_lapwise.items())
  x,y = zip(*lists)
  x,y = np.array(x), np.array(y)

  mean_of_all_times, std_of_all_times = globalStat(countedValues)
  t_stat = (y-mean_of_all_times)/std_of_all_times

  UPPER, LOWER = 2, 0.5
  yellow = []
  index = 0
  END = len(x)
  while index < END:
    if t_stat[index]>UPPER:
      while index<END and t_stat[index]>LOWER:
        yellow.append(x[index])
        index+=1
    else:
      index+=1

  return yellow

def createTempDf(raceId, yellow_flag_laps):
  columns = ['raceId','lap']
  ret = pd.DataFrame(columns=columns)

  raceIds = [raceId]*len(yellow_flag_laps)

  ret.raceId = raceIds
  ret.lap = yellow_flag_laps

  return ret
  
def remove_laps_with_overtakes(yellow_flag_laps, raceOvertake):
  # to find sticks of consecutive laps
  sticks = []
  first = 0
  stick = []
  for lap in yellow_flag_laps:
    if first==0:
      first = 1
      cur = lap
      stick.append(lap)
      continue

    if lap==cur+1:
      stick.append(lap)
    else:
      sticks.append(stick)
      stick = [lap]
    cur = lap
  # add the ones that didn't get added at the end 
  if len(stick)>0:
    sticks.append(stick)
  # use sticks to select only those laps that have >1 lap consecutively as yellow

  final = []
  for stick in sticks:
    for lap in stick:
      num_overtakes = len(set(raceOvertake[raceOvertake.lap==lap].driverId))
      if num_overtakes==0:
        final.append(lap)
      else:
        break

  return final


if __name__ == "__main__":
  PITSTOPS_FILE = "./data/base/pit_stops.csv"
  LAPTIMES_FILE = "./data/base/lap_times.csv"
  OVERTAKE_FILE = "./data/derived/overtaking/overtaking.csv"
  DIR = "./data/derived/yellow/"

  pitstops_df = pd.read_csv(PITSTOPS_FILE)
  laptimes_df = pd.read_csv(LAPTIMES_FILE)
  overtake_df = pd.read_csv(OVERTAKE_FILE)

  # raceIds = [999]
  raceIds = set(pitstops_df['raceId'])
  
  # results dataframe
  columns = ['raceId','lap']
  ResultDf = pd.DataFrame(columns=columns)

  for race in tqdm(raceIds):

    # filter data for this lap
    raceLaptimes = laptimes_df[laptimes_df.raceId==race]
    racePitstops = pitstops_df[pitstops_df.raceId==race]
    raceOvertake = overtake_df[overtake_df.raceId==race]

    # drivers in this race
    DriverIds = set(raceLaptimes.driverId)

    # laps in this race
    Laps = list(set(raceLaptimes.lap))

    # get them in ascending order
    Laps.sort()   

    countedValues = dict()
    # removing laptimes with pitstops
    for lap in Laps:
      times = []
      for driver in DriverIds:
        # did driver take a pitstop
        pitstop_true = (driver in set(racePitstops[racePitstops.lap==lap].driverId)) | (driver in set(racePitstops[racePitstops.lap==(lap+1)].driverId))
        driver_did_not_do_lap = (lap>max(list(set(raceLaptimes[raceLaptimes.driverId==driver].lap))))
        if pitstop_true | driver_did_not_do_lap:
          continue
        laptime = raceLaptimes[(raceLaptimes.lap==lap)&(raceLaptimes.driverId==driver)].milliseconds.values[0]
        times.append(laptime)

      if len(times)==0:
        continue
      countedValues[lap] = times

    # GETTING LAPWISE AND RACEWISE STATS 
    # calculating mean and std for all times in this RACE, single values
    # mean_of_all_times, std_of_all_times = globalStat(countedValues)

    # LAPWISE mean and std, dict {lap:lap_mean}, dict {lap:lap_std}  
    # mean_lapwise, std_lapwise = lapwiseStat(countedValues)

    # lapwise CHANGE in mean laptimes, dict {lap: lap_change}, single values
    # change, mean_change, std_change = changeStat(countedValues)

    # t statistics
    yellow_flag_laps = get_yellow_flag_laps_using_t_statistic(countedValues)
    # remove laps with overtakes during yellow flag
    yellow_flag_laps = remove_laps_with_overtakes(yellow_flag_laps, raceOvertake)

    # create tmp dataframe
    tmpDf = createTempDf(race, yellow_flag_laps)

    # add to result dataframe
    ResultDf = ResultDf.append(tmpDf)

    ### PLOTS
    ### NOTE: uncomment to plot, set race_to_plot 
    # race_to_plot = race
    # if race==race_to_plot:
      # PLOTTING CHANGE
      # plot_change(countedValues) # uncomment to plot

      # PLOTTING MEAN 
      # plot_mean_laptimes(countedValues) # uncomment to plot

      # PLOTTING T STATISTIC
      # plot_t_statistic(countedValues) # uncomment to plot

    # print(ResultDf)
  ResultDf.sort_values(['raceId'], ascending=True, inplace=True)
  print(ResultDf)
  ResultDf.to_csv("yellow_flag.csv", index=False)
  # ResultDf.to_csv(DIR + "yellow_flag.csv",index=False)



    




