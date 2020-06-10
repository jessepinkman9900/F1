### IDEA
---
- laptimes (laptimes.py)
  - create a table for each race
    - for each lap(x-axis) 
      - for each driver (y-axis)
        - add the lap timing, milliseconds will be better and easy to add as well(data in a 2d matrix)

- pitstops (pitstops.py)
  - create a table for each race 
    - for each lap(x-axis)
      - for each driver(y-axis)
        - add 0, pitstop time (or other codes using __status.csv__ to indicate other things)

- steps
  1. for 1 race, create table using __laptimes.csv__
  2. create pitstops table for 1 race using __pitstops.csv__ and __status.csv__
  3. merge the 2 tables above to get a global timing 
  4. use __results.csv__ to verify 
  5. use the global table and pitstops to figure out overtakes

### NOTES
---
- laptimes
  - create files /laptimes/laptimes_raceId.csv for each race, 
  - similarly /pitstops/pitstops_raceId.csv for each race