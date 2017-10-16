import dicom
import numpy as np
from skimage.draw import polygon

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
