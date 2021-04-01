import MySQLdb
from sshtunnel import SSHTunnelForwarder
import numpy as np
from collections import defaultdict, OrderedDict

# Imports for STS / OVH / etc
import sys
sys.path.append('..')
try:
    from .utils import *
    from .settings import * 
    from .sts import getSTSHistogram
    from .ovh import getOVH
    from .similarity import getSTSEmd, getOVHEmd, getTDDistance
except:
    from AlgoEngine.utils import *
    from AlgoEngine.settings import * 
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

    def __init__(self, use_ssh=True):

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
            self.server = SSHTunnelForwarder((ssh_hostname, ssh_port), ssh_username=ssh_username,
                                        ssh_password=ssh_password,
                                            remote_bind_address=('127.0.0.1', 3306))
            self.server.start()
            port = self.server.local_bind_port

        self.connection = MySQLdb.connect(read_default_file='/etc/mysql/my.cnf', autocommit=True)

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

    def __get_contours(self, roi):
        roi_id = roi['roi_id_id']
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

        self.pixel_spacing = pixelSpacing
        return getContours(block_shape, contour_dict, image_orientation=imagePatientOrientaion,
                                    image_position=imagePatientPosition, pixel_spacing=pixelSpacing), imagePatientPosition


    def get_contours_by_id(self, studyID, roi_index):
        self.cursor.execute(query_for_roi_list,studyID)
        rois = self.cursor.fetchall()
        contour_dict = {}
        image_position = None
        print("Starting contour")
        for roi in rois:
            roi_id = roi['roi_id_id']
            if roi_id != roi_index:
                continue
            contours, image_position = self.__get_contours(roi)
            contour_dict[roi_id] = contours
        return contour_dict, image_position

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
            roi_id = roi['roi_id_id']
            contour_block, roi_block = self.__get_contours(roi)

            # Checks for PTVs using ROI name -> if it contains PTV we assume it is a PTV
            self.cursor.execute(query_for_roi_name, (roi_id,))
            roi_name = self.cursor.fetchone()['ROIName']
            roi_interpretation = roi["roi_interpretation"]
            if "PTV" in roi_interpretation or "CTV" in roi_interpretation:
                ptv_dict[roi_name] = (contour_block,roi_block)
            elif "none" in roi_interpretation.lower():
                if "ptv" in roi_name.lower():
                    ptv_dict[roi_name] = (contour_block,roi_block)
                else:
                    oar_dict[roi_name] = (contour_block,roi_block)
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
        query_ovh_exists = "SELECT * from ovh where fk_study_id_id = %s and ptv_id = %s and oar_id = %s"
        
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

        # check if ovh already exists, delete if it does
        rows_count = self.cursor.execute(query_ovh_exists, (studyID, ptv_id, oar_id))
        if rows_count > 0:
            query_delete = "DELETE from ovh where fk_study_id_id = %s and ptv_id = %s and oar_id = %s"
            self.cursor.execute(query_delete, (studyID, ptv_id, oar_id))

        binValue = ','.join(str(point) for point in ovh_hist[0])
        binAmount = ','.join(str(point) for point in ovh_hist[1])

        self.cursor.execute(query_insert_ovh,[binValue, binAmount, 20,ptv_id, oar_id, studyID])

    def save_sts(self,ptv_name,oar_name,sts_hist, study_id):
        '''
        definition is the same as save_ovh
        :param sts: has the same data structure like the one in save_ovh
        :param StudyID:
        :return:
        '''
        query_insert_sts = 'INSERT INTO sts (elevation_bins,distance_bins,azimuth_bins,amounts,ptv_id,oar_id,fk_study_id_id) VALUES (%s,%s,%s,%s,%s,%s,%s)'
        query_oar_id = 'SELECT id from oar_dictionary WHERE ROIName = %s'
        query_sts_exists = "Select * from sts where fk_study_id_id = %s and ptv_id = %s and oar_id = %s"

        self.cursor.execute(query_oar_id, [ptv_name])
        ptv_id = self.cursor.fetchone()['id']
        self.cursor.execute(query_oar_id, [oar_name])
        oar_id = self.cursor.fetchone()['id']
    
        # check if sts already exists, delete if it does
        rows_count = self.cursor.execute(query_sts_exists, (study_id, ptv_id, oar_id))
        if rows_count > 0:
            query_delete = "DELETE from sts where fk_study_id_id = %s and ptv_id = %s and oar_id = %s"
            self.cursor.execute(query_delete, (study_id, ptv_id, oar_id))

        elevation = ",".join(str(point) for point in sts_hist[0])
        azimuth = ",".join(str(point) for point in sts_hist[1])
        distance = ",".join(str(point) for point in sts_hist[2])
        amounts = ",".join(str(point) for point in sts_hist[3])

        self.cursor.execute(query_insert_sts, [elevation, distance, azimuth, amounts ,ptv_id,oar_id,study_id])


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
            ovhDict[str(row['oar_id']) + " " + str(row['ptv_id'])] = (row['bin_value'],row['bin_amount'])

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
            stsDict[str(row['oar_id']) + " " + str(row['ptv_id'])] = (row['elevation_bins'],row['distance_bins'],
                row['azimuth_bins'],row['amounts'])

        return stsDict

    def save_similarity(self,
            DBStudyID,
            TDSimilarity,
            OVHDisimilarity,
            STSDisimilarity,
            TargetOAR_id,
            TargetPTV_id,
            fk_study_id_id_query,
            fk_study_id_id_historical):

        '''
        save a instance of sim
        :param similarity_paris:
        :param StudyID:
        :return:
        '''
        insert_similarity = 'INSERT INTO similarity (DBStudyID, TD_dissimilarity, \
            OVH_dissimilarity, STS_dissimilarity, TargetOAR_id, TargetPTV_id, \
            fk_study_id_1_id, fk_study_id_2_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'

        self.cursor.execute(insert_similarity,
                [DBStudyID, TDSimilarity, OVHDisimilarity, STSDisimilarity, TargetOAR_id, TargetPTV_id,
                fk_study_id_id_query, fk_study_id_id_historical])

    def get_target_dose(self, study_id, dicom_roi_id):
        """
        Parameters
        ----------

        dicom_roi_id : integer
            corresponds to the DICOM ROI id of a given RTROI
        """

        # Conversion from roi to rt_roi (original in oar_dictionary to rt roi contour)
        query_roi_id_from_rtroi = "SELECT id from rt_rois where roi_id_id= %s and fk_study_id_id = %s"
        self.cursor.execute(query_roi_id_from_rtroi, [dicom_roi_id, study_id])
        roi = self.cursor.fetchone()
        roi_id = roi["id"]
        


        query_target_dose = "SELECT DVHMeanDose from rt_dvh where DVHReferencedROI_id = %s and fk_study_id_id = %s"
        self.cursor.execute(query_target_dose, [roi_id, study_id])

        data = self.cursor.fetchall()
        

        for row in data:
            return float(row["DVHMeanDose"])

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
