
import MySQLdb
import numpy as np
import collections
from sts import getSTSHistogram
from ovh import getOVH
from DataFetcher import DataFetcher
from similarity_calculation import cal_dissimilarity_ovh,cal_dissimilarity_sts,cal_dissimilarity_td,cal_similarity

class AlgoManager():
    '''
    attribute
    self.StudyIDs
    '''
    def __init__(self):
        #create a datafetcher instance to fetch the data from the database
        self.data_fetcher = DataFetcher()




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

        for ptv_name,ptv_tuple in PTV.items():
            for oar_name,oar_tuple in OAR.items():
                #in the tuple, the first one is contour block and the second one is roi block





                ovh_hist,overlap_area = getOVH(oar_block,ptv_block, )
                sts_hist = sts.run(ptv_block,oar_block)
                self.data_fetcher.save_ovh(ptv_name,oar_name,ovh_hist,self.queryStudyID)
                self.data_fetcher.save_sts(ptv_name,oar_name,sts_hist,self.queryStudyID)


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
    def similarity_calculation(self):
        '''
        fetch ovh and STS features of other study
        calculate dissimilarity between features
        calculate similarity between study pair
        :return: dict with dissimiarity and similarity
        '''
        queryOVH = self.data_fetcher.get_ovh(self.queryStudyID)
        querySTS = self.data_fetcher.get_sts(self.queryStudyID)
        queryTD = self.data_fetcher.get_target_dose(self.queryStudyID)

        for studyID in self.DBStudy_list:
            dbOVH = self.data_fetcher.get_ovh(studyID)
            ovh_pairs = self.generate_pairs(queryOVH,dbOVH)

            dbSTS = self.data_fetcher.get_sts(studyID)
            sts_pairs = self.generate_pairs(querySTS,dbSTS)

            dbTD = self.data_fetcher.get_target_dose(studyID)
            td_pair = (queryTD,dbTD)

            ovh_dis = cal_dissimilarity_ovh(ovh_pairs)

            sts_dis = cal_dissimilarity_sts(sts_pairs)

            td_dis = cal_dissimilarity_td(td_pair)

            sim = cal_similarity(ovh_dis,sts_dis,td_dis,weight)

            self.data_fetcher.save_similarity(self.queryStudyID,studyID,ovh_dis,sts_dis,td_dis,sim)


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


