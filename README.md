
# EVsSimulator
A V2X Simulation Environment for large scale EV charging optimization

## TODO short term

- [ ] Do not implement the Grid model yet -> Implement the G2V/V2G EVs gym environment.

 

## Future Ideas
Here, I will write down abstract ideas about the V2X problem I am trying to solve:
- Use PandaPower to simulate the grid (use it with the power transformer class id characteristics, use the storage class to simulate the chargers fro each node **aggregate many chargers to one storage** per bus)
- Support any kind of  MV or LV network for the PandaPower grid

### Improve Problem Formulation
- [ ] Add the **grid** as a part of the problem formulation
- [ ] Add **j number of ports** per charging station and include related constraints
- [ ] Add the battery behavior model 0-80 fast, 70-100 slow
- [ ] Add battery degradation model (simple -> just include charge cycles, more complex -> include temperature, SOC, etc.)

## Limitations
- Real **time-series** grid data are required for the PandaPower grid simulator to work, for the following parts:
    - Power transformer
    - Loads
    - Generators
    - Renewable energy sources
    - 
 ## URLs
 - PowerFlow Problem formulation: https://invenia.github.io/blog/2020/12/04/pf-intro/
 - PandaPower MV networks: https://pandapower.readthedocs.io/en/v2.1.0/networks/cigre.html
 - PowerFactory API for python: https://thesmartinsights.com/run-digsilent-powerfactory-via-the-python-api-jump-start-to-your-powerfactory-automatization/


# Assumptions
Assumptions regarding the EVsSimulator environment:
- Power that is charged and discharged is tranferred in the:
    1. charger level 
    2. parking lot/ building level
    3. transformer level
    4. grid level (PandaPower)
 
