import MySQLdb
from sshtunnel import SSHTunnelForwarder
from AlgoEngine.utils import *
import numpy as np
import pdb
from collections import defaultdict, OrderedDict

# Imports for STS / OVH / etc
import sys
sys.path.append('..')
from AlgoEngine.utils import *
import AlgoEngine.settings as settings
from AlgoEngine.sts import getSTSHistogram
from AlgoEngine.ovh import getOVH
from AlgoEngine.similarity import getSTSEmd, getOVHEmd, getTDDistance

import re

#in order to use this AlgoEngine separately, we build this datafetcher by using MySQLdb instead of Django ORM
#it can also be implemented with Django ORM

query_for_study_list = 'SELECT id from studies WHERE id NOT IN (%s)'
query_for_roi_list = 'SELECT * from rt_rois WHERE fk_study_id_id = %s'
query_for_roi_name = 'SELECT ROIName from oar_dictionary WHERE id= %s'
query_for_contour = 'SELECT * from rt_contour WHERE fk_roi_id_id = %s AND fk_structureset_id_id = %s'
query_for_image_plane_info = 'SELECT * from ct_images WHERE SOPInstanceUID = %s'
class DataFetcher():

    def __init__(self, database_username=settings.database_username, 
            database_password=settings.database_password, use_ssh=True):

        """
        Initializes datafetcher by building SSH connection, and saving the connection cursor.
        Then, funnctions to load data are prepared using the SSH tunnel.

        Parameters
        ----------
        database_username : str
            Username for mysql database
        database_password : str
            password for mysql database
        use_ssh : bool
            whether to use remote db or local db (false)
        """
        port = 3306
        if use_ssh:
            self.server = SSHTunnelForwarder((settings.ssh_hostname, settings.ssh_port), ssh_username=settings.ssh_username,
                                        ssh_password=settings.ssh_password,
                                            remote_bind_address=('127.0.0.1', 3306))
            self.server.start()
            port = self.server.local_bind_port

        self.connection = MySQLdb.connect('127.0.0.1',port=port,
                          user = database_username,
                          passwd = database_password,
                          db = settings.database_name, 
                          autocommit=True)

        self.cursor = self.connection.cursor(MySQLdb.cursors.DictCursor)

        print("Finished Setting up database access")


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

    def get_spacing(self, studyID):
        """
        Returns the row spacing and column spacing from the DICOM field `PixelSpacing`, and
        returns the slice thickness from the DICOM filed `SliceThickness` from the SQL
        database.

        Parameters
        ----------
        StudyID : string
            ID in the new dataset. Typically a single number, e.g. `'1'` or `'2'`.

        Returns
        -------
        row_spacing : float
            Row spacing for `StudyID`

        column_spacing : float
            Column spacing for `StudyID`

        slice_thickness : float
            Slice thickness for `StudyID`

        """
        self.cursor.execute(query_for_roi_list,studyID)
        rois = self.cursor.fetchall()
        row_spacing = -1
        column_spacing = -1
        slice_thickness = -1

        roi = rois[0]

        self.cursor.execute(query_for_contour, (roi['id'], roi['fk_structureset_id_id']))
        Contours = self.cursor.fetchall()

        contour = Contours[0]

        self.cursor.execute(query_for_image_plane_info, [contour['ReferencedSOPInstanceUID']])
        image_info = self.cursor.fetchall()[0]
        spacing_array = np.array(image_info['PixelSpacing'].split(','), dtype=np.float32)

        row_spacing = spacing_array[0]
        column_spacing = spacing_array[1]
        slice_thickness = float(image_info['SliceThickness'])

        return row_spacing, column_spacing, slice_thickness

    def get_pixel_spacing(self, studyID):
        return self.pixel_spacing


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

        Parameters
        ----------
        StudyID : string
            ID in the new dataset. Typically a single number, e.g. `'1'` or `'2'`.

        Returns
        --------
        ptv_dict : List of Dict
        a list of dictionaries, the first dictionary contains ptv and the second contains PTV
            in the dictionary the key is the name of ROI, the value is the contour block.

        oar_dict : list of Dict
            a list of dictionaries, the first dictionary contains ptv and the second contains OAR
            in the dictionary the key is the name of ROI, the value is the contour block.
        '''
        self.cursor.execute(query_for_roi_list,studyID)
        rois = self.cursor.fetchall()
        ptv_dict = {}
        oar_dict = {}

        print("Starting contour")
        for roi in rois:
            roi_id = roi['ROIName_id']
            self.cursor.execute(query_for_contour, (roi['id'], roi['fk_structureset_id_id']))
            contour_dict = {}
            imagePatientOrientaion = {}
            imagePatientPosition = {}
            pixelSpacing = {}
            block_shape = []
            Contours = self.cursor.fetchall()
            for contour in Contours:
                contour_array = np.array(contour['ContourData'].split(','), dtype=np.float32)
                contour_array = contour_array.reshape(contour_array.shape[0] // 3 , 3)

                contour_dict[contour['ReferencedSOPInstanceUID']] = contour_array
                self.cursor.execute(query_for_image_plane_info, [contour['ReferencedSOPInstanceUID']])
                image_info = self.cursor.fetchall()[0]
                imagePatientOrientaion[contour['ReferencedSOPInstanceUID']] = np.array(image_info['ImageOrientationPatient'].split(','), dtype=np.float32)
                
                spacing_array = np.array(image_info['PixelSpacing'].split(','), dtype=np.float32)
                pixelSpacing[contour['ReferencedSOPInstanceUID']] = spacing_array

                if not block_shape:
                    block_shape = (image_info['Rows'], image_info['Columns'])

                imagePatientPosition[contour['ReferencedSOPInstanceUID']] = np.array(image_info['ImagePositionPatient'].split(','), dtype=np.float32)


            #Change the definition of this function a little bit
            self.pixel_spacing = pixelSpacing
            contour_block,roi_block = getContours(block_shape, contour_dict, image_orientation=imagePatientOrientaion,
                                        image_position=imagePatientPosition, pixel_spacing=pixelSpacing)

            # Checks for PTVs using ROI name -> if it contains PTV we assume it is a PTV
            self.cursor.execute(query_for_roi_name, (roi_id,))
            roi_name = self.cursor.fetchone()['ROIName']
            if "ptv" in roi_name.lower():
                ptv_dict[roi_name] = (contour_block,roi_block)
            else:
                oar_dict[roi_name] = (contour_block,roi_block)

        print("Done with all")
        return ptv_dict,oar_dict

    def get_SOPIDs(self, StudyID):
        """
        Returns a dict of all the SOPIDs for a given StudyID.

        Parameters
        -----------
        StudyID : String 
            The StudyID to get SOPs for 

        Returns
        -------
        SOPIDs : Ordered Dict
            Ordered by z variable, key is Z var, value is SOP ID.


        """
        SOPIDs = OrderedDict()

        # Fetch from SQL and process here
        

        SOPIDs = OrderedDict(sorted(SOPIDs.items(), key=lambda t : t[0], reverse=True)) # Needed to sort into correct position
        return SOPIDs


    def save_ovh(self,ptv_name,oar_name,ovh_hist,studyID):
        '''
        save ovh every time we have
        :param StudyID:
        :return:if the action is a success or not
        '''
        
        query_insert_ovh = 'INSERT INTO ovh (bin_value, bin_amount, OverlapArea, ptv_id, oar_id, fk_study_id_id) VALUES (%s,%s,%s,%s,%s,%s)'
        query_oar_id = 'SELECT id from oar_dictionary WHERE ROIName = %s'
        
        # used because pymysql expects list params, not strings 
        # even for only one string
        if type(ptv_name) is not list:
            ptv_name = [ptv_name]
            
        if type(oar_name) is not list:
            oar_name = [oar_name]
        
        self.cursor.execute(query_oar_id, ptv_name)
        ptv_id = self.cursor.fetchone()["id"]
        self.cursor.execute(query_oar_id, oar_name)
        oar_id = self.cursor.fetchone()["id"]
        binValue = ','.join(str(point) for point in ovh_hist[0])
        binAmount = ','.join(str(point) for point in ovh_hist[1])

        self.cursor.execute(query_insert_ovh,[binValue, binAmount, 20,ptv_id, oar_id, studyID])


    def save_sts(self,ptv_name,oar_name,sts_hist,StudyID):
        '''
        definition is the same as save_ovh
        :param sts: has the same data structure like the one in save_ovh
        :param StudyID:
        :return:
        '''
        query_insert_sts = 'INSERT INTO sts (elevation_bins,distance_bins,azimuth_bins,amounts,ptv_id,oar_id,fk_study_id_id) VALUES (%s,%s,%s,%s,%s,%s,%s)'
        query_oar_id = 'SELECT id from oar_dictionary WHERE ROIName = %s'

        self.cursor.execute(query_oar_id, [ptv_name])
        ptv_id = self.cursor.fetchone()['id']
        self.cursor.execute(query_oar_id, [oar_name])
        oar_id = self.cursor.fetchone()['id']
        elevation = ",".join(str(point) for point in sts_hist[0])
        azimuth = ",".join(str(point) for point in sts_hist[1])
        distance = ",".join(str(point) for point in sts_hist[2])
        amounts = ",".join(str(point) for point in sts_hist[3])

        self.cursor.execute(query_insert_sts, [elevation, distance, azimuth, amounts ,ptv_id,oar_id,StudyID])


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
        query_for_ovh = 'SELECT * from ovh WHERE fk_study_id_id = %s'

        self.cursor.execute(query_for_ovh,studyID)

        data = self.cursor.fetchall()
        #return it to be a dictionary, the key is the name of oar , the data is the histogram

        ovhDict = defaultdict()

        for row in data:
            ovhDict[row['OAR_id']] = (row['binValue'],row['binAmount'])

        return ovhDict

    def get_sts(self,studyID):
        '''

        :param studyID:
        :return: a dictionary, the key is the name of TargetOAR, the value is the histogram
        '''
        query_for_sts = 'SELECT * from sts WHERE fk_study_id_id = %s'

        self.cursor.execute(query_for_sts,studyID)

        data = self.cursor.fetchall()

        stsDict = defaultdict()

        for row in data:
            stsDict[row['OAR_id']] = (row['elevation_bins'],row['distance_bins'],row['azimuth_bins'],row['amounts'])

        return stsDict

    def save_similarity(self,DBStudyID,Similarity,OVHDisimilarity,STSDisimilarity,TargetOAR,fk_study_id_id):

        '''
        save a instance of sim
        :param similarity_paris:
        :param StudyID:
        :return:
        '''
        insert_similarity = 'INSERT INTO similarity(DBStudyID, Similarity,OVHDisimilarity,STSDisimilarity, TargetOAR, fk_study_id_id VALUES (%s,%s,%s,%s,%s,%s)'
        self.cursor.execute(insert_similarity,DBStudyID,Similarity,OVHDisimilarity,STSDisimilarity,TargetOAR,fk_study_id_id)


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
