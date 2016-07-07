"""
catch all for categorical functions
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six

import numpy as np

import matplotlib.units as units
import matplotlib.ticker as ticker


class StrCategoryConverter(units.ConversionInterface):
    @staticmethod
    def convert(value, unit, axis):
        """Uses axis.unit_data map to encode
        data as floats
        """
        vmap = dict(axis.unit_data)

        if isinstance(value, six.string_types):
            return vmap[value]

        #will likely be replaced by cbook call
        vals = np.asarray(value, dtype='unicode')
        for lab, loc in axis.unit_data:
            vals[vals == lab] = loc

        return vals.astype('float')

    @staticmethod
    def axisinfo(unit, axis):
        seq, locs = zip(*axis.unit_data)
        majloc = StrCategoryLocator(locs)
        majfmt = StrCategoryFormatter(seq)
        return units.AxisInfo(majloc=majloc, majfmt=majfmt)

    @staticmethod
    def default_units(data, axis):
        # the conversion call stack is:
        # default_units->axis_info->convert
        axis.unit_data = map_categories(data, axis.unit_data)
        return None


def map_categories(data, old_map=None):
    """Create mapping between unique categorical
    values and numerical identifier.

    Paramters
    ---------
    data: iterable
        sequence of values
    old_map: list of tuple, optional
        if not `None`, than old_mapping will be updated with new values and
        previous mappings will remain unchanged)
    sort: bool, optional
        sort keys by ASCII value

    Returns
    -------
    list of tuple
        [(label, ticklocation),...]

    """

    # code typical missing data in the negative range because
    # everything else will always have positive encoding
    # question able if it even makes sense
    spdict = {'nan': -1.0, 'inf': -2.0, '-inf': -3.0}

    # will update this post cbook/dict support
    strdata = np.array(data, dtype='unicode')
    uniq = np.unique(strdata)

    if old_map:
        olabs, okeys = zip(*old_map)
        svalue = max(okeys) + 1
    else:
        old_map, olabs, okeys = [], [], []
        svalue = 0

    category_map = old_map[:]

    new_labs = np.setdiff1d(uniq, olabs)
    missing = np.intersect1d(new_labs, list(spdict.keys()))

    category_map.extend([(m, spdict[m]) for m in missing])
    new_labs = np.setdiff1d(new_labs, missing)

    new_locs = np.arange(svalue, svalue + len(new_labs), dtype='float')
    category_map.extend(list(zip(new_labs, new_locs)))
    return category_map


class StrCategoryLocator(ticker.FixedLocator):
    def __init__(self, locs):
        super(StrCategoryLocator, self).__init__(locs, None)


class StrCategoryFormatter(ticker.FixedFormatter):
    def __init__(self, seq):
        super(StrCategoryFormatter, self).__init__(seq)

# Connects the convertor to matplotlib
units.registry[str] = StrCategoryConverter()
units.registry[bytes] = StrCategoryConverter()
units.registry[six.text_type] = StrCategoryConverter()
