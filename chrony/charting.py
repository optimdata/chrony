# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import matplotlib.pyplot as plt
import numpy as np
from .core import compute_category_index


def plot_events(categories, xmin, xmax, labels=None, xlim=None, linewidth=10):
    index = compute_category_index(categories)
    xlim = xlim or (min(xmin), max(xmax))
    xmin_normalized = np.array([(x - xlim[0]) / (xlim[1] - xlim[0]) for x in xmin])
    xmax_normalized = np.array([(x - xlim[0]) / (xlim[1] - xlim[0]) for x in xmax])

    plt.figure(figsize=(20, 5))
    plt.xlim(xlim)
    plt.ylim(0, len(index) + 1)
    plt.xticks(fontsize=18)
    plt.yticks(list(index.values()), list(index.keys()), fontsize=18)
    for i in range(len(categories)):
        if labels is not None:
            plt.text(
                x=xmin[i],
                y=index[categories[i]] + .1 if i % 2 else index[categories[i]] - .1,
                s=labels[i],
                horizontalalignment='left',
                verticalalignment='bottom' if i % 2 else 'top',
                color='k',
                size='x-large',
                weight='bold'
            )
        plt.axhline(
            linewidth=linewidth,
            y=index[categories[i]],
            xmin=xmin_normalized[i],
            xmax=xmax_normalized[i],
            color='b' if i % 2 else 'r',
            label='label'
        )
