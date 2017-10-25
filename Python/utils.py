'''
This module is for general functions we use in the algorithm
use it in this way

import utils


'''
import numpy as np
from skimage.draw import polygon
import os
import sys
import glob
from collections import Counter,OrderedDict
import settings
import cv2


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

    colors = np.array([[255, 0, 255], [255, 0, 0], [255, 165, 0], 
    	[255, 255, 0], [0, 128, 0], [0, 0, 255], [128, 0, 128]])


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


def getContours(block_shape, slice_position_z, contour_data, image_orientation, image_position, pixel_spacing):
    """
    Returns the contour (perimeter) of a specified ROI, and
    the ROI mask of a specified ROI.

    Parameters
    ----------
    block_shape : tuple
        The shape of the CT block, in the format (height,
        width, number_of_ct_scans)

    slice_position_z : 1D NdArray
        The z coordinates of every CT scan for a patient.

    contour_data : dict of 2D NdArray
        Contains contour data (coordinates of contour perimeter)
        as specified by the clinician who entered them. Key
        for contour_data should be ReferencedSOPInstanceUID
        from the structureset dicom file.

    image_orientation : dict
        Contains image orientation data from dicom field
        ImageOrientationPatient for each ROI plane (subset
        of CT images). Key is also ReferencedSOPInstanceUID.

    image_position : dict
        Contains image position data from dicom field
        ImagePositionPatient for each ROI plane (subset
        of CT images). Key is also ReferencedSOPInstanceUID.

    pixel_spacing : dict
        Contains pixel spacing data from dicom field
        PixelSpacing for each ROI plane (subset
        of CT images). Key is also ReferencedSOPInstanceUID.

    Returns
    -------
    contour_block : 3D NdArray
        A 3D array of dimensions specified by block_shape. 
        Contains 1s at coordinates of contour and 0s elsewhere.

    roi_block : 3D NdArray
        A 3D array of dimensions specified by block_shape.
        Contains 1s on and inside contour perimeter and 0s
        elsewhere.

    """
    contour_block = np.zeros((block_shape)).astype(np.int8)
    roi_block = np.zeros((block_shape)).astype(np.int8)
    
    slice_position_z = np.sort(slice_position_z)[::-1] # sort Z coords in descending order- head is most positive z value

    for sop in contour_data:

        z_coor = contour_data[sop][0, 2]

        count = 0
        row_coordinates = np.zeros((contour_data[sop].shape[0])).astype(np.int)
        col_coordinates = np.zeros((contour_data[sop].shape[0])).astype(np.int)
        plane_coor = np.argwhere(slice_position_z == z_coor)[0][0].astype(np.int)
        
        for n in range(0, contour_data[sop].shape[0]):
            
            px = contour_data[sop][n, 0]
            py = contour_data[sop][n, 1]
        
            xx = image_orientation[sop][0]
            xy = image_orientation[sop][1]
            yx = image_orientation[sop][3]
            yy = image_orientation[sop][4]
            
            sx = image_position[sop][0]
            sy = image_position[sop][1]
        
            delJ = pixel_spacing[sop][0]
            delI = pixel_spacing[sop][1]
        
            A = np.array([[xx * delI, yx * delJ], [xy*delI, yy*delJ]])
            b = np.array([px - sx, py - sy])
        
            v = np.linalg.solve(A, b)
            col_coordinates[count] = int(np.round(v[0]))
            row_coordinates[count] = int(np.round(v[1]))
            
            contour_block[row_coordinates[count], col_coordinates[count], plane_coor] = 1
            
            count += 1

        rr, cc = polygon(row_coordinates, col_coordinates, shape=contour_block.shape[:2])
        roi_block[rr, cc, plane_coor] = 1

    return contour_block, roi_block


def getImageblock(patientID):
    """
    Numpy array of CT_IMAGE_BLOCK [height x width x num_ct_scans].
    Array is ordered such that first image is head, last is feet.

    Parameters
    ----------
    patientID : string
        The unique identifier for patient

    Returns
    -------
    imageBlcok : 3d array
        The shape is height * width * num_ct_scans
    uidList: list
        The list of UID, in the order as the slice
    """
    ##find the files through file storage system and use the code left
    ####Test parameter####
    DATA_PATH = settings.DATA_PATH
    #####################
    ct_files = glob.glob(DATA_PATH + patientID + '/' + 'CT*.dcm')
    num_ct_scans = len(ct_files)
    SOPID = OrderedDict()
    images = OrderedDict()
    for file in ct_files:
        df = dicom.read_file(file)
        if df.pixel_array is not None:
            # Based on the slicelocation to find where is the head where is the feet
            images[df.SliceLocation] = (df.SOPInstanceUID, df.pixel_array)
        else:
            print("No images")
            return None
    layer = 0
    # print(images)
    # the larger number of slicelocation is at the top, so reverse the order
    # Tha larger value of slicelocation is more closer to the head
    # images = OrderedDict(sorted(images.items(),reverse=True))
    imageBlock = np.zeros((df.Rows, df.Columns, len(images)))
    for key, value in images.items():
        SOPID[key] = value[0]
        imageBlock[:, :, layer] = value[1]
        layer += 1
    return imageBlock, SOPID

 