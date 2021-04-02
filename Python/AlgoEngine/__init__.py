
import MySQLdb
import numpy as np
import collections
from collections import defaultdict
try:
    from sts import getSTSHistogram
    from ovh import getOVH
    from DataFetcher import DataFetcher
    from similarity import getOVHEmd,getSTSEmd
    from similarity_calculation import cal_dissimilarity_ovh,cal_dissimilarity_sts,cal_dissimilarity_td,cal_similarity
except ImportError: # Used for running notebooks in `similarity` folder
    import sys
    sys.path.append('..')
    from .sts import getSTSHistogram
    from .ovh import getOVH
    from .DataFetcher import DataFetcher
    from .similarity import getOVHEmd,getSTSEmd
    # from AlgoEngine.similarity_calculation import cal_dissimilarity_ovh,cal_dissimilarity_sts,cal_dissimilarity_td,cal_similarity

class AlgoManager():
    '''
    attribute
    self.StudyIDs
    '''
    def __init__(self, studyID, use_ssh=True):
        #create a datafetcher instance to fetch the data from the database
        self.data_fetcher = DataFetcher(use_ssh)

        self.n_bins = 10

        self.queryStudyID = studyID

    def get_contours_by_id(self, roi_index):
        return self.data_fetcher.get_contours_by_id(self.queryStudyID, roi_index)

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
                oar_contour_block = oar_tuple[0][0]
                oar_roi_block = oar_tuple[0][1]

                ptv_contour_block = ptv_tuple[0][0]
                ptv_roi_block = ptv_tuple[0][1]
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
            oar_id: (hist_query,hist_db)
        }
        '''
        queryKeys = set(queryStudy.keys())
        dbKeys = set(dbStudy.keys())
        mergedKeys = queryKeys.intersection(dbKeys)
        mergedDict = defaultdict()
        for key in mergedKeys:
            query_tuple = []
            for block in queryStudy[key]:
                # process amounts (2d array) separately
                if "]" in block:
                    query_values = block.replace("]", " ").replace("[", " ").replace(",", " ").split(" ")
                    query_array = np.zeros(shape=((self.n_bins ** 3 * 4)), dtype=np.float64)
                    
                    count = 0
                    for i, val in enumerate(query_values):
                        if val:
                            query_array[count] = float(val.strip())
                            count +=1
                    query_array = query_array.reshape((self.n_bins ** 3, 4))
                    if count != self.n_bins ** 3 * 4:
                        import pdb ; pdb.set_trace()
                    assert count == self.n_bins ** 3 * 4, "invalid parsed STS values"
                else:
                    query_values = block.split(",")
                    query_array = np.zeros(shape=(len(query_values)), dtype=np.float64)
                    for i, val in enumerate(query_values):
                        query_array[i] = float(val)
                query_tuple.append(query_array)
            
            historical_tuple = []
            for block in dbStudy[key]:
                # process amounts (2d array) separately
                if "]" in block:
                    query_values = block.replace("]", " ").replace("[", " ").replace(",", " ").split(" ")
                    query_array = np.zeros(shape=((self.n_bins ** 3 * 4)), dtype=np.float64)
                    
                    count = 0
                    for i, val in enumerate(query_values):
                        if val:
                            query_array[count] = float(val.strip())
                            count +=1
                    query_array = query_array.reshape((self.n_bins ** 3, 4))
                    assert count == self.n_bins ** 3 * 4, "invalid parsed STS values"
                else:
                    query_values = block.split(",")
                    query_array = np.zeros(shape=(len(query_values)), dtype=np.float64)
                    for i, val in enumerate(query_values):
                        query_array[i] = float(val)
                historical_tuple.append(query_array)

            mergedDict[key] = (query_tuple, historical_tuple)

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

        self.DBStudy_list = self.data_fetcher.get_dbstudy_list(self.queryStudyID)

        for studyID in self.DBStudy_list:
            historical_id = studyID["id"]
            dbOVH = self.data_fetcher.get_ovh(str(historical_id))
            ovh_pairs = self.generate_pairs(queryOVH,dbOVH)

            dbSTS = self.data_fetcher.get_sts(str(historical_id))
            
            sts_pairs = self.generate_pairs(querySTS,dbSTS)

            keys = ovh_pairs.keys()
            if len(keys) > 0:
                print("Processing similar pairs")

            for key in keys:
                ovh_item = ovh_pairs[key]
                ovh_dis = getOVHEmd(ovh_item[0][0],ovh_item[0][1],ovh_item[1][0],ovh_item[1][1])
                sts_item = sts_pairs[key]
                sts_dis = getSTSEmd(sts_item[0][3], sts_item[1][3])

                # Get PTV target dose
                query_target_dose = self.data_fetcher.get_target_dose(self.queryStudyID, int(key.split(" ")[1]))
                historical_target_dose = self.data_fetcher.get_target_dose(historical_id, int(key.split(" ")[1]))

                self.data_fetcher.save_similarity(str(historical_id), query_target_dose - 
                        historical_target_dose, str(ovh_dis), str(sts_dis), key.split(" ")[0], 
                    key.split(" ")[-1], str(historical_id), self.queryStudyID)


    #The entrance of the program
    def run(self):
        #extract OVH and STS for new case
        #store the OVH and STS
        #fetch OVH and STS of other cases
        #Do the similarity calculation
        #Save the result to database

        #Store the StudyID of all DB studies for future similarity calculation
        self.DBStudy_list = self.data_fetcher.get_dbstudy_list(self.queryStudyID)

        #calculate ovh,sts and save it to database
        self.feature_extraction()

        self.similarity_calculation()


