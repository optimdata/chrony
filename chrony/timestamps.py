# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import pandas as pd
import numpy as np

from .exceptions import BadLengthsError, MissingDataError, NotSortedError, IntegrityError, HasTimezoneError, TimeStepError

def audit(ts, val, talk_to_me=False):
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
        if talk_to_me:
            print('TimeStepError')
        else:
            raise TimeStepError
    if (ts < ts.shift()).sum():
        if talk_to_me:
            print('NotSortedError')
        else:
            raise NotSortedError
    if val.count()==0:
        if talk_to_me:
            print('MissingDataError')
        else:
            raise MissingDataError


def find_holes(ts, data):
    """
    ts (pandas Series): timestamp indexing the time series
    data (pandas Series): values of the time series
    """
    audit(ts,data)
    if len(ts)!=len(data):
        raise BadLengthsError
    if data.count()==0:
        raise ValueError('TimeSeries with only missing data')
    t,d = ts.values, data.values
    n = len(t)
    holes = []
    i=0
    while i<n:
        l=0
        dd = d[i]
        while np.isnan(dd) and i+l<n-1:
            l+=1
            dd = d[i+l]
        if l>0: # there is a hole
            holes.append({'ts_beg':t[i],'ts_end':t[i+l-1],'length':l,'i_beg':i,'i_end':i+l-1})
            i+=l
        else:
            i+=1
    return pd.DataFrame(holes)

def trim(ts, val):
    """

    Returns a time series (ts, val) where the missing 
    data at the beginning and end of the series have been 
    trimmed out.
    """
    i=0
    while np.isnan(val[i]):
        i+=1
    j=len(val)-1
    while np.isnan(val[j]):
        j-=1
    return pd.DataFrame({'ts':ts[i:j+1],'data':val[i:j+1]})


def cut(ts, data, min_hole_duration):
    """
    Cuts the time series (ts, data) in h+1 time series where h is the
    number of holes in (ts,data) with duration > min_hole_duration.
    """
    df = trim(ts,data)
    holes = find_holes(df.ts, df.data)
    holes = holes[holes.length>min_hole_duration]
    beg, end = holes.i_beg, holes.i_end
    t, d, n = df.ts.values, df.data.values, len(holes)
    # add first cut
    i_beg = 0
    i_end = beg[0]
    time_series = [pd.DataFrame({'ts':t[i_beg:i_end],'data':d[i_beg:i_end]})] 
    # add all intermediate cuts
    for j in range(n-1):
        i_beg = end[j]+1
        i_end = beg[j+1] 
        time_series.append(pd.DataFrame({'ts':t[i_beg:i_end],'data':d[i_beg:i_end]})) 
    # add last cut (if different from first)
    if n>0:
        i_beg=end[n-1]+1
        i_end=len(d)
        time_series.append(pd.DataFrame({'ts':t[i_beg:i_end],'data':d[i_beg:i_end]})) 
    return time_series


def cut_ts_old(ts, val, min_hole_duration):
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


def describe(ts, val):
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
        ('# holes',len(holes))
    )
    if len(holes)>0:
        metrics+=(
        ('min hole size', holes.length.min()),
        ('1% percentile hole size', np.percentile(holes.length.values,1)),
        ('10% percentile hole size', np.percentile(holes.length.values,10)),
        ('25% percentile hole size', np.percentile(holes.length.values,25)),
        ('median hole size', np.percentile(holes.length.values,50)),
        ('75% percentile hole size', np.percentile(holes.length.values,75)),
        ('90% percentile hole size', np.percentile(holes.length.values,90)),
        ('99% percentile hole size', np.percentile(holes.length.values,99)),
        ('max hole size', holes.length.max())
        )
    retval = pd.Series([m[1] for m in metrics], index=[m[0] for m in metrics])
    print(retval)
    return    

def fill_ts(df, time_step):
    """
    Fills the holes where there is no value of ts in the time series (ts, val)
    by adding a line (ts, np.nan) wherever needs be given the theoretical
    time step time_step. 
    df : pandas Series containing one column 'ts'
    time_step : pandas DataFrame
    """
    ts = pd.date_range(start=df.ts.values[0],end=df.ts.values[-1],freq=time_step)
    return df.merge(pd.DataFrame({'ts':ts}),on='ts',how='outer').sort_values(by='ts')
    

def fill_data(ts, val, max_hole_duration, method='interpolate'):
    """
    Fill the holes of (ts, val) that have a duration <= max_hole_duration
    using linear interpolation.
    """
    holes = find_holes(ts,val)
    if len(holes)==0:
        return pd.DataFrame({'ts':ts,'val':val})
    else:
        newval = val.values
        for ind, h in holes.iterrows():
            length, ts_beg, ts_end = h['length'],h['ts_beg'],h['ts_end']
            if length<=max_hole_duration:
                i_beg = ts[ts==ts_beg].index[0]-1
                i_end = ts[ts==ts_end].index[0]+1
                if i_beg==-1 and i_end==len(val):
                    raise ValueError('Empty Time Series!')
                elif i_beg==-1:
                    for i in range(0,i_end):
                        newval[i] = val[i_end]
                elif i_end==len(val):
                    for i in range(i_beg+1,i_end):
                        newval[i] = val[i_beg]
                else:
                    for i in range(i_beg+1,i_end):
                        newval[i] = val[i_beg] + (i-i_beg)/(i_end-i_beg)*(val[i_end] - val[i_beg])
        return pd.DataFrame({'ts':ts,'data':newval})
    

