import dicom
import os
import sys
import glob
import numpy as np
from collections import Counter,OrderedDict
import matplotlib.pyplot as plt
import cv2


def getImageBlock(images, rows, cols, num_cts):
    """
    Numpy array of CT_IMAGE_BLOCK [height x width x num_ct_scans]. 
    Array is ordered such that first image is head, last is feet.

    Parameters
    ----------
    patientID : string
        The unique identifier for patient

    Returns
    -------
    imageBlock : 3d Ndarray
        The shape is height * width * num_ct_scans
    uidList: list
        The list of UID, in the order as the slice
    """
    layer = 0
    SOPID = OrderedDict()

    #the larger number of slicelocation is at the top, so reverse the order
    #The head is the largest value of slicelocation
    images = OrderedDict(sorted(images.items(),reverse=True))
    imageBlock = np.zeros((rows, cols, num_cts)).astype(np.uint16)
    for key,value in images.items():
        SOPID[key] = value[0]
        imageBlock[:,:,layer] = value[1]
        layer += 1
    return imageBlock,SOPID
