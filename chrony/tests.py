# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import numpy as np
import pandas as pd
import pytz
import unittest

from .charting import compute_category_index
from .exceptions import BadLengthsError, BegPosteriorToEndError, OverlapError, NotSortedError, HasTimezoneError, IntegrityError
from .timespans import audit_timespan, describe_timespan, to_stamps, to_spans, compute_segments

pd.set_option('display.width', 1000)


class TimespanCase(unittest.TestCase):
    def test_all(self):
        with self.assertRaises(HasTimezoneError):
            audit_timespan(
                pd.date_range('1970-1-1', freq='d', periods=10, tz=pytz.utc).to_series().reset_index()['index'],
                pd.date_range('1970-1-2', freq='d', periods=10, tz=pytz.utc).to_series().reset_index()['index'],
            )
        with self.assertRaises(BadLengthsError):
            audit_timespan(
                pd.date_range('1970-1-1', freq='d', periods=1).to_series(),
                pd.date_range('1970-1-1', freq='d', periods=2).to_series(),
            )
        with self.assertRaises(BegPosteriorToEndError):
            audit_timespan(
                pd.date_range('1970-1-2', freq='d', periods=1).to_series(),
                pd.date_range('1970-1-1', freq='d', periods=1).to_series(),
            )
        with self.assertRaises(OverlapError):
            audit_timespan(
                pd.date_range('1970-1-1', freq='h', periods=2).to_series().reset_index(drop=True),
                pd.date_range('1970-1-2', freq='h', periods=2).to_series().reset_index(drop=True),
            )
        with self.assertRaises(NotSortedError):
            audit_timespan(
                pd.date_range('1970-1-1', freq='d', periods=2).to_series().reset_index(drop=True).sort_values(ascending=False).reset_index(drop=True),
                pd.date_range('1970-1-2', freq='d', periods=2).to_series().reset_index(drop=True).sort_values(ascending=False).reset_index(drop=True),
            )
        begs = pd.date_range('1970-1-1', freq='d', periods=2).to_series().reset_index(drop=True)
        ends = pd.date_range('1970-1-2', freq='d', periods=2).to_series().reset_index(drop=True)
        describe_timespan(begs, ends)
        # self.assertTrue(pd.Series().equals(describe_timespan(begs, ends)))

    def test_merge(self):
        span_state_columns = ['state_%s' % c for c in 'ds']
        span_value_columns = ['%s_value_%s' % (i, c) for c in 'ds' for i in ('beg', 'end')]
        stamp_value_columns = ['value_%s' % c for c in 'ds']
        stamp_state_columns = ['%s_state_%s' % (i, c) for c in 'ds' for i in ('beg', 'end')]
        span_columns = ['ts_beg', 'ts_end'] + span_state_columns + span_value_columns
        stamp_columns = ['ts'] + stamp_state_columns + stamp_value_columns
        df1 = pd.DataFrame({
            # 'ts_beg': pd.to_datetime(['2015-1-1', '2015-1-2']),
            # 'ts_end': pd.to_datetime(['2015-1-2', '2015-1-3']),
            'ts_beg': [datetime.datetime(2015, 1, 1), datetime.datetime(2015, 1, 2)],
            'ts_end': [datetime.datetime(2015, 1, 2), datetime.datetime(2015, 1, 3)],
            'state_d': [1., 2.],
            'state_s': ['1', '2'],
            'beg_value_d': [10., 20.],
            'end_value_d': [20., 30.],
            'beg_value_s': ['10', '20'],
            'end_value_s': ['20', '30'],
        }, columns=span_columns)
        df2 = pd.DataFrame({
            'ts': pd.to_datetime(['2015-1-1', '2015-1-2', '2015-1-3']),
            'beg_state_d': [1., 2., np.NaN],
            'end_state_d': [np.NaN, 1., 2.],
            'beg_state_s': ['1', '2', None],
            'end_state_s': [None, '1', '2'],
            'value_d': [10., 20., 30.],
            'value_s': ['10', '20', '30']
        }, columns=stamp_columns)
        df3 = pd.DataFrame(
            to_stamps(
                df1,
                state_columns=span_state_columns,
                value_columns=stamp_value_columns
            ),
            columns=stamp_columns
        )
        pd.util.testing.assert_frame_equal(df3, df2)
        df4 = pd.DataFrame(
            to_spans(
                df3,
                state_columns=span_state_columns,
                value_columns=stamp_value_columns
            ),
            columns=span_columns
        )
        pd.util.testing.assert_frame_equal(df4, df1)

        with self.assertRaises(IntegrityError):
            df1['beg_value_d'] = [10., 25.]
            df3 = pd.DataFrame(
                to_stamps(
                    df1,
                    state_columns=span_state_columns,
                    value_columns=stamp_value_columns
                ),
                columns=stamp_columns
            )

    def test_compute_segments(self):
        df = pd.DataFrame({
            'a': [0, 1, 1, 2],
            'b': [0, 1, 2, 3]
        })
        pd.util.testing.assert_series_equal(
            compute_segments(df, ['a']),
            pd.Series([1, 2, 2, 3])
        )
        pd.util.testing.assert_series_equal(
            compute_segments(df, ['a', 'b']),
            pd.Series([1, 2, 3, 4])
        )


class ChartingCase(unittest.TestCase):
    def test_all(self):
        self.assertTrue(compute_category_index([]) == {})
        self.assertTrue(compute_category_index(['a']) == {'a': 1})
        self.assertTrue(compute_category_index(['b', 'a', 'b']) == {'a': 1, 'b': 2})
