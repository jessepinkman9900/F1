### DATA
Explain schema and data in csv files in alphabetical order

1. [circuits.csv](../data/base/circuits.csv)

| circuitId | circuitRef | name | location | country | lat | lng | alt | url | kms | turns | miles | 
| :---       | :---        | :---  | :---      | :---     | :--- | :--- | :--- | :--- | :--- | :---   | :---   |
| int 1-73 | reference name | official circuit name | city | country | latitude | longitude | altitude | wikipedia link | length of 1 lap in km | number of turns | length of 1 lap in miles |

2. [constructorresults.csv](../data/base/constructorresults.csv)

| constructorResultsId | raceId | constructorId | points | status | 
| :---       | :---        | :---  | :---      | :---     | 
| int 1-15889 | int 1-1013 | int 1-211 | points won 0-66 (some float values) | (D, NULL, empty) | 

3. [constructors.csv](../data/base/constructors.csv)

| constructorId | constructorRef | name | nationality | url | 
| :---       | :---        | :---  | :---      | :---     | 
| int 1-211 | common name | official name | country of HQ | wikipedia link | 

4. [constructorstandings.csv](../data/base/constructorstandings.csv)

| constructorResultsId | raceId | constructorId | points | position | positionText | wins | 
| :---       | :---        | :---  | :---      | :---     |  :---  | :---      | :---     |
| int 1-27242 | int 1-1013 | int 1-211 | points won 0-765 (some float values) | int 1-22 | (int 1-22) OR (E)| int 0-19| 

5. [drivers.csv](../data/base/drivers.csv)

|driverId|driverRef|number|code|forename|surname|dob|nationality|url|
|---|---|---|---|---|---|---|---|---|
|int 1-848|reference name|driver number|3 letter code name|first name|surname|dob|nationality|wikipedia link|

6. [driverstandings.csv](../data/base/driverstandings.csv)

|driverStandingsId|raceId|driverId|points|position|positionText|wins|
|---|---|---|---|---|---|---|
|int 1-69268|int 1-1013|int 1-848|points won 0-408 (some float values)|int 1-108|int 1-108|int 0-13|

7. [heavyrain.csv](../data/base/heavyrain.csv)

| year | round | 
| --- | --- |
| year | the round(race) that had heavy rain |

8. [laptimes.csv](../data/base/laptimes.csv)

|raceId|driverId|lap|position|time|milliseconds|
|---|---|---|---|---|---|
|int 1-1013| int 1-848| int 1-78 | int 1-24 | min:sec.ms | time in milliseconds|

9. [pitstops.csv](../data/base/pitstops.csv)

|raceId|driverId|stop|lap|time|duration|milliseconds|
|---|---|---|---|---|---|---|
|int 1-1013| int 1-848| int 1-6 | int 1-74 | min:sec.ms | seconds.ms (some in min:sec.ms)|time in milliseconds|

10. [qualifying.csv](../data/base/qualifying.csv)

- no headers

- speculation 

|dk |raceId|driverId|constructorId|dk|dk|time1|time2|time3|
|---|---|---|---|---|---|---|---|---|
|int 1-8037| int 1-1013| int 1-848 | int 1-211 | int 0-99 | int 1-28|time 1|time 2|time 3|

11. [races.csv](../data/base/races.csv)

|raceId|year|round|circuitId|name|date|time|url|positionPointsRace|
|---|---|---|---|---|---|---|---|---|
|int 1-1013|int 1950-2019|int 1-21|int 1-73|name of GP|date|time|wikipedia link|int 5-10|

12. [results.csv](../data/base/results.csv)

resultId|raceId|driverId|constructorId|number|grid|position|positionText|positionOrder|points|laps|time|milliseconds|fastestLap|rank|fastestLapTime|fastestLapSpeed|statusId|
---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|int 1-24282|int 1-1013|int 1-848|int 1-211| (int 0-208) OR (NULL)|int 0-34|(int 1-33) OR (NULL)|(int 1-33) OR (W,R,N,F,D)|int 1-39|int 0-50 (some float values)|int 0-200|min:sec.ms|milliseconds|(int 2-78)OR(NULL)|(int 0-24) OR (NULL)|(min:sec.ms)OR(NULL)|(float) OR (NULL)|int 1-137|

13. [season.csv](../data/base/season.csv)
- no headers (added them)

|year|url|
|---|---|
|year| wikipedia link|

14. [status.csv](../data/base/status.csv)
- no headers (Added them)

|number| meaning|
|--- | ---|
| int 1-137 | string |

15. [wetraces.csv](../data/base/wetraces.csv)

|year|round|
|---|---|
|int 1990-2018 |int 1-20|

16. [winninground.csv](../data/base/winninground.csv)

|year| winningRound|
|---|---|
|int 1991-2018| int 11-21|


#### other

- /base intial data
- /derived all the tables that have been created using the tables from /base