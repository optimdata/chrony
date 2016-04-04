from chrony import timestamps
import numpy as np
import pandas as pd
import random
#import matplotlib.pyplot as plt

print('Test for library timestamps')
print('============================')

ts = pd.date_range(start='2015-09-01',end='2015-09-30',freq='D')
y = list(map(lambda x:np.sin(4*np.pi*x/len(ts)),range(len(ts))))
y = [yy+0.5*random.random() for yy in y] # add noise
for i in [4,5,6,10,20,21,-1,-2,-3]:
    y[i] = np.nan # add holes

df=pd.DataFrame({'data':y}, index=ts)
print('df=')
print(df)
df_initial = df

#fig, ax = plt.subplots(figsize=(10,5))
#ax.plot(df.ts,df.data,'-o',lw=2)
#ax.set_ylim([-1.5,1.5])
#ax.set_xlim([df.ts.values[0],df.ts.values[-1]])
#ax.set_xlabel('ts',fontsize=20)
#ax.set_ylabel('data',fontsize=20)
#for t in ax.get_xticklabels():
#    t.set_fontsize(16)
#for t in ax.get_yticklabels():
#    t.set_fontsize(16)
#fig.autofmt_xdate()
##fig.savefig('images/plot_fake_timeseries.svg',bbox_inches='tight', pad_inches=0.5)


print('')
print('find_holes(df)')
print(timestamps.find_holes(df))

print('')
print('timestamps.audit(df,talk_to_me=True):')
timestamps.audit(df,talk_to_me=True)

print('')
print('timestamps.describe(df):')
timestamps.describe(df)

print('')
print('timestamps.trim(df):')
df=timestamps.trim(df)
print(df)

print('')
print('timestamps.fill_data(df,max_hole_duration=2):')
df = timestamps.fill_data(df, max_hole_duration=2)
print(df)

#fig, ax = plt.subplots(figsize=(10,5))
#ax.plot(df.ts,df.data,'r--o',lw=2,label='Filled')
#ax.plot(df_initial.ts,df_initial.data,'-o',lw=2,label='Initial')
#ax.set_ylim([-1.5,1.5])
#ax.set_xlabel('ts',fontsize=20)
#ax.set_ylabel('data',fontsize=20)
#ax.legend()
#for t in ax.get_xticklabels():
#    t.set_fontsize(16)
#for t in ax.get_yticklabels():
#    t.set_fontsize(16)
#fig.autofmt_xdate()
##fig.savefig('images/plot_fake_timeseries_aftershave.svg',bbox_inches='tight', pad_inches=0.5)


print('')
print('timestamps.describe(df):')
print(timestamps.describe(df))

print('')
print('time_series = timestamps.cut(df,min_hole_duration=2):')
time_series=timestamps.cut(df, min_hole_duration=2)
print(time_series)

j=0
for df in time_series:
    j+=1
#    fig, ax = plt.subplots(figsize=(10,5))
#    ax.plot(df.ts,df.data,'-o',lw=2)
#    ax.set_xlabel('ts',fontsize=20)
#    ax.set_ylabel('data',fontsize=20)
#    ax.legend()
#    ax.set_xlim([df_initial.ts.values[0],df_initial.ts.values[-1]])
#    ax.set_ylim([-1.5,1.5])
#    for t in ax.get_xticklabels():
#        t.set_fontsize(16)
#    for t in ax.get_yticklabels():
#        t.set_fontsize(16)
#    fig.autofmt_xdate()
#   # fig.savefig('images/plot_fake_timeseries_cut'+str(j)+'.svg',bbox_inches='tight', pad_inches=0.5)

print('')
print('for df in time_series:')
print('    timestamps.cut_fixed_size(df.ts,df.data,size=6, overlap=2)')
for df in time_series:
    print(timestamps.cut_fixed_size(df,size=6, overlap=3))

print('')
print('Done.')
