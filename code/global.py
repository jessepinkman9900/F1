import pandas as pd
import numpy as np
from tqdm import tqdm

def create_globalDf(laptime_df, subtime_df):
  columns = subtime_df.columns[1:]
  global_df = subtime_df
  print(global_df)
  for x in range(1,len(columns)):
    cur_col, prev_col = columns[x], columns[x-1]
    list_cur_col, list_prev_col = np.array(global_df[cur_col]), np.array(global_df[prev_col])
    # print(list_cur_col)
    # print(list_prev_col)
    # print(type(list_cur_col))
    # print(type(list_cur_col[0]))
    list_cur_col = list_cur_col+list_prev_col
    global_df[cur_col] = list_cur_col
  print(global_df)
  return global_df


if __name__ == "__main__":
  BASE_LAP = "./data/derived/overtaking/laptimes/laptimes_race_"
  BASE_PIT = './data/derived/overtaking/pitstops/pitstops_race_'
  BASE_GLO = './data/derived/overtaking/global/global_race_'
  BASE_CAL = './data/derived/overtaking/subtracted/calculated_race_'
  CSV = ".csv"
  laptimes_df = pd.read_csv("./data/base/laptimes.csv")
  # raceIds = set(laptimes_df['raceId'])
  raceIds = [841]

  for raceId in raceIds:
    srid = str(raceId)
    laptime_df = pd.read_csv(BASE_LAP + srid + CSV)
    # pitstop_df = pd.read_csv(BASE_PIT + srid + CSV)
    subtime_df = pd.read_csv(BASE_CAL + srid + CSV)
    global_df = create_globalDf(laptime_df, subtime_df)
    global_df.to_csv(BASE_GLO + srid + CSV,index=False)

  pass

'''
cumulatiuve times doine
need to create files
BUT need to add status codes into the laptimes/pitstoptimes
'''