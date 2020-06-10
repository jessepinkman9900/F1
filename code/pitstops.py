import pandas as pd 
from tqdm import tqdm


def fill_df(race_laptimes_df,pitstops_df, col_df):
  ''' adds rows into the empty datafame 'col_df',
  each row: [driverid, laptime for each lap]
  '''
  driverIds = list(set(race_laptimes_df['driverId']))
  laps = list(set(race_laptimes_df['lap']))
  num_laps = len(laps)
  for x in range(len(driverIds)):    
    '''using indexes instead of 'driverId in driverIds' so that it'll 
    be easy to add rows into the df 
    '''         
    driverId = driverIds[x]
    ''' have a time array with all 0 and then 
    time[x]=t where x is a lap where pitstop occours 
    and t is duration in milliseconds'''
    time = [0 for _ in range(num_laps)]
    
    # all pitstop times for a driver in this race
    tmp_pitstops = pitstops_df[pitstops_df['driverId']==driverId] 
    pit_time = tmp_pitstops.loc[:,['lap','milliseconds']]  

    # filling laps where pitstops occour
    for _, r in pit_time.iterrows(): 
      lap_num, stop_time = int(r['lap']),int(r['milliseconds'])
      time[lap_num] = stop_time

    row = [driverId]+time   # final list to add into df
    col_df.loc[x] = row
 
  return col_df

def create_finalDf(race_laptimes_df,pitstops_df):
  ''' create an empty df with just column names, 
  and then call fill_df()
  '''
  total_laps = list(set(race_laptimes_df['lap']))
  total_laps = ["lap_"+str(x) for x in total_laps]  # ['lap_1',...,'lap_n']
  columns = ['driverId'] + total_laps               # ['driverId','lap_1',...,'lap_n']
  colm_df = pd.DataFrame(columns=columns)           # df with just column names
  return fill_df(race_laptimes_df,pitstops_df,colm_df)


if __name__ == "__main__":
  ''' create tables laptimes_race_<race_id>.csv '''
  laptimes_df = pd.read_csv("./data/base/laptimes.csv")
  pitstops_df = pd.read_csv("./data/base/pitstops.csv")
  raceIds = set(laptimes_df['raceId'])
  for raceId in tqdm(raceIds):
    race_laptimes_df = laptimes_df[(laptimes_df['raceId'] == raceId)]
    race_pitstops_df = pitstops_df[(pitstops_df['raceId'] == raceId)]
    ''' for each race create a df '''
    final_df = create_finalDf(race_laptimes_df,race_pitstops_df)
    final_df.to_csv('./data/derived/overtaking/pitstops/pitstops_race_'+str(raceId)+'.csv',index=False)
