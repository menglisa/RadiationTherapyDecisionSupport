from getDistance import getDistance
from getElevation import getElevation
import numpy as np
from math import acos


def getAzimuth(ptv_vox, oar_cen):
    """
    Returns the azimuth between two voxels
    
    Parameters
    ----------
    ptv_vox : tuple
        Index location of PTV voxel
        
    oar_cen : tuple
        Index location of OAR centroid
        
    Returns
    -------
    azimuth : double
        Azimuth angle between voxels (in radians)
   
    """
    elevation = getElevation(ptv_vox, oar_cen)
    distance = getDistance(ptv_vox, oar_cen)
    
    z_over_r = elevation/distance
    azimuth = acos(z_over_r)
    return azimuth