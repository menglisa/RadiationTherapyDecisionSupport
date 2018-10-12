
import MySQLdb
import numpy as np
import collections
from AlgoEngine.sts import getSTSHistogram
from AlgoEngine.ovh import getOVH
from AlgoEngine.DataFetcher import DataFetcher
from AlgoEngine.similarity import getOVHEmd,getSTSEmd
import pdb
from collections import defaultdict
try:
    from sts import getSTSHistogram
    from ovh import getOVH
    from DataFetcher import DataFetcher
    from similarity_calculation import cal_dissimilarity_ovh,cal_dissimilarity_sts,cal_dissimilarity_td,cal_similarity
except ImportError: # Used for running notebooks in `similarity` folder
    import sys
    sys.path.append('..')
    from AlgoEngine.sts import getSTSHistogram
    from AlgoEngine.ovh import getOVH
    from AlgoEngine.DataFetcher import DataFetcher
    # from AlgoEngine.similarity_calculation import cal_dissimilarity_ovh,cal_dissimilarity_sts,cal_dissimilarity_td,cal_similarity

class AlgoManager():
    '''
    attribute
    self.StudyIDs
    '''
    def __init__(self, studyID, database_username, database_password, use_ssh=True):
        #create a datafetcher instance to fetch the data from the database
        self.data_fetcher = DataFetcher(database_username, database_password, use_ssh)

        self.n_bins = 10

        self.queryStudyID = studyID




    def feature_extraction(self):
        '''
        call ovh, sts and td to get the ovh sts and td features
        :param StudyID:
        :return ovh: a histogram of ovh feature
        :return sts: a histogram of sts feature
        :return td: target dose
        '''
        #Both PTV and OAR are dictionary
        PTV,OAR = self.data_fetcher.get_contours(self.queryStudyID)
        
        # Check that PTV has been found
        assert len(PTV.keys()) > 0 , "PTV NOT FOUND"

        row_spacing, column_spacing, slice_thickness = self.data_fetcher.get_spacing(self.queryStudyID)
        pixel_spacing = self.data_fetcher.get_pixel_spacing(self.queryStudyID)

        for ptv_name,ptv_tuple in PTV.items():
            for oar_name,oar_tuple in OAR.items():
                #in the tuple, the first one is contour block and the second one is roi block
                print("process the pair")
                oar_contour_block = oar_tuple[0]
                oar_roi_block = oar_tuple[1]

                ptv_contour_block = ptv_tuple[0]
                ptv_roi_block = ptv_tuple[1]

                bin_vals, bin_amts = getOVH(oar_roi_block, ptv_contour_block, ptv_roi_block, pixel_spacing,
                            row_spacing, column_spacing, slice_thickness, self.n_bins)

                ovh_hist = (bin_vals, bin_amts)

                # print("Get ovh {}".format(ovh_hist))
                print("OVH Done")
                elevation_bins, distance_bins, azimuth_bins, amounts = getSTSHistogram(ptv_roi_block, oar_roi_block, self.n_bins)
                sts_hist = (elevation_bins, distance_bins, azimuth_bins, amounts)

                print("STS Done")
                # print("Get Sts {}".format(sts_hist))

                self.data_fetcher.save_ovh(ptv_name,oar_name,ovh_hist,self.queryStudyID)
                self.data_fetcher.save_sts(ptv_name,oar_name,sts_hist,self.queryStudyID)

                print("Saved OVH and STS")
        pass

    def generate_pairs(self,queryStudy,dbStudy):
        '''
        match the queryStudy with dbStudy to generate pairs
        :param queryStudy: a dictionary, key is the name of OAR, the value is the histogram
        :param dbStudy: a dictionary, key is the name of OAR, the value is the histogram
        :return:
        {
            oar_name: (hist_query,hist_db)
        }
        '''
        queryKeys = set(queryStudy.keys())
        dbKeys = set(dbStudy.keys())
        mergedKeys = queryKeys.intersection(dbKeys)
        mergedDict = defaultdict()
        for key in mergedKeys:
            mergedDict[key] = (queryStudy[key],dbStudy[key])

        return mergedDict

    def similarity_calculation(self):
        '''
        fetch ovh and STS features of other study
        calculate dissimilarity between features
        calculate similarity between study pair
        :return: dict with dissimiarity and similarity
        '''
        queryOVH = self.data_fetcher.get_ovh(self.queryStudyID)
        querySTS = self.data_fetcher.get_sts(self.queryStudyID)

        for studyID in self.DBStudy_list:
            dbOVH = self.data_fetcher.get_ovh(studyID)
            ovh_pairs = self.generate_pairs(queryOVH,dbOVH)

            dbSTS = self.data_fetcher.get_sts(studyID)
            sts_pairs = self.generate_pairs(querySTS,dbSTS)

            keys = ovh_pairs.keys()
            for key in keys:
                ovh_item = ovh_pairs[key]
                ovh_dis = getOVHEmd(ovh_item[0][0],ovh_item[0][1],ovh_item[1][0],ovh_item[1][1])
                sts_item = sts_pairs[key]
                sts_dis = getSTSEmd(sts_item)
                self.data_fetcher.save_similarity(studyID,0,ovh_dis,sts_dis,key,self.queryStudyID)


    #The entrance of the programe
    def run(self,StudyID):
        #extract OVH and STS for new case
        #store the OVH and STS
        #fetch OVH and STS of other cases
        #Do the similarity calculation
        #Save the result to database


        #queryStudyID
        self.queryStudyID = StudyID
        #Store the StudyID of all DB studies for future similarity calculation
        self.DBStudy_list = self.data_fetcher.get_dbstudy_list(self.queryStudyID)

        #calculate ovh,sts and save it to database
        self.feature_extraction()

        self.similarity_calculation()


