import numpy as np
from skimage.draw import polygon
import scipy.misc as misc
import sys
sys.path.append('..')
import glob
from collections import Counter,OrderedDict, defaultdict
import cv2
import dicom


def dicom_to_string(df):
    return ','.join([str(data_str) for data_str in df])


#convert string to list
def string_to_list(dbTextfiled):
    return dbTextfiled.split(',')


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


def _convertIsodoseCoordinates(temp_array, x0, y0, x_spacing, y_spacing):
    """

    Returns the rows and columns of each point of a given isodose value

    Parameters
    ----------
    temp_mask : 2d NdArray
        Contains dose data in dose array space. Is to be converted to CT array space.

    x0 : float
        Initial position (x) of isodose with respect to the CT scan. Used for aligning Isodose onto the CT scan

    y0 : float 
        Initial position (y) of isodose with respect to the CT scan. Used for aligning Isodose onto the CT scan

    x_spacing : float
        Pixel spacing of CT scan in the x direction

    y_spacing : float
        Pixel spacing of CT scan in the y direction
        
    Returns
    -------
    row : 1D NdArray
        Rows of each dose contour as corrected to CT array space

    col : 1D NdArray
        Columns of each dose contour as corrected to CT array space
    """

    temp_mask = misc.imresize((temp_array == 255), (temp_array.shape[0] * x_spacing, 
                                                    temp_array.shape[1] * y_spacing), 'nearest')

    row, col = np.nonzero(temp_mask)
    
    row = row + y0
    col = col + x0

    return row, col


def getIsodose(dose_grid, DoseGridScaling, x0, y0, x_spacing, y_spacing, sopUID):
    """
    Returns 2D isodose wash (contours of each dose)
    
    Parameters
    ----------
    dose_grid: 3D NdArray
        Dose values in the format (number_of_ct_scans, height, width)
    
    DoseGridScaling: float
        Scaling factor that when multiplied by dose bin widths (from dose_grid), yields dose bin widths in correct units 

    x0 : float
        Initial position (x) of isodose with respect to the CT scan. Used for aligning Isodose onto the CT scan

    y0 : float 
        Initial position (y) of isodose with respect to the CT scan. Used for aligning Isodose onto the CT scan

    x_spacing : float
        Pixel spacing of CT scan in the x direction

    y_spacing : float
        Pixel spacing of CT scan in the y direction

    sopUID : Dict of strings
        the Study IDs for each CT scan, in order. Used for indexing each slice of the dose grid by corresponding CT
        scan. 
        
    Returns
    -------
    isodose: Dict of Dict of 1D NdArray
         Array with outer dict key as SOPID and inner dict key as isodose value (percentage). Contains the rows
         and columns in the specified CT scan where the dose is greater than the percentage specified by the inner
         key.
    
    """
    dose_grid = np.swapaxes(np.swapaxes(dose_grid, 0, 2), 0, 1)
    dose_grid = dose_grid * DoseGridScaling

    maxDose = np.max(dose_grid)
    dose_grid = dose_grid / maxDose

    isodoseValues = np.array([40, 50, 60, 70, 80, 90, 95])

    sopIDs = list(sopUID.values())

    isodose = defaultdict(dict)

    for j in range(0, dose_grid.shape[2]):


        tempDoseMask = np.zeros(dose_grid.shape).astype(np.uint8)

        for n in range(0, len(isodoseValues)):

            doseMask = dose_grid > isodoseValues[n]*0.01 
            tempDoseMask[doseMask] = 1;

            temp_uint8_mask = np.array(tempDoseMask[:,:,j]).astype(np.uint8)
            doseOutline, contours, hierarchy = cv2.findContours(temp_uint8_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            temp_array = np.zeros(doseOutline.shape).astype(np.uint8)

            cv2.drawContours(temp_array, contours, -1, 255, 1)
            
            row, col = _convertIsodoseCoordinates(temp_array, x0, y0, x_spacing, y_spacing)

            rc = np.concatenate((np.expand_dims(row, axis=1), np.expand_dims(col, axis=1)), axis=1)

            isodose[sopIDs[j]] [isodoseValues[n]] = rc  
                                                                                      
    return isodose


def getMeanTargetDose(ptv_roi_block, block_shape, dose_grid, DoseGridScaling, x0, y0, x_spacing, y_spacing, sopUID):
    """
    
    Returns mean dose, as an absolute value scaled by `DoseGridScaling`, from inside the PTV.
    
    Parameters
    ----------
    ptv_roi_block : 3D NdArray
        A 3D array of dimensions specified by block_shape.
        Contains 1s on and inside PTV contour perimeter and 0s
        elsewhere.

    block_shape : tuple
        The shape of the CT block, in the format `(height,
        width, number_of_ct_scans)`

    DoseGridScaling: float
        Scaling factor that when multiplied by dose bin widths (from dose_grid), yields dose bin widths in correct units 

    x0 : float
        Initial position (x) of isodose with respect to the CT scan. Used for aligning Isodose onto the CT scan

    y0 : float 
        Initial position (y) of isodose with respect to the CT scan. Used for aligning Isodose onto the CT scan

    x_spacing : float
        Pixel spacing of CT scan in the x direction

    y_spacing : float
        Pixel spacing of CT scan in the y direction

    sopUID : Dict of strings
        the Study IDs for each CT scan, in order. Used for indexing each slice of the dose grid by corresponding CT
        scan. 
        
    Returns
    -------
    dose_mean : float
         Scalar mean dose of doses inside PTV contour
    
    """
    dose_grid = dose_grid * DoseGridScaling

    block_shape = block_shape + (ptv_roi_block.shape[2],)

    dose_array = np.zeros(block_shape).astype(np.float32)

    for j in range(0, dose_grid.shape[2]):

        temp_array = dose_grid[:, :, j].astype(np.float32)

        temp_mask = misc.imresize(temp_array, (temp_array.shape[0] * x_spacing, 
                                                    temp_array.shape[1] * y_spacing), 'nearest', mode='F')

        x_max = np.min((block_shape[0], temp_mask.shape[0] + x0))
        y_max = np.min((block_shape[1], temp_mask.shape[1] + y0))

        dose_array[x0 : x_max, y0 : y_max, j] = temp_mask[:x_max - x0, :y_max - y0]

    return np.mean(dose_array[ptv_roi_block == 1])


def convertROIToCTSpace(roi_block, image_position, sopIDs):
    """
    Converts an ROI block of size `[h x w x num_rois]` to 
    a CT block of size `[h x w x num_cts]`

    Parameters
    ----------
    roi_block : 3D NdArray
        A 3D array of dimensions specified by block_shape.
        Contains 1s on and inside contour perimeter and 0s
        elsewhere.

    image_position : dict
        Contains image position data from dicom field
        ImagePositionPatient for each ROI plane (subset
        of CT images). Key is also ReferencedSOPInstanceUID.

    SOPIDs : Ordered Dict
        Ordered by z variable, key is Z var, value is SOP ID.

    Returns
    -------
    ct_roi_block : 3D NdArray
        the `roi_block` with zeros intersped where there is no
        ROI contour. 
    """
    ct_z = np.array(list(sopIDs.keys()), dtype=np.float32)

    slice_position_z = np.zeros(roi_block.shape[2]).astype(np.float32)
    for i, ct in enumerate(image_position.values()):
        slice_position_z[i] = ct[2]
    np.sort(slice_position_z)[::-1]


    ct_roi_block = np.zeros((roi_block.shape[0], roi_block.shape[1], len(sopIDs))).astype(np.int8)

    for i in range(0, slice_position_z.shape[0]):

        ct_roi_block[:, :, np.argwhere(ct_z == slice_position_z[i])[0][0]] = roi_block[:, :, i]

    return ct_roi_block


def getContours(block_shape, contour_data, 
    image_orientation, image_position, pixel_spacing):
    """
    Returns the contour (perimeter) of a specified ROI, and
    the ROI mask of a specified ROI.

    Parameters
    ----------
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

    slice_position_z = np.zeros(len(contour_data)).astype(np.float32)
    for i, ct in enumerate(image_position.values()):
        slice_position_z[i] = ct[2]
    np.sort(slice_position_z)[::-1]

    block_shape = block_shape + (len(contour_data),)
    contour_block = np.zeros((block_shape)).astype(np.int8)
    roi_block = np.zeros((block_shape)).astype(np.int8)

    for sop in contour_data:

        z_coor = contour_data[sop][0, 2]

        count = 0
        row_coordinates = np.zeros((contour_data[sop].shape[0])).astype(np.int)
        col_coordinates = np.zeros((contour_data[sop].shape[0])).astype(np.int)
        plane_coor = np.argwhere(slice_position_z == z_coor).astype(np.int)
        
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


def getImageBlock(patientID, DATA_PATH):
    """
    Numpy array of CT_IMAGE_BLOCK [height x width x num_ct_scans].
    Array is ordered such that first image is head, last is feet.

    Parameters
    ----------
    patientID : string
        The unique identifier for patient

    DATA_PATH : string
        The abosolute local path location where dicom CT scan files are stored.
        
    Returns
    -------
    imageBlock : 3d array
        The shape is height * width * num_ct_scans

    SOPID : Ordered Dict
        The list of UID, in the order as the slice
    """

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
    
    imageBlock = np.zeros((df.Rows, df.Columns, len(images)))
    for key, value in images.items():
        SOPID[key] = value[0]
    
    # the larger number of slicelocation is at the top, so reverse the order
    # Tha larger value of slicelocation is more closer to the head
    SOPID = OrderedDict(sorted(SOPID.items(), key=lambda t : t[0], reverse=True))
    
    layer = 0
    for key, value in SOPID.items():
        imageBlock[:, :, layer] = images[key][1]
        layer += 1
    
    return imageBlock, SOPID
