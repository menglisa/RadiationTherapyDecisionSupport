import MySQLdb
import settings

#in order to use this AlgoEngine separately, we build this datafetcher by using MySQLdb instead of Django ORM
#it can also be implemented with Django ORM

class DataFetcher():
    def __init__(self):
        #build connection
        #save the connection with the class
        self.db_connection = MySQLdb.connect(settings.hostname, settings.username,settings.password, settings.database)

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

    def get_target_dose(self,studyID):
        '''
        get the target dose for this studyID
        :param studyID:
        :return:
        '''

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
        pass

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