def getDistance(ptv_vox, oar_cen):
    """
    Returns the radial distance between two voxels
    
    Parameters
    ----------
    ptv_vox : tuple
        Index location of PTV voxel
        
    oar_cen : tuple
        Index location of OAR centroid
        
    Returns
    -------
    distance : int
        Radial distance between voxels 
   
    """
    
    distance = ((ptv_vox[0]-oar_cen[0])**2 + (ptv_vox[1]-oar_cen[1])**2 + (ptv_vox[2]-oar_cen[2])**2)**(0.5)
    return distance