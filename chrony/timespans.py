# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import pandas as pd

from .exceptions import BadLengthsError, BegPosteriorToEndError, OverlapError, NotSortedError, IntegrityError, HasTimezoneError


def audit_timespan(begs, ends):
    if begs.empty and ends.empty:
        return
    if begs.dt.tz or ends.dt.tz:
        raise HasTimezoneError
    if len(begs) != len(ends):
        raise BadLengthsError
    for beg, end in zip(begs, ends):
        if beg > end:
            raise BegPosteriorToEndError
    if (begs < begs.shift()).sum():
        raise NotSortedError
    if (ends.shift() > begs)[1:].sum():
        raise OverlapError


def audit_timespan_print(begs, ends):
    if begs.dt.tz or ends.dt.tz:
        print('')
        print('TimeZoneError')
    if len(begs) != len(ends):
        print('')
        print('TimeZoneError')
    print('')
    for beg, end in zip(begs, ends):
        if beg > end:
            print('beg=', beg, ' posterior to end=', end)
    print('')
    for i in range(len(begs) - 1):
        if begs[i + 1] < begs[i]:
            print('Events are not sorted')
        if ends[i] > begs[i + 1]:
            print('At row %s end %s is posterior to %s by %s' % (i, ends[i], begs[i + 1], ends[i] - begs[i + 1]))


def describe_timespan(begs, ends):
    if begs.empty and ends.empty:
        print('Empty series')
        return
    contiguous_transitions = (begs == ends.shift()).sum()
    coverage = (ends - begs).sum().total_seconds() / (ends[len(ends) - 1] - begs[0]).total_seconds()
    metrics = (
        ('beg', begs[0]),
        ('count', len(begs)),
        ('contiguous transitions', contiguous_transitions),
        ('not contiguous transitions', len(begs) - contiguous_transitions - 1),
        ('coverage', coverage),
        ('end', ends[len(ends) - 1])
    )
    retval = pd.Series([m[1] for m in metrics], index=[m[0] for m in metrics])
    return retval


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
        ddf = df.sort_values(by=beg)
        begs = ddf[beg]
        ends = ddf[end] 
        for i in range(len(begs)-1):
            j=i+1
            while ends[i]>begs[j]: # one enters the loop iff there is an overlap
                begs[j]=begs[i] # event j actually starts at begs[i]
                ends[i]=max(ends[i],ends[j]) # event i actually ends at least at ends[j]
                if j<len(begs)-1:
                     j+=1
                else:
                    break
        # At this point, event i :
        #   - starts at the initial begs[i] which was the correct one
        #   thanks to the initial sort_values 
        #   - ends at ends[j] with j the latest overlapping event after i
        # 
        # We drop all events from i+1 to j
        ddf = ddf.drop_duplicates(beg, keep='first').reset_index(drop=True)
    else:
        raise ValueError('Case kind is not None not coded yet')
    return ddf


