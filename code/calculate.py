import pandas as pd
import numpy as np
from tqdm import tqdm

def remove_pit_time(laptime_df, pitstop_df):
  res_df = pd.DataFrame(columns=laptime_df.columns)
  columns = laptime_df.columns[1:]
  print(columns) #without driverId
  res_df[laptime_df.columns[0]] = laptime_df[laptime_df.columns[0]]
  for column in columns:
    res_df[column] = laptime_df[column]-pitstop_df[column]
  #   pass
  # laptime_df.subtract(pitstop_df)
  print(res_df) 
  return res_df.astype(int)
  


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
    pitstop_df = pd.read_csv(BASE_PIT + srid + CSV)
    # print(laptime_df.columns)
    # print(pitstop_df.columns)
    # print(laptime_df.columns==pitstop_df.columns)
    # global_df = create_globalDf(laptime_df, pitstop_df)
    lt_wo_ps = remove_pit_time(laptime_df, pitstop_df)
      # print(lt_wo_ps)
    lt_wo_ps.to_csv(BASE_CAL + srid + CSV,index=False)
    print("file saved")
    # global_df.to_csv(BASE_GLO + srid + CSV)
    break

  pass

'''
cumulatiuve times doine
need to create files
BUT need to add status codes into the laptimes/pitstoptimes
'''