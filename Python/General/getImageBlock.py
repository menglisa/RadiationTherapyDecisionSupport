import dicom
import os
import sys
import glob
import numpy as np
from collections import Counter,OrderedDict
import matplotlib.pyplot as plt
import cv2
sys.path.append('..')
import settings


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
    imageBlock : 3d array
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
