import numpy as np
import dicom
import sys
sys.path.append('..')
import cv2
from .ovh import getOVH
from .utils import getContours
from math import sqrt


def getOVHEmd(query_bin_vals, query_bin_amts, historical_bin_vals, historical_bin_amts):
	"""
	Returns the Earth Mover's distance for a single PTV-OAR pair. 

	Parameters
	----------
	query_bin_vals : 1D NdArray
		A vector of length `n-bins + 1`. Contains the bin intervals starting at
		minimum distance, ending at maximum distance for the query patient.

	query_bin_amts : 1D NdArray
		Contains the percentage of pixels at a given distance range (`i to i + 1`)
		or less for the query patient.

	historical_bin_vals : 1D NdArray
		A vector of length `n-bins + 1`. Contains the bin intervals starting at
		minimum distance, ending at maximum distance for the historical patient.

	historical_bin_amts : 1D NdArray
		Contains the percentage of pixels at a given distance range (`i to i + 1`)
		or less for the historical patient.

	Returns
	-------
	emd : float
		The scalar earth mover's distance (dissimilarity) between the two study pairs.

	"""

	query_bin_vals = np.expand_dims(query_bin_vals[1:], axis=1)
	query_bin_amts = np.expand_dims(query_bin_amts, axis=1)
	weights = np.ones((query_bin_vals.shape[0], 1))

	query_hist = np.array(np.concatenate((weights, query_bin_vals, query_bin_amts), axis=1))

	historical_bin_vals = np.expand_dims(historical_bin_vals[1:], axis=1)
	historical_bin_amts = np.expand_dims(historical_bin_amts, axis=1)
	weights_historical = np.ones((historical_bin_vals.shape[0], 1))

	historical_hist = np.array(np.concatenate((weights, historical_bin_vals, historical_bin_amts), axis=1))

	query_hist = query_hist.astype(np.float32)
	historical_hist = historical_hist.astype(np.float32)

	emd = cv2.EMD(query_hist, historical_hist, distType=2)[0]
	return emd


def getSTSEmd(query_sts, historical_sts):
	"""
	Returns the Earth Mover's distance for a single PTV-OAR pair's spatial transformation signature.

	Parameters
	----------

	query_sts : 2D NdArray
        Dimensions are [num_combinations, 4]. Contains
        percentage of points in each interval, normalized but not cumulative, for the query case.

    historical_sts : 2D NdArray
        Dimensions are [num_combinations, 4]. Contains
        percentage of points in each interval, normalized but not cumulative, for the historical case.

	Returns
	-------
	emd : float
		The scalar earth mover's distance (dissimilarity) between the two study pairs.
	"""
	weights_hist = np.ones((historical_sts.shape[0], 1))
	weights_query = np.ones((query_sts.shape[0], 1))

	query_hist = np.array(np.concatenate((weights_query, query_sts), axis=1)).astype(np.float32)
	historical_hist = np.array(np.concatenate((weights_hist, historical_sts), axis=1)).astype(np.float32)

	emd = cv2.EMD(query_hist, historical_hist, distType=2)[0]
	return emd


def getTDDistance(query_dose_mean, historical_dose_mean):
	"""
	Returns the absolute L1 distance between the query and historical dose means from the same PTV.

	Parameters
	----------
	query_dose_mean : float
		A float representing the mean dose inside the PTV ROI in the query case

	historical_dose_mean : float
		Represents the mean dose inside the PTV ROI of the historical case

	Returns
	-------
	dose_distance : float
		A scalar of the L1 distance between the query and historical dose means.
	"""

	dose_distance = np.abs(query_dose_mean - historical_dose_mean)
	return dose_distance