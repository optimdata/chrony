# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import matplotlib as plt
import numpy as np


def compute_category_index(categories):
    return {category: index + 1 for index, category in enumerate(sorted(set(categories)))}


def plot_events(categories, xmin, xmax, labels=None, xlim=None, linewidth=10):
    index = compute_category_index(categories)
    xlim = xlim or (min(xmin), max(xmax))
    xmin_normalized = np.array([(x - xlim[0]) / (xlim[1] - xlim[0]) for x in xmin])
    xmax_normalized = np.array([(x - xlim[0]) / (xlim[1] - xlim[0]) for x in xmax])

    plt.figure(figsize=(20, 5))
    plt.xlim(xlim)
    plt.ylim(0, len(index) + 1)
    plt.yticks(index.values(), index.keys())
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
