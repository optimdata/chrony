from chrony import timestamps
import numpy as np
import pandas as pd
import random

print('Test for library timestamps')
print('============================')

ts = pd.date_range(start='2015-09-01',end='2015-09-30',freq='D')
y = list(map(lambda x:np.sin(2*np.pi*x/len(ts)),range(len(ts))))
y = [yy+0.1*random.random() for yy in y] # add noise
for i in [4,5,6,10,20,21]:
    y[i] = np.nan # add holes

df=pd.DataFrame({'ts':ts,'val':y})
print('df=',df)

print('')
print('audit_timestamp(df.ts, df.val,talk_to_me=True):')
timestamps.audit_timestamp(df.ts, df.val,talk_to_me=True)

print('')
print('describe_timestamp(df.ts, df.val):')
timestamps.describe_timestamp(df.ts, df.val)


print('')
print('Done.')

