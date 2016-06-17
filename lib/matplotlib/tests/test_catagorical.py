"""This will be factored out into different functions (and possibly libraries) 
but I wanted to start with a catch all place for simplicity's sake

#testing implemenation of native (registered) support for pandas 
catagorical dataframe objects 
"""

import nose.tools
from nose.plugins.skip import SkipTest

import numpy as np

from matplotlib.testing.decorators import knownfailureif

import importlib.util
spec = importlib.util.spec_from_file_location("matplotlib.categorical", "../categorical.py")
cat = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cat)



def checkdep_pandas():
    return importlib.util.find_spec("pandas") is not None

@knownfailureif(checkdep_pandas())
def test_factorize():
    index, labels = cat.factorize([1,1,2,2,1,1,4,5,6])
    np.testing.assert_equal(index, np.array([0, 0, 1, 1, 0, 0, 2, 3, 4]))
    np.testing.assert_equal(labels, np.array([1, 2, 4, 5, 6]))

@SkipTest
def test_CategoricalLocator():
    loc = cat.CategoricalLocator()
    

@SkipTest
def test_CategoricalFormatter():
    class FakeAxis(object):
        """Allow Formatter to be called without having a "full" plot set up."""
        def __init__(self, vmin=1, vmax=10):
            self.vmin = vmin
            self.vmax = vmax

        def get_view_interval(self):
            return self.vmin, self.vmax
    
    formatter = cat.CategoricalFormatter()
    formatter.axis = FakeAxis()
