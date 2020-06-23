##################################################
## Infer overtaking data from laptimes and pitstops data
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

__author__ = "Saisrinivasa Likhit Kota"
__copyright__ = "Copyright 2020, F1 Data Project"
__credits__ = ["Saisrinivasa Likhit Kota"]
__license__ = "MIT"
__version__ = "0.1.1"~
__maintainer__ = "Saisrinivasa Likhit Kota"
__email__ = "saisrinivasa.likhit@students.iiit.ac.in"
__status__ = "Dev"

import pandas as pd
from tqdm import tqdm

class Base:
  LAPTIMES_FILE = "./data/base/laptimes.csv"
  PITSTOPS_FILE = "./data/base/pitstops.csv"
  RESULTS_FILE = "./data/base/results.csv"
  SAVE_DIR = "./data/derived/overtaking/"
  SAVE_FILE = "overtaking_race_"
  CSV = ".csv"
  def __init__(self):
    self.laptimes_df = pd.read_csv(Base.LAPTIMES_FILE)
    self.pitstops_df = pd.read_csv(Base.PITSTOPS_FILE)
    self.results_df = pd.read_csv(Base.RESULTS_FILE)
    
  def getRaceIds(self):
    raceIds = set(self.laptimes_df['raceId'])
    return raceIds
  
  def saveAsCsv(self,df,raceId):
    # store the csv files in ./data/derived/overtaking/overtaking_race_<raceId>.csv
    return df.to_csv(Base.SAVE_DIR + Base.SAVE_FILE 
    + str(raceId) + Base.CSV, index = False)




class Laptimes(Base): # get df with the laptimes for a given race for each driver
  INF = int(1e8)
  def __init__(self):
    super().__init__()

  def fillDf(self, raceId, columnDf):
    ''' adds rows into the empty datafame 'columnDf',
    each row: [driverId, laptime for each lap]
    '''
    # laptimes for race with given raceId argument
    race_laptimes_df = self.laptimes_df[self.laptimes_df['raceId']==raceId]
    driverIds = list(set(race_laptimes_df['driverId']))

    # get number of laps in this race
    laps = list(set(race_laptimes_df['lap']))
    num_laps = len(laps)

    for index in range(len(driverIds)):
      '''using indexes instead of 'driverId in driverIds' so that it'll 
      be easy to add rows into the df 
      ''' 
      driverId = driverIds[index]
      # all the rows with the wanted driverId
      tmp = race_laptimes_df[race_laptimes_df['driverId']==driverId] 
      # all lap times for a driver in this race
      times = list(tmp.loc[:,'milliseconds']) 
      if len(times) != num_laps:
        for _ in range(num_laps-len(times)):
          # add default value INF for all laps without times in laptimes.csv
          times.append(Laptimes.INF) 

      row = [driverId]+times # final list to add into df
      columnDf.loc[index] = row

    return columnDf

  def createLaptimesDf(self, raceId):
    ''' create an empty df with just column names, 
    and then call fillDf()
    '''
    race_laptimes_df = self.laptimes_df[self.laptimes_df['raceId']==raceId]
    laps = list(set(race_laptimes_df['lap']))
    # append 'lap_' before lapnumber for easier readability 
    total_laps = ['lap_'+str(lap_num) for lap_num in laps]
    # create the headers for the dataframe
    columns = ['driverId'] + total_laps
    # create an empty dataframe with just column names
    columnDf = pd.DataFrame(columns=columns)
    return self.fillDf(raceId, columnDf)




class Pitstops(Base): # get the pistop times for each lap in a given race [default 0]
  def __init__(self):
    super().__init__()

  def fillDf(self, raceId, columnDf):
    ''' adds rows into the empty datafame 'columnDf',
    each row: [driverid, pitstop time for each lap]
    '''
    # get laptimes and pitstop times for the given raceId
    race_laptimes_df = self.laptimes_df[self.laptimes_df['raceId']==raceId]
    race_pitstops_df = self.pitstops_df[self.pitstops_df['raceId']==raceId]

    # get list of all the drivers and laps in this race
    driverIds = list(set(race_laptimes_df['driverId']))
    laps = list(set(race_laptimes_df['lap']))
    num_laps = len(laps)

    for index in range(len(driverIds)):    
      '''using indexes instead of 'driverId in driverIds' so that it'll 
      be easy to add rows into the df 
      '''         
      driverId = driverIds[index]
      ''' have a time array with all 0 and then 
      time[x]=t where x is a lap where pitstop occours 
      and t is duration in milliseconds'''
      time = [0 for _ in range(num_laps)]
      
      # all pitstop times for a driver in this race
      tmp = race_pitstops_df[race_pitstops_df['driverId']==driverId] 
      pit_time = tmp.loc[:,['lap','milliseconds']]  

      # filling laps where pitstops occour
      for _, r in pit_time.iterrows(): 
        lap_num, stop_time = int(r['lap']),int(r['milliseconds'])
        time[lap_num] = stop_time

      row = [driverId]+time   # final list to add into df
      columnDf.loc[index] = row

    return columnDf

  def createPistopsDf(self, raceId):
    ''' create an empty df with just column names, 
    and then call fillDf()
    '''
    # get laptimes for the given raceId
    race_laptimes_df = self.laptimes_df[self.laptimes_df['raceId']==raceId]

    # get list of the laps in this race
    laps = list(set(race_laptimes_df['lap']))
    total_laps = ['lap_'+str(lap_num) for lap_num in laps]

    # create the headers for the dataframe
    columns = ['driverId'] + total_laps
    # create an empty dataframe with just column names
    columnDf = pd.DataFrame(columns=columns)
    return self.fillDf(raceId, columnDf)




class ActualLaptimes(Base): # get the timing for a lap, remove the pitstop time included in laptimes.csv
  def __init__(self):
    super().__init__()

  def fillDf(self, laptimes, pitstops, columnDf):
    ''' adds rows into the empty datafame 'columnDf',
    each row: [driverId, laptime - pitstop time for each lap]
    '''
    columns = laptimes.columns
    columnDf[columns[0]] = laptimes[columns[0]] # copy driverId column
    # columnDf[columns[1]] = laptimes[columns[1]] # copy lap_1 column
    
    # lap_1 to final lap
    for column in columns[1:]:
      # subtract pitstop time from laptime
      columnDf[column] = laptimes[column] - pitstops[column] 

    # get cumulative sum
    for index in range(2,len(columns)):
      columnDf[columns[index]]+=columnDf[columns[index-1]]
    return columnDf
    
  def createActualLaptimesDf(self, laptimes, pitstops):
    ''' create an empty df with just column names, 
    and then call fillDf()
    '''
    # create an empty dataframe with just column names [col names taken from laptimes]
    columnDf = pd.DataFrame(columns=laptimes.columns)
    return self.fillDf(laptimes, pitstops, columnDf)




class Overtaking(Base): # get df of who each racer overtook and in which lap for a given race
  def __init__(self):
    super().__init__()

  def sort(self, actualLaptime, lap):
    ''' create the standings for this lap using the laptime '''
    driverIds = actualLaptime['driverId'].to_numpy()
    # create a tmp dataframe in which we will sort to get standings for this lap
    tmp = pd.DataFrame(columns=['driverId','time'])
    # fill dataframe with the driverIds
    tmp['driverId'] = driverIds
    # fill dataframe with times for this lap
    tmp['time'] = actualLaptime.loc[:, lap]

    # sort the dataframe based on the timing in 'time' column 
    tmp.sort_values(['time'], axis=0, ascending=True, 
    inplace=True, kind='quicksort', na_position='last')
    # reset order to forget base indexing before sorting
    tmp = tmp.reset_index(drop=True) 
    return tmp
  
  def getPosition(self, standings, driver):
    ''' get the position of the drive in the standings for this lap '''
    return standings.index[standings['driverId']==driver].tolist()[0]

  def legitimateOvertakes(self, raceId, lap, racers_overtaken):
    print(raceId, lap)
    lap = lap.split("_")[1]
    # if each driver in racers_overtaken was still racing when this overtake happened
    # i.e it is wthin the number of laps they completed as given in results.csv
    final = []
    for racer in racers_overtaken:
      laps_done = self.results_df[(self.results_df['raceId']==raceId) & (self.results_df['driverId']==racer)]['laps']
      # equal to because racer completed laps_done laps, racer gets out of race in the incomplete lap that will not be counted in laps_done
      if int(lap)<=int(laps_done): # int conversion, beacuse stored as string in df
        final.append(racer)
    return set(final)

  def getOvertakes(self, raceId, lap, prev, cur, driverIds):
    ''' get list containg a list of racers each driver overtook in this lap '''
    overtakes = [[] for _ in range(len(driverIds))] #list to store list of all racers a driver overtook
    for index in range(len(driverIds)):
      driver = driverIds[index]

      # get position of driver in last lap and this lap
      pos_last_lap = self.getPosition(prev, driver)
      pos_this_lap = self.getPosition(cur, driver)

      #add racers to list of position of racer improves
      if pos_this_lap<pos_last_lap:
        #all the racers behind me now who were not behind me in prev lap
        drivers_behind_me_last_lap = set(prev.driverId[pos_last_lap+1:])
        drivers_behind_me_this_lap = set(cur.driverId[pos_this_lap+1:])
        racers_overtaken = drivers_behind_me_this_lap.difference(drivers_behind_me_last_lap)
        # filter the overtakes based on if it is legitimate overtake or of it is due to retirement or other resons
        racers_overtaken = self.legitimateOvertakes(raceId, lap, racers_overtaken)
        # add list of all drivers i overtook into the overtakes list
        overtakes[index] = list(racers_overtaken)
    return overtakes

  def fillDf(self, raceId, actualLaptime, columnDf):
    ''' adds rows into the empty datafame 'columnDf',
    each row: [driverId, list of drivers driver overtook for each lap]
    '''
    driverIds = actualLaptime['driverId'].to_numpy()
    laps = actualLaptime.columns[2:] #lap2 onwards
    columnDf['driverId'] = driverIds
    prev_lap_standins = self.sort(actualLaptime, 'lap_1')

    for lap in laps:
      cur_lap_standings = self.sort(actualLaptime, lap)
      overtook = self.getOvertakes(raceId, lap, prev_lap_standins, cur_lap_standings, driverIds)
      columnDf[lap] = overtook
      prev_lap_standins = cur_lap_standings
    return columnDf

  def createOvertakingDf(self, raceId, actualLaptime):
    ''' create an empty df with just column names, 
    and then call fillDf()
    '''
    # create an empty dataframe with just column names [col names taken from actualLaptimes]
    columnDf = pd.DataFrame(columns=laptimes.columns)
    return self.fillDf(raceId, actualLaptime, columnDf)


if __name__ == "__main__":
    raceIds = Base().getRaceIds()
    # raceIds = [841]
    LAPTIMES, PITSTOPS, ACTUAL_LAPTIMES, OVERTAKES, BASE = Laptimes(), Pitstops(), ActualLaptimes(), Overtaking(), Base()
    for raceId in tqdm(raceIds):
      laptimes = LAPTIMES.createLaptimesDf(raceId)
      pitstops = PITSTOPS.createPistopsDf(raceId)
      actualLaptime = ACTUAL_LAPTIMES.createActualLaptimesDf(laptimes, pitstops)
      overtakes = OVERTAKES.createOvertakingDf(raceId, actualLaptime)
      BASE.saveAsCsv(overtakes,raceId)