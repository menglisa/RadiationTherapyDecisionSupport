import numpy as np


def getNormalizedHistogram(bin_amts, volume):
	"""
	Returns the normalized vector containing the 
	percentage of pixels at a given distance or lower.

	Parameters
	----------
	bin_amts : 1D NdArray
		Contains the number of pixels at a given distance,
		specified in `bin_vals` returned from `getHistogram`
	volume : int 
		Contains the number of pixels in the ROI

	Returns
	-------
	norm_bin_amts : 1D NdArray
		Contains the percentage of pixels at a given distance
		or less

	"""

	norm_bin_amts = np.cumsum(bin_amts) / np.float32(volume)
	return norm_bin_amts