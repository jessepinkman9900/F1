import pandas as pd 
from tqdm import tqdm


def fill_df(race_laptimes_df, col_df):
  driverIds = list(set(race_laptimes_df['driverId']))
  laps = list(set(race_laptimes_df['lap']))
  num_laps = len(laps)
  for x in range(len(driverIds)):
    driverId = driverIds[x]
    tmp = race_laptimes_df[race_laptimes_df['driverId']==driverId]
    time = list(tmp.loc[:,'milliseconds'])
    # filling with inf to ensure same len for each row in df
    if len(time)!= num_laps:
      for _ in range(num_laps-len(time)):
        time.append('inf')

    row = [driverId]+time
    col_df.loc[x] = row
 
  return col_df

def create_finalDf(race_laptimes_df):
  total_laps = list(set(race_laptimes_df['lap']))
  total_laps = ["lap_"+str(x) for x in total_laps]
  columns = ['driverId'] + total_laps
  colm_df = pd.DataFrame(columns=columns)
  return fill_df(race_laptimes_df,colm_df)


if __name__ == "__main__":
  # create tables laptimes_race_<race_id>.csv
  laptimes_df = pd.read_csv("./data/base/laptimes.csv")
  raceIds = set(laptimes_df['raceId'])
  for raceId in tqdm(raceIds):
    race_laptimes_df = laptimes_df[(laptimes_df['raceId'] == raceId)]
    final_df = create_finalDf(race_laptimes_df)
    final_df.to_csv('./data/derived/overtaking/laptimes/laptimes_race_'+str(raceId)+'.csv',index=False)
