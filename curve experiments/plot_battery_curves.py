#here we will plot the data


import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np
import pylab as pl
import matplotlib.dates as mdates

df_dis = pd.read_csv('dis_honda_3.csv', sep=',')

#plot the current
df_dis["current_setpoint"] = df_dis["AC_Power_set_ID2"]*1000 / df_dis["Output_Voltage_ID2"]

# -10 *\
    #  1000 / 394  # df[f"Output_Voltage_ID{port}"]
print(df_dis.columns)
columns_to_plot_dis = ["Output_Current_ID2",
                    #    "current_setpoint",      
                    "AC_Power_set_ID2", 
                    "Output_Voltage_ID2",                
                       'Capacity_EV_ID2',
                       'SoC_ID2',
                       ]

columns_to_plot_dis = ["SoC_ID2", "Linear Model"]
df_dis['Linear Model'] =  0
df_dis['Linear Model'].at[0] = df_dis['SoC_ID2'].iloc[0]

df_dis.epoch = pd.to_datetime(df_dis.epoch, unit="ms")
print(df_dis.epoch)
df_dis.reset_index(inplace=True)
timestep = df_dis.epoch.iloc[1] - df_dis.epoch.iloc[0]
#turn timestep into minutes
timestep = timestep.total_seconds()/60
print(f'timestep: {timestep} minutes')

for [i, row] in df_dis.iterrows():
    if i > 0:
        df_dis['Linear Model'].at[i] = df_dis['Linear Model'].iloc[i-1] + \
            ((df_dis['current_setpoint'].iloc[i]*df_dis['Output_Voltage_ID2'].iloc[i]/1000 * timestep/60) / 28) * 100


# df_dis.plot(x="epoch", y=columns_to_plot_dis, subplots=False, figsize=(10, 10))
# plt.show()

plt.figure(figsize=(10, 7))
# plt.style.use('seaborn-darkgrid')
# plt.rcParams.update({'font.size': 16})
plt.rcParams['font.family'] = ['serif']

plt.plot(df_dis.epoch.iloc[:-10], df_dis[columns_to_plot_dis].iloc[:-10], linewidth=2.5)


#add xtixks, yticks, grid, legend, title, and labels, and increase font size
plt.xticks(fontsize=28, rotation=45)
#change xtick labels to show only hours and minutes
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

plt.yticks(fontsize=28)
# plt.legend(loc='center left', fontsize=28)
#write legend text
plt.legend(['Actual SoC', 'Linear Model'], fontsize=28, loc='center left')


# plt.title('Mitsubishi Outlander PHEV Charging Curve', fontsize=34)
plt.xlabel('Time', fontsize=32)
plt.ylabel('State of Charge (%)', fontsize=32)
# plt.grid(True, which='minor', axis='both')
plt.xlim([df_dis.epoch.iloc[500], df_dis.epoch.iloc[-500]])
plt.grid(True, which='major', axis='both')
ax = plt.gca()
ax2 = ax.twinx()
ax2.plot(df_dis.epoch.iloc[:-10], df_dis['current_setpoint'].iloc[:-10], linewidth=2.5, color='lightcoral',label='Setpoint')
ax2.plot(df_dis.epoch.iloc[:-10], df_dis['Output_Current_ID2'].iloc[:-10], linewidth=2, color='red', linestyle='--',label='Actual')


plt.ylabel('Current (A)', fontsize=38,color='lightcoral')    
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
plt.yticks(np.arange(-30, 31, 5)
    ,fontsize=28,color='lightcoral')
plt.xlim([df_dis.epoch.iloc[500], df_dis.epoch.iloc[-500]])
#turn off grid
ax2.grid(False)
plt.legend(loc='center right', fontsize=28)
#move legend over the grid lines




plt.tight_layout()  
plt.show()