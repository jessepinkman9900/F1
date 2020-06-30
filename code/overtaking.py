##################################################
## Infer overtaking data from laptimes and pitstops data
##################################################
## Author: Saisrinivasa Likhit Kota
## Copyright: Copyright 2020, F1 Data Project
## Credits: [Saisrinivasa Likhit Kota]
## License: MIT
## Version: 0.2.1
## Mmaintainer: Saisrinivasa Likhit Kota
## Email: saisrinivasa.likhit@students.iiit.ac.in
## Status: Dev
##################################################


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



class Overtakes(Base):
  def __init__(self):
    super().__init__()
    self.columns = ['raceId', 'driverId', 'lap', 'driverOvertaken']
    self.overtakeDf = pd.DataFrame(columns=self.columns)

  def createPanel(self, raceId, data):
    res = pd.DataFrame(columns=self.columns)
    driverId = data.driverId
    laps = [lap.split("_")[1] for lap in data.keys()[2:]]

    for lap in laps:
      overtaken_driverIds = data["lap_"+str(lap)]
      for driverId in overtaken_driverIds:
        tmp = pd.DataFrame({
          "raceId" : [raceId],
          "driverId" : [driverId],
          "lap" : [lap],
          "driverOvertaken" : [driverId]
        })
        res = res.append(tmp)
    return res

  def addToOvertakeDf(self, raceId, overtakes):
    # iterate through each row in overtakes and
    # add each column in that row into the self.overtakeDf dataframe
    for index, data in overtakes.iterrows():
      tmp = self.createPanel(raceId, data)
      self.overtakeDf = self.overtakeDf.append(tmp)

  def legitimateOvertakes(self, raceId, lap, drivers_overtaken):
    lap = lap.split("_")[1]
    # if each driver in racers_overtaken was still racing when this overtake happened
    # i.e it is wthin the number of laps they completed as given in results.csv
    final = []
    for driverId in drivers_overtaken:
      laps_done = self.results_df[(self.results_df.raceId==raceId) & (self.results_df.driverId==driverId)].laps
      # equal to because racer completed laps_done laps,
      # racer gets out of race in the incomplete lap that will not be counted in laps_done
      if int(lap) <= int(laps_done): # int conversion, beacuse stored as string in df
        final.append(driverId)

    # check for pitstop in lap and lap-1
    for driverId in final:
      tmp = self.pitstops_df[(self.pitstops_df.raceId==raceId) & (self.pitstops_df.driverId==driverId)]
      pitstop_true = (int(lap) in set(tmp.lap))|(int(lap)-1 in set(tmp.lap))
      if pitstop_true:
        final.remove(driverId)
    return set(final)

  def getPosition(self, standings, driverId):
    ''' get the position of the drive in the standings for this lap '''
    return int(standings[standings.driverId==driverId].position)

  def getOvertakes(self, raceId, driverIds, lap, prev_lap_standinds, cur_lap_standings):
    ''' get list containg a list of racers each driver overtook in this lap '''
    #list to store list of all racers a driver overtook
    overtakes = [[] for _ in range(len(driverIds))]
    # sorting
    prev_lap_standinds.sort_values(['position'], axis=0, ascending=True, inplace=True, kind='quicksort', na_position='last')
    cur_lap_standings.sort_values(['position'], axis=0, ascending=True, inplace=True, kind='quicksort', na_position='last')

    for index in range(len(driverIds)):
      driverId = driverIds[index]

      # get position of driver in last lap and this lap
      prev_lap_pos = self.getPosition(prev_lap_standinds, driverId)
      cur_lap_pos = self.getPosition(cur_lap_standings, driverId)

      # add driverIds to list of position of racer improves
      # all the driverIds behind me now who were not behind me in prev lap
      drivers_behind_me_prev_lap = set(prev_lap_standinds.driverId[prev_lap_pos+1:])
      drivers_behind_me_cur_lap = set(cur_lap_standings.driverId[cur_lap_pos+1:])
      drivers_overtaken = drivers_behind_me_cur_lap.difference(drivers_behind_me_prev_lap)
      # possible that driver might have moved ahead
      if driverId in drivers_overtaken:
        drivers_overtaken.remove(driverId)
      # filter the overtakes based on if it is legitimate overtake or
      # of it is due to retirement or other resons
      drivers_overtaken = self.legitimateOvertakes(raceId, lap, drivers_overtaken)
      # add list of all drivers i overtook into the overtakes list
      overtakes[index] = list(drivers_overtaken)
    return overtakes


  def getStandings(self, driverIds, positions):
    # creadting a df with driverId and postion
    # so that can query postion of driver in this lap
    tmp = pd.DataFrame(columns=['driverId','position'])
    tmp.driverId = driverIds
    tmp.position = positions
    return tmp

  def fillDf(self, raceId, positionsDf, columnDf):
    ''' adds rows into the empty datafame 'columnDf',
    each row: [driverId, list of drivers driver overtook for each lap]
    '''
    # numpy array of the driverIds
    driverIds = positionsDf.driverId.to_numpy()
    # lap_1 taken as base to start comparing
    laps = positionsDf.columns[2:] # lap_2 onwards
    # add the list of drivers to dataframe
    columnDf.driverId = driverIds

    prev_lap_standinds = self.getStandings(driverIds, positionsDf['lap_1'])
    # comparing postion change bw last lap and this lap
    # if a driver who was ahead of you last lap fall behind this lap
    # counts as overtake
    for lap in laps:
      cur_lap_standings = self.getStandings(driverIds, positionsDf[lap])
      overtook = self.getOvertakes(raceId, driverIds, lap, prev_lap_standinds, cur_lap_standings)
      columnDf[lap] = overtook
      prev_lap_standinds = cur_lap_standings
    return columnDf

  def saveOvertakeDf(self):
    # save in "./data/derived/overtaking/" as "overtaking.csv"
    self.overtakeDf.to_csv(Base.SAVE_DIR + "overtaking.csv",index=False)

  def createOvertakesDf(self, raceId, positionsDf):
    ''' create an empty df with just column names,
    and then call fillDf()
    '''
    columnDf = pd.DataFrame(columns=positionsDf.columns)
    return self.fillDf(raceId, positionsDf, columnDf)



class Positions(Base):
  def __init__(self):
    super().__init__()

  def fillDf(self, raceId, columnDf):
    ''' adds rows into the empty datafame 'columnDf',
    each row: [driverId, position from standings for each lap]
    '''
    # laptimes for race with given raceId argument
    race_laptimes_df = self.laptimes_df[self.laptimes_df.raceId==raceId]
    # list of driver ids in this race
    driverIds = list(set(race_laptimes_df.driverId))
    # get number of laps in this race
    laps = set(race_laptimes_df.lap)
    num_laps = len(laps)
    # if no lap time then default last place
    INF = len(driverIds)
    for index in range(len(driverIds)):
      '''using indexes instead of 'driverId in driverIds' so that it'll
      be easy to add rows into the df
      '''
      driverId = driverIds[index]
      # all the rows with the wanted driverId
      tmp = race_laptimes_df[race_laptimes_df.driverId==driverId]
      # lapwise positions (standings) for a driver in this race
      positions = list(tmp.loc[:,'position'])
      # if driver did complete all laps of race then add defualt postion value
      if len(positions) != num_laps:
        for _ in range(num_laps-len(positions)):
          # add default value INF for all laps without position in laptimes.csv
          positions.append(INF)
      # crete the list to add to dataframe
      row = [driverId]+positions
      columnDf.loc[index] = row
    return columnDf

  def createPositionsDf(self, raceId):
    ''' create an empty df with just column names,
    and then call fillDf()
    '''
    # get laptimes for this race
    race_laptimes_df = self.laptimes_df[self.laptimes_df.raceId==raceId]
    # get a set of all the laps {1,2 ...}
    laps = set(race_laptimes_df.lap)
    # list of laps (string) ['lap_1', 'lap_2', ...]
    total_laps = ['lap_'+str(lap_num) for lap_num in laps]
    # columns to use to make dataframe ['driverId', 'lap_1', 'lap_2', ...]
    columns = ['driverId'] + total_laps
    # create dataframe
    columnDf = pd.DataFrame(columns=columns)
    return self.fillDf(raceId, columnDf)



if __name__ == "__main__":
    raceIds = Base().getRaceIds()
    # raceIds = [118]
    BASE, OVERTAKES, POSITIONS  = Base(), Overtakes(), Positions()
    for raceId in tqdm(raceIds):
      positions = POSITIONS.createPositionsDf(raceId)
      overtakes = OVERTAKES.createOvertakesDf(raceId, positions)
      OVERTAKES.addToOvertakeDf(raceId, overtakes)
      BASE.saveAsCsv(overtakes,raceId)
    OVERTAKES.saveOvertakeDf()