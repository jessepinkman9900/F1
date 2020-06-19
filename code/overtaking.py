import pandas as pd
from tqdm import tqdm

class Base:
  LAPTIMES_FILE = "./data/base/laptimes.csv"
  PITSTOPS_FILE = "./data/base/pitstops.csv"
  SAVE_DIR = "./data/derived/overtaking/"
  SAVE_FILE = "overtaking_race_"
  CSV = ".csv"
  def __init__(self):
    self.laptimes_df = pd.read_csv(Base.LAPTIMES_FILE)
    self.pitstops_df = pd.read_csv(Base.PITSTOPS_FILE)
    
  def getRaceIds(self):
    raceIds = set(self.laptimes_df['raceId'])
    return raceIds
  
  def saveAsCsv(self,df,raceId):
    return df.to_csv(Base.SAVE_DIR + Base.SAVE_FILE 
    + str(raceId) + Base.CSV, index = False)

class Laptimes(Base):
  INF = int(1e8)
  def __init__(self):
    super().__init__()

  def fillDf(self, raceId, columnDf):
    ''' adds rows into the empty datafame 'col_df',
    each row: [driverid, laptime for each lap]
    '''
    race_laptimes_df = self.laptimes_df[self.laptimes_df['raceId']==raceId]
    driverIds = list(set(race_laptimes_df['driverId']))
    laps = list(set(race_laptimes_df['lap']))
    num_laps = len(laps)

    for index in range(len(driverIds)):
      '''using indexes instead of 'driverId in driverIds' so that it'll 
      be easy to add rows into the df 
      ''' 
      driverId = driverIds[index]
      tmp = race_laptimes_df[race_laptimes_df['driverId']==driverId] # all the rows with the wanted driverId
      times = list(tmp.loc[:,'milliseconds']) # all lap times for a driver in this race
      if len(times) != num_laps:
        for _ in range(num_laps-len(times)):
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
    total_laps = ['lap_'+str(lap_num) for lap_num in laps]
    columns = ['driverId'] + total_laps
    columnDf = pd.DataFrame(columns=columns)
    return self.fillDf(raceId, columnDf)

class Pitstops(Base):
  def __init__(self):
    super().__init__()

  def fillDf(self, raceId, columnDf):
    ''' adds rows into the empty datafame 'col_df',
    each row: [driverid, laptime for each lap]
    '''
    race_laptimes_df = self.laptimes_df[self.laptimes_df['raceId']==raceId]
    race_pitstops_df = self.pitstops_df[self.pitstops_df['raceId']==raceId]
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
    race_laptimes_df = self.laptimes_df[self.laptimes_df['raceId']==raceId]
    laps = list(set(race_laptimes_df['lap']))
    total_laps = ['lap_'+str(lap_num) for lap_num in laps]
    columns = ['driverId'] + total_laps
    columnDf = pd.DataFrame(columns=columns)
    return self.fillDf(raceId, columnDf)


class ActualLaptimes(Base): # get the timing for a lap, remove the pitstop time included in laptimes.csv
  def __init__(self):
    super().__init__()

  def fillDf(self, laptimes, pitstops, columnDf):
    columns = laptimes.columns
    columnDf[columns[0]] = laptimes[columns[0]] # copy driverId column
    columnDf[columns[1]] = laptimes[columns[1]] # copy driverId column
    
    for column in columns[2:]:
      columnDf[column] = laptimes[column] - pitstops[column] #subtract pitstop time from laptime
    
    return columnDf
    
  def createActualLaptimesDf(self, laptimes, pitstops):
    columnDf = pd.DataFrame(columns=laptimes.columns)
    return self.fillDf(laptimes, pitstops, columnDf)

class Overtaking(Base):
  def __init__(self):
    super().__init__()

  def sort(self, actualLaptime, lap):
    driverIds = actualLaptime['driverId'].to_numpy()
    tmp = pd.DataFrame(columns=['driverId','time'])
    tmp['driverId'] = driverIds
    tmp['time'] = actualLaptime.loc[:, lap]
    tmp.sort_values(['time'], axis=0, ascending=True, 
    inplace=True, kind='quicksort', na_position='last')
    tmp = tmp.reset_index(drop=True) #reset order to forget base indexing before sorting
    return tmp
  
  def getPosition(self, standings, driver):
    return standings.index[standings['driverId']==driver].tolist()[0]

  def getOvertakes(self, prev, cur, driverIds):
    overtakes = [[] for _ in range(len(driverIds))] #list to store list of all racers a driver overtook
    for index in range(len(driverIds)):
      driver = driverIds[index]
      pos_last_lap = self.getPosition(prev, driver)
      pos_this_lap = self.getPosition(cur, driver)
      #add racers to list of position of racer improves
      if pos_this_lap<pos_last_lap:
        #all the racers behind me now who were not behind me in prev lap
        drivers_behind_me_last_lap = set(prev.driverId[pos_last_lap+1:])
        drivers_behind_me_this_lap = set(cur.driverId[pos_this_lap+1:])
        racers_overtaken = drivers_behind_me_this_lap.difference(drivers_behind_me_last_lap)
        overtakes[index] = list(racers_overtaken)
    return overtakes

  def fillDf(self, actualLaptime, columnDf):
    driverIds = actualLaptime['driverId'].to_numpy()
    laps = actualLaptime.columns[2:] #lap2 onwards
    columnDf['driverId'] = driverIds
    prev_lap_standins = self.sort(actualLaptime, 'lap_1')

    for lap in laps:
      cur_lap_standings = self.sort(actualLaptime, lap)
      overtook = self.getOvertakes(prev_lap_standins, cur_lap_standings, driverIds)
      columnDf[lap] = overtook
      prev_lap_standins = cur_lap_standings
    return columnDf

  def createOvertakingDf(self, actualLaptime):
    columnDf = pd.DataFrame(columns=laptimes.columns)
    return self.fillDf(actualLaptime, columnDf)


if __name__ == "__main__":
    raceIds = Base().getRaceIds()
    # raceIds = [841]
    for raceId in tqdm(raceIds):
      laptimes = Laptimes().createLaptimesDf(raceId)
      pitstops = Pitstops().createPistopsDf(raceId)
      actualLaptime = ActualLaptimes().createActualLaptimesDf(laptimes, pitstops)
      overtakes = Overtaking().createOvertakingDf(actualLaptime)
      Base().saveAsCsv(overtakes,raceId)
      print(overtakes)
      break