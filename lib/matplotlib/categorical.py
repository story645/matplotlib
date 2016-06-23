"""
catch all for categorical functions
"""
from collections import OrderedDict

import six
import numpy as np

import matplotlib.units as units
import matplotlib.ticker as ticker
import matplotlib.dates as dates


def register():
    """conversation with pandas dev on what specifically gets
    registered"""
    if six.PY3:
        units.registry[str] = CategoricalConverter()
    elif six.PY2:
        units.registry[basestring] = CategoricalConverter()


class CategoricalConverter(units.ConversionInterface):

    @staticmethod
    def convert(value, unit, axis):
        if isinstance(value, six.string_types):
            return 0
        
        vals = np.asarray(value, dtype='str')
        for label, loc  in axis.unit_data.items():
            vals[vals == label] = loc

        return vals.astype('int')

    @staticmethod
    def axisinfo(unit, axis):
        seq, locs = zip(*axis.unit_data.items())
        majloc = CategoricalFormatter(locs)
        majfmt = CategoricalLocator(seq)
        return units.AxisInfo(majloc=majloc, majfmt=majfmt, label=None)

    @staticmethod
    def default_units(data, axis):
        """map is built here because the conversion call stack is:
        default_units->axis info->convert
        """

        # factor this stuff out so I can test it
        vals = np.asarray(data, dtype='str')
        uniq = np.unique(vals)

        # pandas factorize convention
        if 'nan' in uniq:
            vals[vals == 'nan'] = -1
            uniq = uniq[uniq != 'nan']

        for inf in ['-inf', 'inf']:
            if inf in uniq:
                vals[vals == inf] = uniq.shape[0] - 1
                uniq = uniq[uniq != inf]

        index = list(range(uniq.shape[0]))
        axis.unit_data = OrderedDict(zip(uniq, index))

        return None


class CategoricalLocator(ticker.FixedLocator):
    def __init__(self, locs):
        super(CategoricalLocator, self).__init__(locs)


class CategoricalFormatter(ticker.FixedFormatter):
    def __init__(self, seq):
        super(CategoricalFormatter, self).__init__(seq)
