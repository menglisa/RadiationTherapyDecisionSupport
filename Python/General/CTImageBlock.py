
# coding: utf-8


import dicom
import os
import sys
import glob
import numpy as np
from collections import Counter,OrderedDict
import matplotlib.pyplot as plt
import cv2


# In[15]:

import dicom
import os
import sys
import glob
import numpy as np
from collections import Counter,OrderedDict
import matplotlib.pyplot as plt
import cv2


def get_ct_image_block(patientID):
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
    DATA_PATH = 'D:/Django/matlab/Backup/MATLAB/data/'
    #####################
    ct_files = glob.glob(DATA_PATH + patientID + '/' + 'CT*.dcm')
    num_ct_scans = len(ct_files)
    SOPID = []
    images = OrderedDict()
    for file in ct_files:
        df = dicom.read_file(file)
        if df.pixel_array is not None:
            #Based on the slicelocation to find where is the head where is the feet
            images[df.SliceLocation] = (df.SOPInstanceUID,df.pixel_array)
        else:
            print("No images")
            return None
    layer = 0
    #the larger number of slicelocation is at the top, so reverse the order
    images = OrderedDict(sorted(images.items(),reverse=True))
    imageBlock = np.zeros((df.Rows,df.Columns,len(images)))
    for key,value in images.items():
        SOPID.append(value[0])
        imageBlock[:,:,layer] = value[1]
        layer += 1
    return imageBlock,SOPID
 
# def mouse_callback(event,slicelocation,flags,param):
#     if event == cv2.EVENT_MOUSEWHEEL:
#         delta = cv2.getMouseWheelDelta()
#         if delta > 0:
#             cv2.
if __name__ == '__main__':
    patientID = 'UCLA_PR_5'
    imageBlock,SOPID = get_ct_image_block(patientID)
#     print(imageBlock.shape)
#     print(SOPID)
    for index in range(300):
        plt.figure(index)
        plt.imshow(imageBlock[:,:,index],cmap=plt.get_cmap('gray'))
        plt.show()





