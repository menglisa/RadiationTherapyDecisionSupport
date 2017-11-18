import MySQLdb
import settings
from sshtunnel import SSHTunnelForwarder
from utils import *



# Imports for STS / OVH / etc
import sys
sys.path.append('..')
from utils import getContours, getMeanTargetDose
from sts import getSTSHistogram
from ovh import getOVH
from similarity import getSTSEmd, getOVHEmd, getTDDistance

import re

#in order to use this AlgoEngine separately, we build this datafetcher by using MySQLdb instead of Django ORM
#it can also be implemented with Django ORM

query_for_study_list = 'SELECT id from studies WHERE id NOT IN (%s)'
query_for_roi_list = 'SELECT * from rt_rois WHERE fk_study_id_id = %s'
query_for_contour = 'SELECT * from rt_contour WHERE fk_roi_id_id = %s AND fk_structureset_id_id = %s'
query_for_image_plane_info = 'SELECT * from ct_images WHERE SOPInstanceUID = %s'
class DataFetcher():
    def __init__(self):
        #build connection
        #save the connection with the class

        #define some prepared statement to fetch data
        #usin ssh tunnel
        self.server = SSHTunnelForwarder((settings.ssh_hostname, settings.ssh_port), ssh_username=settings.ssh_username,
                                    ssh_password=settings.ssh_password,
                                        remote_bind_address=('127.0.0.1', 3306))
        self.server.start()

        self.connection = MySQLdb.connect('127.0.0.1',port = self.server.local_bind_port,
                          user = settings.database_username,passwd = settings.database_password,db = settings.database_name)

        self.cursor = self.connection.cursor(MySQLdb.cursors.DictCursor)


    #with these two functions, we could use with statement with instance of this class
    #because we use with statement with db connection, we want to inherit this convention
    def __enter__(self):
        return DataFetcher()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("exit the context manager")
        #close the db connection
        if self.connection:
            print("close connection")
            self.connection.close()

        #close the ssh connection
        if self.server:
            print("close the server")
            self.server.stop()

        print("finish the exit process")

    def get_contours(self,studyID):
        '''
        Get contour block for all rois under this studyID
        we need fetch following things to construct
        block_shape
        slice_position_z
        contour_data
        image_orientation
        image_position
        pixel_spacing
        :param studyID:
        :return: a list of dictionaries, the first dictionary contains ptv and the second contains OAR
        in the dictionary the key is the name of Roi, the value is the contour block
        {
            ROI:contourBlock
        }
        '''
        self.cursor.execute(query_for_roi_list,studyID)
        rois = self.cursor.fetchall()
        ptv_dict = {}
        oar_dict = {}
        for roi in rois:
            roi_name = roi['ROIName']
            if re.match(r'^PTV',roi_name,re.IGNORECASE):
                self.cursor.execute(query_for_contour, (roi['id'], roi['fk_structureset_id_id']))
                imagePatientOrientaion = []
                imagePatientPosition = {}
                pixelSpacing = None
                block_shape = []
                Contours = self.cursor.fetchall()
                for contour in Contours:
                    contour_dict[contour['ReferencedSOPInstanceUID']] = contour['ContourData']
                    # print(contour['ReferencedSOPInstanceUID'])
                    self.cursor.execute(query_for_image_plane_info, [contour['ReferencedSOPInstanceUID']])
                    image_info = self.cursor.fetchall()[0]
                    if not imagePatientOrientaion:
                        imagePatientOrientaion = image_info['ImageOrientationPatient'][0]
                    if not pixelSpacing:
                        pixelSpacing = image_info['PixelSpacing']
                    if not block_shape:
                        block_shape = (image_info['Rows'], image_info['Columns'])
                    imagePatientPosition[contour['ReferencedSOPInstanceUID']] = image_info['ImagePositionPatient']
                contour_block, roi_block = getContours(block_shape, contour_dict,
                                                       image_orientation=imagePatientOrientaion,
                                                       image_position=imagePatientPosition, pixel_spacing=pixelSpacing)
                ptv_dict[roi_name] = (contour_block,roi_block)
            else:
                self.cursor.execute(query_for_contour, (roi['id'], roi['fk_structureset_id_id']))
                contour_dict = {}
                imagePatientOrientaion = []
                imagePatientPosition = {}
                pixelSpacing = None
                block_shape = []
                Contours = self.cursor.fetchall()
                for contour in Contours:
                    contour_dict[contour['ReferencedSOPInstanceUID']] = np.array(contour['ContourData'].split(','))
                    #print(contour['ReferencedSOPInstanceUID'])
                    self.cursor.execute(query_for_image_plane_info, [contour['ReferencedSOPInstanceUID']])
                    image_info = self.cursor.fetchall()[0]
                    if not imagePatientOrientaion:
                        imagePatientOrientaion = image_info['ImageOrientationPatient'].split(',')
                    if not pixelSpacing:
                        pixelSpacing = image_info['PixelSpacing'].split(',')
                    if not block_shape:
                        block_shape = (image_info['Rows'], image_info['Columns'])

                    imagePatientPosition[contour['ReferencedSOPInstanceUID']] = image_info['ImagePositionPatient']


                #Change the definition of this function a little bit
                contour_block,roi_block = getContours(block_shape, contour_dict, image_orientation=imagePatientOrientaion,
                                            image_position=imagePatientPosition, pixel_spacing=pixelSpacing)

                oar_dict[roi_name] = (contour_block,roi_block)

        return ptv_dict,oar_dict

    def save_ovh(self,SourceOAR,TargetOAR,hist,StudyID):
        '''
        save ovh every time we have
        :param StudyID:
        :return:if the action is a success or not
        '''

    def save_sts(self,sts,StudyID):
        '''
        definition is the same as save_ovh
        :param sts: has the same data structure like the one in save_ovh
        :param StudyID:
        :return:
        '''
        pass

    #I don't know how to get this value, so we don't consider this right now
    def get_target_dose(self,studyID):
        '''
        get the target dose for this studyID
        :param studyID:
        :return:
        '''
        target_dose = getMeanTargetDose(ptv_roi_block, block_shape, dose_grid, 
                          DoseGridScaling, x0, y0, x_spacing, y_spacing, sopUID)
        pass


    def get_ovh(self,studyID):
        '''
        get the ovh of this study, if the study has two ptv or more, make it to be a single ptv-ovh
        :param studyID:
        :return: a dictionary, the key is the name of TargetOAR, the value is the histogram
        '''
        pass

    def get_sts(self,studyID):
        '''

        :param studyID:
        :return: a dictionary, the key is the name of TargetOAR, the value is the histogram
        '''


    def save_similarity(self,SourceStudyID,TargetStudyID,ovh_dis,sts_dis,td_dis,sim):
        '''
        save a instance of sim
        :param similarity_paris:
        :param StudyID:
        :return:
        '''
        pass

    def get_dbstudy_list(self,studyID):
        '''
        Get a list of the names of db study
        :param studyID: is to eliminate the study belongs to the same patient
        :return: a list
        '''
        self.cursor.execute(query_for_study_list,str(studyID))
        study_list = self.cursor.fetchall()
        return list(study_list)

    def fetch_similarity(self,studyID):
        '''
        find similarity of this studyID
        :param studyID:
        :return:dict
        {
            studyID:similarity
        }
        '''
        pass