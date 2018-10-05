import numpy as np
import os
import sys
sys.path.append('..')
import glob
from collections import Counter,OrderedDict, defaultdict
import cv2
import dicom


def getROINumber(structureset, roi_name, excluding=[]):
    """
    Returns the number associated with a given ROI in the DICOM file.
    We return the first number which has `roi_name` as a substring
    and is not in the `excluding` optional input argument.

    Parameters
    ----------
    structureset : DICOM dict
        The DICOM file read in by `dicom.read_file`. 

    roi_name : string
        The name of the ROI, for example `'bladder'` or `'PTV'`

    excluding : List of strings
        The previously processed ROIs of the same type. Used in the 
        event, primarily, of multiple PTVs. 

    Returns
    -------
    return : int
        The number associated with the ROI in the DICOM file
    """

    for n in range(0, len(structureset.StructureSetROISequence)):
        roi_name_query = structureset.StructureSetROISequence[n].ROIName 
        if roi_name in roi_name_query and roi_name_query not in excluding:
            return n

    return -1


def getContourInputs(BASE_DIR, StudyID, ROI_NAME, excluding=[]):
    """
    Returns inputs needed to test `getContours` with Local inputs. Prevents
    repetitive code in the notebooks.

    Parameters
    ----------
    BASE_DIR : string
        The base directory containing the `StudyID` subfolders.

    StudyID : string
        The study ID for the case being used.

    ROI_NAME : string
        The name of the ROI to extract contours for 

    excluding : List
        Default value is an empty list (`[]`). Used to avoid repeatedly getting 
        same ROI name.

    Returns
    -------
    block_shape : tuple
        The shape of the CT block, in the format `(height,
        width)`

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


    """
    ctFilenames = [fl for fl in os.listdir(BASE_DIR + "/" + StudyID) if 'CT' in fl]
    numImages = len(ctFilenames)

    sampleCTImage = dicom.read_file(BASE_DIR + StudyID + '/' + ctFilenames[0])
    width = sampleCTImage.Columns
    height = sampleCTImage.Rows

    block_shape = (width, height)

    structureset = dicom.read_file(BASE_DIR + StudyID + '/structureset.dcm')
    ROI_NUM = getROINumber(structureset, ROI_NAME)

    roiNumPlanes = len(structureset.ROIContourSequence[ROI_NUM].ContourSequence) 

    contour_data = {} # Input to function
    image_orientation = {} # Input to function
    image_position = {} # Input to function
    pixel_spacing = {} # Input to function

    for index in range(0, roiNumPlanes):
        
        imageSOP = structureset.ROIContourSequence[ROI_NUM].ContourSequence[index].ContourImageSequence[0].ReferencedSOPInstanceUID
        
        planeContourData = np.array(structureset.ROIContourSequence[ROI_NUM].ContourSequence[index].ContourData)
        planeContourData = planeContourData.reshape(planeContourData.shape[0] // 3 , 3)
        
        contour_data[imageSOP] = planeContourData
        imagei = dicom.read_file(BASE_DIR + StudyID + '/CT.' + imageSOP + '.dcm')
        
        image_orientation[imageSOP] = imagei.ImageOrientationPatient
        image_position[imageSOP] = imagei.ImagePositionPatient
        pixel_spacing[imageSOP] = imagei.PixelSpacing 

    return block_shape, contour_data, image_orientation, image_position, pixel_spacing