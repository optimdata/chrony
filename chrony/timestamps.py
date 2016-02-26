# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import pandas as pd
import numpy as np

from .exceptions import BadLengthsError, MissingDataError, NotSortedError, IntegrityError, HasTimezoneError




def audit_timestamp(ts, val, talk_to_me=False):
    if ts.empty and val.empty:
        return
    if ts.dt.tz: 
        if talk_to_me:
            print('HasTimezoneError')
        else:
            raise HasTimezoneError
    if len(ts) != len(val):
        if talk_to_me:
            print('BadLengthsError')
        else:
            raise BadLengthsError
    if len((ts-ts.shift())[1:].drop_duplicates())>1:
        print('Bonjour')
    if (ts < ts.shift()).sum():
        if talk_to_me:
            print('NotSortedError')
        else:
            raise NotSortedError
    if val.count()!=len(val):
        if talk_to_me:
            print('MissingDataError')
        else:
            raise MissingDataError


def find_holes(ts, val):
    """
    ts (pandas Series): timestamp indexing the time series
    val (pandas Series): values of the time series
    """
    if len(ts)!=len(val):
        raise BadLengthsError
    t,v = ts.values, val.values
    n = len(t)
    holes = []
    i=0
    while i<n:
        l=0
        vv = v[i]
        while np.isnan(vv):
            l+=1
            vv = v[i+l]
        if l>0: # there is a hole
            holes.append({'ts_beg':t[i],'ts_end':t[i+l-1],'length':l})
            i+=l
        else:
            i+=1
    return holes


def cut_ts(ts, val, min_hole_duration):
    """
    Cuts the time series (ts,val) in h+1 time series where h is the
    number of holes in (ts,val) with duration > min_hole_duration.
    """
    holes = find_holes(ts,val)
    t = ts.values
    v = val.values
    n = len(holes)
    time_series = []
    it1 = 0
    i = 0
    while i<n:
        ts_beg, ts_end, l = holes[i]['ts_beg'], holes[i]['ts_end'], holes[i]['length']
        if l>min_hole_duration:
            it2 = np.where(t==ts_beg)[0][0] - 1
            time_series.append(pd.DataFrame({'ts':t[it1:it2],'val':v[it1:it2]}))
            it1 = np.where(t==ts_end)[0][0] + 1
        i+=1
    return time_series


def describe_timestamp(ts, val):
    if ts.empty and val.empty:
        print('Empty series')
        return
    holes = pd.DataFrame(find_holes(ts, val))
    metrics = (
        ('beg',ts[0]),
        ('time step',ts[1]-ts[0]),
        ('end', ts[len(ts)-1]),
        ('# ts',len(ts)),
        ('missing values',len(ts)-val.count()),
        ('# holes',len(holes)),
        ('min hole size', holes.length.min()),
        ('25% percentile hole size', np.percentile(holes.length.values,25)),
        ('median hole size', np.percentile(holes.length.values,25)),
        ('75% percentile hole size', np.percentile(holes.length.values,25)),
        ('max hole size', holes.length.max())
    )
    retval = pd.Series([m[1] for m in metrics], index=[m[0] for m in metrics])
    print(retval)
    return    


def clean_overlap_timespan(begs, ends):
    return pd.DataFrame({'ts_end': ends, 'ts_end_shifted': begs.shift(-1)}).min(axis=1)


def fill_na_series(series):
    if series.dtype.char == 'O':
        series.fillna('UNDEFINED', inplace=True)
    else:
        series.fillna(-1, inplace=True)


def fill_na_dataframe(df):
    for column in df.columns:
        if column.startswith('beg_') or column.startswith('end_'):
            fill_na_series(df[column])


def to_stamps(df, state_columns, value_columns, beg_col='ts_beg', end_col='ts_end'):
    '''
        Convert an frame representing periods (eg each row has a beg and end) to a frame representing change of periods.
        Example:

        This dataframe:

           dummy     ts_beg     ts_end  value
        0      3 2015-01-01 2015-01-02      1
        1      4 2015-01-02 2015-01-03      2

        is converted to

                  ts  beg_value  end_value
        0 2015-01-01          1        NaN
        1 2015-01-02          2          1
        2 2015-01-03        NaN          2
    '''
    beg_columns = dict(
        [(beg_col, 'ts')] +
        [(col, 'beg_%s' % col) for col in state_columns] +
        [('beg_%s' % col, col) for col in value_columns]
    )
    end_columns = dict(
        [(end_col, 'ts')] +
        [(col, 'end_%s' % col) for col in state_columns] +
        [('end_%s' % col, col) for col in value_columns]
    )
    df1 = pd.DataFrame(df, columns=list(beg_columns.keys()))
    df1.rename(columns=beg_columns, inplace=True)
    df2 = pd.DataFrame(df, columns=list(end_columns.keys()))
    df2.rename(columns=end_columns, inplace=True)
    # return df1, df2
    retval = pd.merge(
        df1,
        df2,
        on=['ts'] + value_columns,
        how='outer'
    )
    retval.sort_values('ts', inplace=True)
    if retval['ts'].duplicated().sum():
        raise IntegrityError
    return retval


def to_spans(df, state_columns, value_columns, beg_col='ts_beg', end_col='ts_end'):
    '''
        Revert method of to_stamps
        Example:

        This dataframe:

                  ts  beg_value  end_value
        0 2015-01-01          1        NaN
        1 2015-01-02          2          1
        2 2015-01-03        NaN          2

        is converted to

               ts_beg     ts_end  value
        0  2015-01-01 2015-01-02      1
        1  2015-01-02 2015-01-03      2
    '''
    beg_columns = dict(
        [('ts', beg_col)] +
        [('beg_%s' % col, col) for col in state_columns] +
        [(col, 'beg_%s' % col) for col in value_columns]
    )
    end_columns = dict(
        [('ts', end_col)] +
        [('end_%s' % col, col) for col in state_columns] +
        [(col, 'end_%s' % col) for col in value_columns]
    )
    df_beg = pd.DataFrame(df.iloc[:-1], columns=beg_columns.keys())
    df_beg.rename(columns=beg_columns, inplace=True)
    df_beg.reset_index(drop=True, inplace=True)
    df_end = pd.DataFrame(df.iloc[1:], columns=end_columns.keys())
    df_end.rename(columns=end_columns, inplace=True)
    df_end.reset_index(drop=True, inplace=True)
    # print(df_beg)
    # print(df_end)
    return pd.DataFrame(dict(list(df_beg.to_dict('series').items()) + list(df_end.to_dict('series').items())))


# def merge_spans(left, right):
    
    # for key in ('beg', 'end'):
    #     spans['ts'] = spans['ts_%s' % key]
    #     spans = pd.merge(stamps, spans, how='outer', on='ts')
    #     spans.set_index('ts', inplace=True)
    #     spans.sort_index(inplace=True)
    #     for column in columns_states:
    #         spans['%s_%s' % (column, key)] = spans.pop(column).interpolate(method='time')
    #         spans['%s_%s' % (column, key)].fillna(method='ffill', inplace=True)
    #         spans['%s_%s' % (column, key)].fillna(method='bfill', inplace=True)
    #     spans.reset_index(inplace=True)
    #     spans.pop('ts')
    #     spans = spans[~pd.isnull(spans['ts_%s' % key])]
    # return spans


def compute_segments(df, columns):
    '''
    '''
    mask = pd.Series([False] * len(df))
    for column in columns:
        mask = mask | (df[column] != df[column].shift(1))
    return mask.astype(int).cumsum()


def merge_overlapping_events(df, beg, end, kind=None):
    '''
    Args:
    - df (pandas dataframe): contains events.
    - beg (str): name of the column containing beginning timestamps.
    - end (str): name of the column containing ending timestamps.
    - kind (str): name of the column describing the kind of events (useful if two kind of events coexist and you do not want to merge events
    of different kinds).
    Output:
    - ddf (pandas dataframe). Dataframe df where overlapping events have been merged
    '''
    if kind is None:
        ddf = df.sort_values(by=beg).reset_index(drop=True)
        begs = ddf[beg].copy()
        ends = ddf[end].copy()
        i=0
        while i <= len(begs)-2:
            j=i+1
            while ends[i]>begs[j]: # one enters the loop iff there is an overlap
                begs[j]=begs[i] # event j actually starts at begs[i]
                ends[i]=max(ends[i],ends[j]) # event i actually ends at least at ends[j]
                if j<len(begs)-1:
                     j+=1
                else:
                    break
            i=j
        # At this point, event i :
        #   - starts at the initial begs[i] which was the correct one
        #   thanks to the initial sort_values 
        #   - ends at ends[j] with j the latest overlapping event after i
        # 
        # We drop all events from i+1 to j
        for l in [beg,end]:
            ddf.pop(l)
        ddf[beg]=begs
        ddf[end]=ends
        ddf = ddf.drop_duplicates(beg, keep='first').reset_index(drop=True)
    else:
        raise ValueError('Case kind is not None not coded yet')
    return ddf


def merge_overlapping_events_kind(df, beg, end, kind=None):
    '''
    Args:
    - df (pandas dataframe): contains events.
    - beg (str): name of the column containing beginning timestamps.
    - end (str): name of the column containing ending timestamps.
    - kind (list of str): name of the column describing the kind of events (useful if two kind of events coexist and you do not want to merge events of different kinds).
    Output:
    - ddf (pandas dataframe). Dataframe df where overlapping events have been merged
    '''
    new_df = pd.DataFrame({beg:[],end:[]})
    for kind, ddf in df.groupby(kind):
        dddf = merge_overlapping_events(ddf, beg, end)
        new_df = new_df.append(dddf, verify_integrity=True, ignore_index=True) 
    new_df = new_df.reset_index(drop=True)
    return new_df


def add_time_between_events(df, beg, end, kind=None):
    '''
    Args:
    - df (pandas dataframe): contains events.
    - beg (str) : name of the column containing beginning timestamps.
    - end (str) : name of the column containing ending timestamps.
    - kind (list of str): list of the columns defining a kind of event (if you want to study separately 
    different kinds of events)
    '''
    new_df = pd.DataFrame({beg:[],end:[]})
    for kind, ddf in df.groupby(kind):
        dddf=ddf.sort_values(by=beg).reset_index(drop=True).copy()

        begs = dddf[beg].values
        ends = dddf[end].values
        
        if (len(begs)>1):
            time_since_previous = [None]
            for i in range(1,len(begs)):
                time_since_previous.append(begs[i]-ends[i-1])
    
            time_to_next = []
            for i in range(0,len(begs)-1):
                time_to_next.append(begs[i+1]-ends[i])
            time_to_next.append(None)

            dddf['time_since_previous']=pd.Series(time_since_previous)
            dddf['time_to_next']=pd.Series(time_to_next)
        else:
            dddf['time_since_previous']=pd.Series([None])
            dddf['time_to_next']=pd.Series([None])
        
        new_df = new_df.append(dddf, verify_integrity=True, ignore_index=True)
        dddf=None
    return new_df

