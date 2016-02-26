from chrony import timespans
import pandas as pd

print('')
print('Test merge_overlapping_events #1')
print('=================================')

begs = pd.to_datetime(['2014-09-12 12:00:00','2014-09-12 13:00:00','2014-09-12 14:00:00', '2014-09-12 15:00:00', '2014-09-12 22:00:00','2014-09-12 23:15:00','2014-09-12 23:46:00'])
ends = pd.to_datetime(['2014-09-12 12:30:00','2014-09-12 15:30:00','2014-09-12 15:00:00', '2014-09-12 16:00:00','2014-09-12 23:00:00','2014-09-12 23:16:00','2014-09-12 23:50:00'])

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
print('Test merge_overlapping_events_kind #1')
print('======================================')

begs = pd.date_range('2014-09-12 12:00:00','2014-09-12 20:00:00',freq='h')
ends = pd.date_range('2014-09-12 13:00:01','2014-09-12 21:00:01',freq='h')
cats = []
for i in range(len(begs)):
    if i<len(begs)/2:
        cats.append(1)
    else:
        cats.append(2)

df = pd.DataFrame({'ts_beg':begs,'ts_end':ends,'category':cats})

print('')
print('df=')
print(df)
print('')
print('merge_overlapping_events_kind(df, \'ts_beg\', \'ts_end\', [\'category\'])=')
print(timespans.merge_overlapping_events_kind(df,'ts_beg','ts_end',kind=['category']))

print('')
print('Test merge_overlapping_events_kind #2')
print('======================================')

begs = pd.to_datetime(['2014-09-12 12:00:00','2014-09-12 13:00:00','2014-09-12 14:00:00', '2014-09-12 15:00:00', '2014-09-12 17:00:00'])
ends = pd.to_datetime(['2014-09-12 12:30:00','2014-09-12 15:30:00','2014-09-12 15:00:00', '2014-09-12 17:01:00','2014-09-12 18:00:00'])
cats = [1,1,1,2,2]

df = pd.DataFrame({'ts_beg':begs,'ts_end':ends,'category':cats})

print('')
print('df=')
print(df)
print('')
print('merge_overlapping_events_kind(df, \'ts_beg\', \'ts_end\', [\'category\'])=')
print(timespans.merge_overlapping_events_kind(df,'ts_beg','ts_end',kind=['category']))


print('')
print('Test add_time_between_events #1')
print('======================================')

begs = pd.to_datetime(['2014-09-12 12:00:00','2014-09-12 13:00:00','2014-09-12 14:00:00', '2014-09-12 15:00:00', '2014-09-12 17:00:00'])
ends = pd.to_datetime(['2014-09-12 12:30:00','2014-09-12 15:30:00','2014-09-12 15:00:00', '2014-09-12 17:01:00','2014-09-12 18:00:00'])
cats = [1,1,1,2,2]

df = pd.DataFrame({'ts_beg':begs,'ts_end':ends,'category':cats})
df = timespans.merge_overlapping_events_kind(df,'ts_beg','ts_end',kind=['category'])

print('')
print('df=')
print(df)
print('')
print('add_time_between_events(df, \'ts_beg\', \'ts_end\', [\'category\'])=')
print(timespans.add_time_between_events(df,'ts_beg','ts_end',['category']))


print('')
print('Test add_time_between_events #2')
print('======================================')


begs = pd.to_datetime(['2014-09-12 12:00:00','2014-09-12 13:00:00','2014-09-12 14:00:00', '2014-09-12 15:00:00', '2014-09-12 22:00:00','2014-09-12 23:15:00','2014-09-12 23:46:00'])
ends = pd.to_datetime(['2014-09-12 12:30:00','2014-09-12 15:30:00','2014-09-12 15:00:00', '2014-09-12 16:00:00','2014-09-12 23:00:00','2014-09-12 23:16:00','2014-09-12 23:50:00'])
cats = [1,1,1,1,1,1,1]
subcats = [1,1,1,2,2,2,2]

df = pd.DataFrame({'ts_beg':begs,'ts_end':ends,'category':cats,'subcategory':subcats})
df = timespans.merge_overlapping_events_kind(df,'ts_beg','ts_end',kind=['category','subcategory'])

print('')
print('df=')
print(df)
print('')
print('add_time_between_events(df, \'ts_beg\', \'ts_end\', [\'category\',\'subcategory\'])=')
print(timespans.add_time_between_events(df,'ts_beg','ts_end',['category','subcategory']))




print('')
print('Done.')

