def getElevation(ptv_vox, oar_cen):
    """
    Returns the elevation between two voxels
    
    Parameters
    ----------
    ptv_vox : tuple
        Index location of PTV voxel
        
    oar_cen : tuple
        Index location of OAR centroid
        
    Returns
    -------
    elevation : int
        Elevation between voxels 
   
    """
    
    elevation = (ptv_vox[2]-oar_cen[2]) #absolute value? 
    return elevation