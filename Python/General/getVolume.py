import numpy as np

def getVolume(roi_block):
    """
    Returns the volume of an ROI as the number of voxels it contains
    
    Parameters
    ----------
    roi_block : 3d Ndarray
        A 3D array of dimensions h x w  x num_cts. Contains 1s on and inside contour perimeter and 0s elsewhere.
        
    Returns
    -------
    volume : int
        Number of voxels in ROI 
   
    """
    
    volume = np.count_nonzero(roi_block)
    return volume