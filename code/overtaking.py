import pandas as pd

class Base:
  LAPTIMES_FILE = "./data/base/laptimes.csv"
  PITSTOPS_FILE = "./data/base/pitstops.csv"
  def __init__(self):
    self.laptimes_df = pd.read_csv(Base.LAPTIMES_FILE)
    self.pitstops_df = pd.read_csv(Base.PITSTOPS_FILE)
    
  def getRaceIds(self):
    raceIds = set(self.laptimes_df['raceId'])
    return raceIds
  
  def saveAsCsv(self,df,name):
    return df.to_csv(name, index = False)

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


class ActualLaptimes:
  pass

class Overtaking:
  pass

if __name__ == "__main__":
    raceIds = Base().getRaceIds()
    # raceIds = [841]
    for raceId in raceIds:
      laptimes = Laptimes().createLaptimesDf(raceId)
      pit = Pitstops().createPistopsDf(raceId)
      Base().saveAsCsv(pit,'test.csv')
      print(pit)
      break