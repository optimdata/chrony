# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import pandas as pd


def compute_category_index(categories):
    return {category: index + 1 for index, category in enumerate(sorted(set(categories)))}


def weighted_interpolate(serie, weights):
    sb = serie.fillna(method='ffill')
    se = serie.fillna(method='bfill')
    cw = weights.cumsum()
    w2 = pd.Series(None, index=serie.index)
    w2[~np.isnan(serie)] = cw[~np.isnan(serie)]
    wb = w2.fillna(method='ffill')
    we = w2.fillna(method='bfill')
    cw = (cw - wb) / (we - wb)
    r = sb + cw * (se - sb)
    r.update(serie)
    return r
