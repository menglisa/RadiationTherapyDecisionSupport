import MySQLdb
import settings
from sshtunnel import SSHTunnelForwarder
from types import *
from utils import *
from DataFetcher import DataFetcher
import pdb

from AlgoEngine import AlgoManager

"""
Testing file for the backend SQL connections
with the functions.

First, feature extraction is done and saved
to the server. 

Then (in the future) you can use this script
for similarity testing as well
"""

am = AlgoManager('3', False)

# tests saving of STS and OVH
#am.feature_extraction()

# TODO: tests saving of similarity
am.similarity_calculation()


########################################################################################################################
#
# query_for_study_list = 'SELECT * from studies'
# query_for_roi_list = 'SELECT * from rt_rois WHERE fk_study_id_id = 1'
# query_for_contour = 'SELECT * from rt_contour WHERE fk_roi_id_id = %s AND fk_structureset_id_id = %s'
# query_for_image_plane_info = 'SELECT * from ct_images WHERE SOPInstanceUID = %s'
# server = SSHTunnelForwarder((settings.ssh_hostname,settings.ssh_port),ssh_username=settings.ssh_username,ssh_password=settings.ssh_password,
#                         remote_bind_address=('127.0.0.1',3306))
# server.start()
#
# con = MySQLdb.connect('127.0.0.1',port = server.local_bind_port,
#
#                      user = settings.database_username,passwd = settings.database_password,db = settings.database_name)
# #
# cur = con.cursor(MySQLdb.cursors.DictCursor)
# cur.execute('SELECT ContourData from rt_contour WHERE id = 8140')
#
# data = cur.fetchall()
# print(len(data))
#
# contour = data[0]['ContourData']
# print(contour)
#
#
#
# con.close()
#
# server.stop()

#
# con.close()
# cur = con.cursor(MySQLdb.cursors.DictCursor)
# cur.execute('SELECT ContourData from rt_contour WHERE id = 8140')
# data = cur.fetchall()
# print(data)

# rois = cur.fetchall()
# res = {}
# for roi in rois:
#     roi_name = roi['ROIName']
#     cur.execute(query_for_contour,(roi['id'],roi['fk_structureset_id_id']))
#     contour_dict = {}
#     imagePatientOrientaion = []
#     imagePatientPosition = {}
#     pixelSpacing = None
#     block_shape = []
#     Contours = cur.fetchall()
#     for contour in Contours:
#         contour_dict[contour['ReferencedSOPInstanceUID']] = contour['ContourData']
#         cur.execute(query_for_image_plane_info,[contour['ReferencedSOPInstanceUID']])
#         image_info = cur.fetchall()[0]
#
#         if not imagePatientOrientaion:
#             imagePatientOrientaion = image_info['ImageOrientationPatient'][0]
#         if not pixelSpacing:
#             pixelSpacing = image_info['PixelSpacing']
#         if not block_shape:
#             block_shape = (image_info['Rows'],image_info['Columns'])
#         imagePatientPosition[contour['ReferencedSOPInstanceUID']] = image_info['ImagePositionPatient']
#
#     #call utils function to reorganize the things in block
#     #block_shape, slice_position_z, contour_data, image_orientation, image_position, pixel_spacing
#     # contour_block = getContours(block_shape,contour_data,image_orientation=imagePatientOrientaion,
#     #             image_position=imagePatientPosition,pixel_spacing=pixelSpacing)
#     res[roi_name] = contour_dict

