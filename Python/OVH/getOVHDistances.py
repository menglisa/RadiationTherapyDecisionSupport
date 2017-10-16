import numpy as np
from math import sqrt

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
