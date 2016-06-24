"""
catch all for categorical functions
"""
from collections import OrderedDict

import six
import numpy as np


import matplotlib.units as units
import matplotlib.ticker as ticker
import matplotlib.transforms as mtransforms


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
        vals = np.asarray(value, dtype = 'str') 
         
        for label, loc  in axis.unit_data:
            vals[vals == label] = loc

        return vals.astype('float')

    @staticmethod
    def axisinfo(unit, axis):
        seq, locs = zip(*axis.unit_data)
        majloc = CategoricalLocator(locs)
        majfmt = CategoricalFormatter(seq)
        return units.AxisInfo(majloc=majloc, majfmt=majfmt)

    @staticmethod
    def default_units(data, axis):
        # the conversion call stack is: 
        # default_units->axis_info->convert
        if 'unit_data' not in axis.__dict__:
            axis.unit_data = map_categories(data) 
        return None

   
def map_categories(data):
    """Create mapping between unique categorical
    values and numerical identifier"""
    vals = np.asarray(data, dtype='str')
    uniq = np.unique(vals)
    
    # pandas factorize convention
    dmap = []
    if 'nan' in uniq:
        vals[vals == 'nan'] = -1
        uniq = uniq[uniq != 'nan']
        dmap.append(('nan', - 1))
        
    inf_map = []    
    for inf in ['inf','-inf']:
        if inf in uniq:
            vals[vals == inf] = uniq.shape[0] - 1
            uniq = uniq[uniq != inf]
            inf_map.append((inf, uniq.shape[0]))
        
    # categorical value map 
    category_map = zip(uniq, list(range(uniq.shape[0])))
        
    dmap.extend(category_map)
    dmap.extend(inf_map[::-1])
        
    return dmap
    
    
class CategoricalLocator(ticker.FixedLocator):
    def __init__(self, locs):
        super(CategoricalLocator, self).__init__(locs, None)    
        

class CategoricalFormatter(ticker.FixedFormatter):
    def __init__(self, seq):
        super(CategoricalFormatter, self).__init__(seq)
