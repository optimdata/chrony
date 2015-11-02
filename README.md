# chrony

Timeseries analysis tools with specific focus on timespans. Built on top of pandas.

## tldr

This library provides helpers for timespans manipulation using pandas objects. Let's consider the following DataFrame `df`.

    In [1]: df
    Out[1]: 
             beg        end
    0 2015-01-01 2015-01-02
    1 2015-01-02 2015-01-03
    2 2015-01-04 2015-01-05

### Chart timespans

    from chrony.charting import plot_events
    plot_events(
        categories=np.array(['a', 'b']),
        xmin=np.array([2, 4], dtype='d'),
        xmax=np.array([6, 8], dtype='d'),
        xlim=(0, 10),
        labels=['RED', 'BLUE']
    )

### Describe the timespan

This following method gives a quick overview of your timespans:

    In [2]: describe_timespan(df['beg'], df['end'])
    Out[2]: 
    beg                           2015-01-01 00:00:00
    count                                           3
    contiguous transitions                          1
    not contiguous transitions                      1
    coverage                                     0.75
    end                           2015-01-05 00:00:00
    dtype: object

### Audit the timespan

The library gives you a `audit_timespan` function which raises an error if:

- beg or end columns have a timezone (due to https://github.com/pydata/pandas/pull/11410)
- Lengths of beg or end columns does not match
- Columns are not sorted
- There is overlap between timespans.

Check out tests for examples.

## Terminology

A **timespan** is a row of a `pandas.DataFrame` which represents a period of time between two fixed points. These are represented using a beg and a end column.


