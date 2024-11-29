#!/usr/bin/python3

__all__ = ["threshold_otsu"]

import numpy as np

def threshold_otsu(image, bins=256, range_=None):
    """
    Returns the threshold value of the image based on the Otsu's 
    threshold selection method.
    
    Parameters
    ----------
    image : array_like
        Input data.
    bins : int or sequence of scalars or str, optional
        Same usage like for the numpy histogram function [0].
    
    range_ : (float, float), optional
        The lower and upper range of the bins.
        Same usage like for the numpy histogram function [0].
    
    Returns
    -------
    threshold : float
        The threshold value.
    
    References
    ---------
    [0] https://docs.scipy.org/doc/numpy/reference/generated/numpy.histogram.html
    [1] Otsu, 1979, A Threshold Selection Method from Gray-Level Histograms, 
        DOI: 10.1109/TSMC.1979.4310076 
    """
    

    if len(image) == 0:
        raise ValueError("the image is empty")
    
    # calculate the normalized histogram --> np.sum(normalized_histogram) == 1.0
    histogram, bin_edges = np.histogram(image.ravel(), bins=bins, range=range_)
    normalized_histogram = histogram / np.sum(histogram)
    
    if isinstance(bins, str):
        # the bins parameter can also be used as estimator string identifier 
        # for the call of np.histogram()
        bins = len(normalized_histogram)
    
    # calculate the total mean value of the image
    mt = np.dot(np.arange(bins), normalized_histogram)
    
    # calculate the zeroth- and first-order cumulative moments (sums)
    w = normalized_histogram.cumsum()
    m = (np.arange(bins) * normalized_histogram).cumsum()
    
    # find the maximum value of the between-class variance
    var_max, threshold = 0.0, np.nanmax(image)
    for k in range(bins):
        if not 0 < w[k] < 1:
            continue
        var = ((mt * w[k] - m[k])**2) / (w[k] * (1.0 - w[k]))
        if var > var_max:
            var_max = var
            threshold = bin_edges[k] + 0.5 * (bin_edges[k+1] - bin_edges[k])

    return threshold
