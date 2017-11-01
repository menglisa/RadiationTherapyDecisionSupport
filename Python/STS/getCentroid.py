import numpy as np

def getCentroid(roi_block):
    
    positions = np.where(roi_block == 1)
    
    x_center = round(np.average(positions[0])).astype(np.uint8)
    y_center = round(np.average(positions[1])).astype(np.uint8)
    z_center = round(np.average(positions[2])).astype(np.uint8)
    
    return [x_center, y_center, z_center]
