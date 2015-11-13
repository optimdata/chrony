# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals


def compute_category_index(categories):
    return {category: index + 1 for index, category in enumerate(sorted(set(categories)))}
