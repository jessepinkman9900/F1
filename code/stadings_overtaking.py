import pandas as pd
import numpy as np
from tqdm import tqdm

def sort(global_time_df, lap):
  driverId = global_time_df['driverId'].to_numpy()
  tmp_df = pd.DataFrame(columns=['driverId','time'])
  tmp_df['driverId'] = driverId
  tmp_df['time'] = global_time_df.loc[:,lap]
  tmp_df.sort_values(['time'],axis=0, ascending=True,
   inplace=True, kind='quicksort',na_position='last')
  tmp_df = tmp_df.reset_index(drop=True) #reset order to forget base indexing
  return tmp_df

def get_position(standings, driver):
  x = standings.index[standings['driverId']==driver].tolist()
  return x[0]

def get_array(dId):
  res = []
  for _ in range(len(dId)):
    res.append([])
  # print(res)
  return res

def get_overtakes(prev, cur, dId):
  overtakes = get_array(dId)
  # print(prev)
  # print(cur)

  # print("lame: \n",cur)
  for index in range(len(dId)):
    driver = dId[index]
    prev_pos = get_position(prev, driver)
    cur_pos  = get_position(cur , driver)
    # print(index, cur_pos, prev_pos)
    if(cur_pos<prev_pos): #i.e who they overtook
      # need to modify (set subtraction)
      prev_dri_behind_me = set(prev.driverId[prev_pos+1:])
      cur_dri_behind_me = set(cur.driverId[cur_pos+1:])
      i_overtook = cur_dri_behind_me.difference(prev_dri_behind_me)
      # print(index,driver, list(i_overtook))
      overtakes[index]= (list(i_overtook))
  return overtakes

def createOvertakes(global_time_df):
  driverId = global_time_df['driverId'].to_numpy()
  prev_lap_standings = sort(global_time_df, 'lap_1')
  laps = global_time_df.columns[2:]
  overtakes = pd.DataFrame(columns=global_time_df.columns)
  overtakes['driverId']=driverId
  for lap in tqdm(laps):
    cur_lap_standings = sort(global_time_df, lap)
    overtaken_by = get_overtakes(prev_lap_standings, cur_lap_standings, driverId)
    # print(overtaken_by)
    overtakes[lap] = overtaken_by
    prev_lap_standings = cur_lap_standings
    # break
  return overtakes

if __name__ == "__main__":
  BASE_GLO = './data/derived/overtaking/global/global_race_'
  BASE_OT = './data/derived/overtaking/overtaking/overtaking_race_'
  CSV = ".csv"
  raceIds = [841]

  for raceId in tqdm(raceIds):
    srid = str(raceId)
    global_time_df = pd.read_csv(BASE_GLO + srid + CSV)
    overtakes_df = createOvertakes(global_time_df)
    overtakes_df.to_csv(BASE_OT + srid + CSV)

    test_df = pd.read_csv(BASE_OT + srid + CSV)
    # print(test_df)
  pass
    