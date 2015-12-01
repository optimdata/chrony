from chrony import timespans
import pandas as pd

print('')
print('Test merge_overlapping_events #1')
print('=================================')

begs = pd.to_datetime(['2014-09-12 12:00:00','2014-09-12 13:00:00','2014-09-12 14:00:00', '2014-09-12 15:00:00'])
ends = pd.to_datetime(['2014-09-12 12:30:00','2014-09-12 15:30:00','2014-09-12 14:00:00', '2014-09-12 15:00:00'])

df = pd.DataFrame({'ts_beg':begs,'ts_end':ends})

print('')
print('df=')
print(df)
print('')
print('merge_overlapping_events(df,ts_beg,ts_end)=')
print(timespans.merge_overlapping_events(df,'ts_beg','ts_end'))

print('')
print('Test merge_overlapping_events #2')
print('=================================')


begs = pd.date_range('2014-09-12 12:00:00','2014-09-12 20:00:00',freq='h')
ends = pd.date_range('2014-09-12 13:00:01','2014-09-12 21:00:01',freq='h')

df = pd.DataFrame({'ts_beg':begs,'ts_end':ends})

print('')
print('df=')
print(df)
print('')
print('merge_overlapping_events(df, ts_beg, ts_end)=')
print(timespans.merge_overlapping_events(df,'ts_beg','ts_end'))


print('')
print('Done.')
