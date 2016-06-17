"""
catch all for categorical functions before they get farmed out to 
ticker & Pandas.
"""

import numpy as np

#factorization of pandas factorize:
#https://github.com/pydata/pandas/blob/master/pandas/core/algorithms.py#L145

def factorize(values, sort=False, order=None, na_sentinel=-1, size_hint=None):
    """
    Encode input values as an enumerated type or categorical variable
    Parameters
    ----------
    values : ndarray (1-d)
        Sequence
    sort : boolean, default False
        Sort by values
    na_sentinel : int, default -1
        Value to mark "not found"
    size_hint : hint to the hashtable sizer
    Returns
    -------
    labels : the indexer to the original array
    uniques : ndarray (1-d) or Index
        the unique values. Index is returned when passed values is Index or
        Series
    note: an array of Periods will ignore sort as it returns an always sorted
    PeriodIndex
    """
    from pandas import Index, Series, DatetimeIndex
    import pandas.core.common as com
    from pandas.core.algorithms import _get_data_algo, _hashtables
    vals = np.asarray(values)

    # localize to UTC
    is_datetimetz = com.is_datetimetz(values)
    if is_datetimetz:
        values = DatetimeIndex(values)
        vals = values.tz_localize(None)

    is_datetime = com.is_datetime64_dtype(vals)
    is_timedelta = com.is_timedelta64_dtype(vals)
    (hash_klass, vec_klass), vals = _get_data_algo(vals, _hashtables)

    table = hash_klass(size_hint or len(vals))
    uniques = vec_klass()
    labels = table.get_labels(vals, uniques, 0, na_sentinel, True)

    labels = com._ensure_platform_int(labels)

    uniques = uniques.to_array()

    if sort and len(uniques) > 0:
        try:
            sorter = uniques.argsort()
        except:
            # unorderable in py3 if mixed str/int
            t = hash_klass(len(uniques))
            t.map_locations(com._ensure_object(uniques))

            # order ints before strings
            ordered = np.concatenate([
                np.sort(np.array([e for i, e in enumerate(uniques) if f(e)],
                                 dtype=object)) for f in
                [lambda x: not isinstance(x, string_types),
                 lambda x: isinstance(x, string_types)]])
            sorter = com._ensure_platform_int(t.lookup(
                com._ensure_object(ordered)))

        reverse_indexer = np.empty(len(sorter), dtype=np.int_)
        reverse_indexer.put(sorter, np.arange(len(sorter)))

        mask = labels < 0
        labels = reverse_indexer.take(labels)
        np.putmask(labels, mask, -1)

        uniques = uniques.take(sorter)

    if is_datetimetz:

        # reset tz
        uniques = DatetimeIndex(uniques.astype('M8[ns]')).tz_localize(
            values.tz)
    elif is_datetime:
        uniques = uniques.astype('M8[ns]')
    elif is_timedelta:
        uniques = uniques.astype('m8[ns]')
    if isinstance(values, Index):
        uniques = values._shallow_copy(uniques, name=None)
    elif isinstance(values, Series):
        uniques = Index(uniques)
    return labels, uniques



"""these should probably  be acting on lists of strings...
and support nested catagories at some point...
should NOT be limited to pandas if possible
"""
def CategoricalLocator():
    """probably a wrapper on index formatter"""
    pass

def CategoricalFormatter():
    """Probably a wrapper on one of the string formatters"""
    pass



