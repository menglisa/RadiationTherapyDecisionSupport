import dicom
import numpy as np
import cv2
import matplotlib.pyplot as plt

def getIsodose(dose_grid, DoseGridScaling):
    """
    Returns 2D isodose wash (contours of each dose)
    
    Parameters
    ----------
    dose_grid: 3D NdArray
        Dose values in the format (number_of_ct_scans, height, width)
    
    DoseGridScaling: floating point
        Scaling factor that when multiplied by dose bin widths (from dose_grid), yields dose bin widths in correct units 
        
    Returns
    -------
    doseBlocks: 4D NdArray
         Array wit all dose contours of varying values (40%, 50%, etc.) in one block in the format (height, width, RGB channel, number_of_ct_scan]
    
    """
    
    dose_grid = np.swapaxes(np.swapaxes(dose_grid, 0, 2), 0, 1)
    dose_grid = dose_grid * DoseGridScaling

    dose_grid = np.expand_dims(dose_grid, axis=2)
    dose_grid = np.repeat(dose_grid, 3, axis=2)

    maxDose = np.max(dose_grid)
    dose_grid = dose_grid/maxDose

    isodoseValues = np.array([40, 50, 60, 70, 80, 90, 95])

    doseBlocks = np.zeros(dose_grid.shape).astype(np.uint8)

    colors = np.array([[255, 0, 255], [255, 0, 0], [255, 165, 0], [255, 255, 0], [0, 128, 0], [0, 0, 255], [128, 0, 128]])


    for n in range(0, len(isodoseValues)):

        tempDoseMask = np.zeros(dose_grid.shape).astype(np.uint8)
        doseOutline = np.zeros(dose_grid.shape).astype(np.uint8)

        doseMask = dose_grid > isodoseValues[n]*0.01 # removed maxDose 
        tempDoseMask[doseMask] = 1;

        for j in range(0, dose_grid.shape[3]):
            for channel in range(0, 3):
                temp_temp_mask = np.array(tempDoseMask[:,:,channel,j]).astype(np.uint8)
                doseOutline[:,:,channel,j], contours, hierarchy = cv2.findContours(temp_temp_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                temp_array = np.zeros(doseOutline[:,:,channel,j].shape).astype(np.uint8)

                cv2.drawContours(temp_array, contours, -1, 255, 1)
                temp_mask = temp_array == 255
                temp_array[temp_mask] = colors[n, channel]
                doseBlocks[:,:,channel,j][temp_mask] = temp_array[temp_mask]  
                                                                                  
    return doseBlocks