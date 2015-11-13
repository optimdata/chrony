# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import pandas as pd

from .exceptions import BadLengthsError, BegPosteriorToEndError, OverlapError, NotSortedError, IntegrityError, HasTimezoneError


def audit_timespan(begs, ends):
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


def describe_timespan(begs, ends):
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
