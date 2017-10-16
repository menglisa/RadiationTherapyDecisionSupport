import numpy as np


def getHistogram(oar_dists, oar_roi_block, n_bins):
	"""
	Returns the non-normalized histogram vectors for the OVH histogram.

	Parameters
	----------
	oar_dists : 3D NdArray
		Contains distances of each OAR voxel to the closest PTV surface labelled 
		over the corresponding voxel.
	oar_roi_block : 3D NdArray
		Contains 1s for all points inside the ROI, and 0s for all points
		outside the ROI.
	n_bins : int
		Contains the number of bins the user desires for histogram generation.
		A greater amount of bins may give more accurate hisotgrams but will
		result in longer runtims.

	Returns
	-------
	bin_vals : 1D NdArray
		A vector of length `n-bins + 1`. Contains the bin intervals starting at
		minimum distance, ending at maximum distance.
	bin_amts : 1D NdArray
		A vector of length `n_bins`. Contains the number of OAR voxels in each
		bin interval. The kth element in `bin_amts`contains the number of OAR
		voxels with distances from `bin_vals[k]` to `bin_vals[k+ 1].`

	"""
	min_distance = np.min(oar_dists[oar_roi_block == 1])
	max_distance = np.max(oar_dists[oar_roi_block == 1])
	delta = (max_distance - min_distance) / n_bins

	bin_amts = np.zeros((n_bins )).astype(np.int)
	bin_vals = np.zeros((n_bins + 1)).astype(np.float64)

	bin_vals[0] = min_distance
	bin_vals[-1] = max_distance

	for n in range(0, n_bins):
	    bin_vals[n + 1] = min_distance + delta*(n + 1)
	    bin_amts[n] = np.count_nonzero((oar_roi_block == 1) & (oar_dists < bin_vals[n + 1]) & (oar_dists >= bin_vals[n]))


	return bin_vals, bin_amts