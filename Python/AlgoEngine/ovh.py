import numpy as np
from math import sqrt
try:
	from .utils import getVolume, getContours
except:
	from AlgoEngine.utils import getVolume, getContours
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


def getOVHDistances(oar_roi_block, ptv_contour_block, ptv_roi_block, row_spacing, column_spacing, slice_spacing):
	"""
	Returns the distances of each voxel in the `oar_roi_block` to the nearest PTV surface voxel.

	Parameters
	----------
	oar_roi_block : 3D NdArray
		A 3D array with 1s inside and on contour perimeter of OAR ROI and 0s elsewhere.

	ptv_contour_block : 3D NdArray
		A 3D array with 1s on contour perimeter of PTV and 0s elsewhere.

	ptv_roi_block : 3D NdArray
		A 3D array with 1s inside and on contour perimeter of PTV ROI and 0s elsewhere.

	row_spacing : float
		Spacing between rows of CT image

	column_spacing : float
		Spacing between columns of CT image

	slice_spacing : float
		Spacing between slices (separate CT images) of CT block

	Returns
	-------
	oar_dists : 3D NdArray
		A 3D array with the same shape as `oar_roi_block`. Where `oar_roi_block` contains 1s,
		`oar_dists` contains distances between the given voxel and the closest voxel on the PTV
		surface. Note that distance is negative for an OAR voxel inside the PTV.

	"""
	oar_intersecting = np.zeros(oar_roi_block.shape).astype(np.int8)
	oar_nonintersecting = np.zeros(oar_roi_block.shape).astype(np.int8)

	oar_intersecting[(oar_roi_block == 1) & (oar_roi_block == ptv_roi_block)] = 1
	oar_nonintersecting = oar_roi_block - oar_intersecting

	oar_i_row, oar_i_col, oar_i_slice = np.nonzero(oar_intersecting)

	oar_ni_row, oar_ni_col, oar_ni_slice = np.nonzero(oar_nonintersecting)

	oar_dists = np.zeros(oar_roi_block.shape).astype(np.float32)

	ptv_row, ptv_col, ptv_slice = np.nonzero(ptv_contour_block)


	num_ptv_voxels = np.count_nonzero(ptv_contour_block)
	num_oar_voxels_i = np.count_nonzero(oar_intersecting)
	num_oar_voxels_ni = np.count_nonzero(oar_nonintersecting)

	alpha = column_spacing / row_spacing
	beta =  slice_spacing / row_spacing

	for oar_voxel in range(0, num_oar_voxels_i):
	    min_distance = 1000000
	    for ptv_voxel in range(0, num_ptv_voxels):
	        distance = sqrt( (oar_i_row[oar_voxel] - ptv_row[ptv_voxel])**2  + 
	                        alpha*(oar_i_col[oar_voxel] - ptv_col[ptv_voxel])**2 + 
	                        beta*(oar_i_slice[oar_voxel] - ptv_slice[ptv_voxel])**2)
	        
	        min_distance = min(distance, min_distance)
	    
	    oar_dists[oar_i_row[oar_voxel], oar_i_col[oar_voxel], oar_i_slice[oar_voxel]]= -1 * min_distance

	for oar_voxel in range(0, num_oar_voxels_ni):
	    min_distance = 1000000
	    for ptv_voxel in range(0, num_ptv_voxels):
	        distance = sqrt( (oar_ni_row[oar_voxel] - ptv_row[ptv_voxel])**2  + 
	                        alpha*(oar_ni_col[oar_voxel] - ptv_col[ptv_voxel])**2 + 
	                        beta*(oar_ni_slice[oar_voxel] - ptv_slice[ptv_voxel])**2)
	        
	        min_distance = min(distance, min_distance)
	    
	    oar_dists[oar_ni_row[oar_voxel], oar_ni_col[oar_voxel], oar_ni_slice[oar_voxel]] = min_distance

	return oar_dists


def getOVHDistancesOptimized(oar_roi_block, ptv_contour_block, ptv_roi_block, row_spacing, column_spacing, slice_spacing):
	"""
	Returns the distances of each voxel in the `oar_roi_block` to the nearest PTV surface voxel, with 
	additional optimizations in numpy

	Parameters
	----------
	oar_roi_block : 3D NdArray
		A 3D array with 1s inside and on contour perimeter of OAR ROI and 0s elsewhere.

	ptv_contour_block : 3D NdArray
		A 3D array with 1s on contour perimeter of PTV and 0s elsewhere.

	ptv_roi_block : 3D NdArray
		A 3D array with 1s inside and on contour perimeter of PTV ROI and 0s elsewhere.

	row_spacing : float
		Spacing between rows of CT image

	column_spacing : float
		Spacing between columns of CT image

	slice_spacing : float
		Spacing between slices (separate CT images) of CT block

	Returns
	-------
	oar_dists : 3D NdArray
		A 3D array with the same shape as `oar_roi_block`. Where `oar_roi_block` contains 1s,
		`oar_dists` contains distances between the given voxel and the closest voxel on the PTV
		surface. Note that distance is negative for an OAR voxel inside the PTV.

	"""
	oar_intersecting = np.zeros(oar_roi_block.shape).astype(np.int8)
	oar_nonintersecting = np.zeros(oar_roi_block.shape).astype(np.int8)

	oar_intersecting[(oar_roi_block == 1) & (oar_roi_block == ptv_roi_block)] = 1
	oar_nonintersecting = oar_roi_block - oar_intersecting

	oar_i_coords = np.nonzero(oar_intersecting)

	oar_ni_coords = np.nonzero(oar_nonintersecting)

	oar_dists = np.zeros(oar_roi_block.shape).astype(np.float32)

	ptv_coords = np.nonzero(ptv_contour_block)
	# reshape to 1 array
	ptv_coords = np.concatenate(( 
		np.expand_dims(ptv_coords[0],axis=-1),
		np.expand_dims(ptv_coords[1],axis=-1),
		np.expand_dims(ptv_coords[2],axis=-1),
	), axis=-1)
	oar_ni_coords = np.concatenate(( 
		np.expand_dims(oar_ni_coords[0],axis=-1),
		np.expand_dims(oar_ni_coords[1],axis=-1),
		np.expand_dims(oar_ni_coords[2],axis=-1),
	), axis=-1)
	oar_i_coords = np.concatenate(( 
		np.expand_dims(oar_i_coords[0],axis=-1),
		np.expand_dims(oar_i_coords[1],axis=-1),
		np.expand_dims(oar_i_coords[2],axis=-1),
	), axis=-1)

	num_oar_voxels_i = np.count_nonzero(oar_intersecting)
	num_oar_voxels_ni = np.count_nonzero(oar_nonintersecting)

	alpha = column_spacing / row_spacing
	beta =  slice_spacing / row_spacing
	
	for oar_voxel in range(0, num_oar_voxels_i):
		oar_dists[oar_i_coords[oar_voxel]] = -1 * np.min(np.sqrt(np.sum(
			(ptv_coords[:, 0] - oar_i_coords[oar_voxel, 0]) ** 2 +
			alpha * (ptv_coords[:, 1] - oar_i_coords[oar_voxel, 1]) ** 2 +
			beta * (ptv_coords[:, 2] - oar_i_coords[oar_voxel, 2]) ** 2
			)))

	print("processing nonintersecting ovh pixels: " + str(num_oar_voxels_ni))
	
	# For time saving reasons we cut all long processes
	if num_oar_voxels_ni < 1000000:
		for oar_voxel in range(0, num_oar_voxels_ni):
			if (oar_voxel + 1) % max(1, int(num_oar_voxels_ni/10)) == 0:
				print("processing pixels...")
			oar_dists[oar_ni_coords[oar_voxel]] = np.min(np.sqrt(np.sum(
				(ptv_coords[:, 0] - oar_ni_coords[oar_voxel, 0]) ** 2 +
				alpha * (ptv_coords[:, 1] - oar_ni_coords[oar_voxel, 1]) ** 2 +
				beta * (ptv_coords[:, 2] - oar_ni_coords[oar_voxel, 2]) ** 2
				)))

	return oar_dists

def getOVH(oar_roi_block, ptv_contour_block, ptv_roi_block, pixel_spacing, 
	row_spacing, column_spacing, slice_spacing, n_bins):
	"""
	Gets a complete OVH histogram given preprocessed DICOM inputs. For use with managers / other wrapper
	classes to get data effectively.

	Parameters
	----------
	oar_roi_block : 3D NdArray
		A 3D array with 1s inside and on contour perimeter of OAR ROI and 0s elsewhere.

	ptv_contour_block : 3D NdArray
		A 3D array with 1s on contour perimeter of PTV and 0s elsewhere.

	ptv_roi_block : 3D NdArray
		A 3D array with 1s inside and on contour perimeter of PTV ROI and 0s elsewhere.

    row_spacing : float
		Spacing between rows of CT image

	column_spacing : float
		Spacing between columns of CT image

	slice_spacing : float
		Spacing between slices (separate CT images) of CT block

	n_bins : int
		Contains the number of bins the user desires for histogram generation.
		A greater amount of bins may give more accurate hisotgrams but will
		result in longer runtims.


	Returns
	-------
	bin_vals : 1D NdArray
		A vector of length `n-bins + 1`. Contains the bin intervals starting at
		minimum distance, ending at maximum distance.

	norm_bin_amts : 1D NdArray
		Contains the percentage of pixels at a given distance
		or less

	"""
	
	oar_dists = getOVHDistancesOptimized(oar_roi_block, ptv_contour_block, ptv_roi_block, row_spacing, column_spacing, slice_spacing)
	print("done with distance")
	bin_vals, bin_amts = getHistogram(oar_dists, oar_roi_block, n_bins)
	print("done with histogram")
	volume = getVolume(oar_roi_block)
	print("done with volume")
	norm_bin_amts = getNormalizedHistogram(bin_amts, volume)
	print("donw with normalization")
	return bin_vals, norm_bin_amts
