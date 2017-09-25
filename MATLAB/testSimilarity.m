%test 20 and 8
clear all;
query_patient_id=1;

conn = mysql('open','localhost','root');
mysql('use rt_hn_v5');

all_patient_ids = mysql('SELECT DISTINCT fk_patient_id FROM structure_set_roi_sequence_copy');
sample = randsample(all_patient_ids,5);

[queryDistance queryVolume queryROIList queryOverlap queryDistanceMean queryDoseMean queryDoseMax, queryAlpha, queryBeta, queryGamma] = mysql(horzcat('SELECT ovhDistance_ptv1, ovhVolume_ptv1, stdROIName, PercentageOverlap_ROI_Fraction_ptv1, distanceMean_ptv1, doseMean, doseMax, alpha_ptv1, beta_ptv1, gamma_ptv1 FROM structure_set_roi_sequence_copy WHERE fk_patient_id=',num2str(query_patient_id),' AND stdROIName NOT LIKE "brain" AND stdROIName NOT LIKE "heart" AND stdROIName NOT LIKE "liver" AND stdROIName NOT LIKE "lungRt" AND stdROIName NOT LIKE "lungLt" AND stdROIName NOT LIKE "lungTt" AND stdROIName NOT LIKE "tvc" AND stdROIName NOT LIKE "lensRt" AND stdROIName NOT LIKE "lensLt" AND stdROIName NOT LIKE "chiasm" AND stdROIName NOT LIKE "parotidTt" AND stdROIName NOT LIKE "ptv%"'));
ovhQuery = cell(length(queryROIList),1);

queryParameters=cell(length(queryROIList),5);
results=cell(length(queryROIList),2);

for roiIndex = 1:length(queryROIList)
    distance = regexp(queryDistance{roiIndex},',','split');
    distance{1}=distance{1}(2:length(distance{1}));
    distance{length(distance)}=distance{length(distance)}(1:length(distance{length(distance)})-1);
    distance=str2double(distance);
    volume = regexp(queryVolume{roiIndex},',','split');
    volume{1}=volume{1}(2:length(volume{1}));
    volume{length(volume)}=volume{length(volume)}(1:length(volume{length(volume)})-1);
    volume=str2double(volume);  
    ovhQuery{roiIndex} = [distance' volume'];
    queryParameters{roiIndex,1}=queryROIList(roiIndex);
    queryParameters{roiIndex,2}=queryOverlap(roiIndex);
    queryParameters{roiIndex,3}=queryDistanceMean(roiIndex);
    queryParameters{roiIndex,4}=queryDoseMax(roiIndex);
    queryParameters{roiIndex,5}=queryDoseMean(roiIndex);
    results{roiIndex,2}=queryROIList(roiIndex);
end;

%Select all patient ids other than the query patient id. Exclude all
%patients with no dose and structure set objects
%Exclude patient 49 (Very low dose prescription)
patient_ids=mysql(horzcat('SELECT DISTINCT fk_patient_id FROM structure_set_roi_sequence_copy WHERE fk_patient_id NOT LIKE "',num2str(query_patient_id),'" AND fk_patient_id NOT LIKE "49" AND fk_patient_id NOT LIKE "58" AND fk_patient_id NOT LIKE "61" AND fk_patient_id NOT LIKE "16" AND fk_patient_id NOT LIKE "11" AND fk_patient_id NOT LIKE "23" AND fk_patient_id NOT LIKE "57" AND ptv1 IS NOT NULL'));

%Initialize result set. Rows represent different patients, columns
%represent ROIs in the order given by queryROIList, and the third
%dimension represents parameters: 1-overlap; 2-dose mean; 3-dose max; 4-emd
%results=zeros(length(patient_ids),length(queryROIList),4);

for x = 1:length(queryROIList)
    results{x,1}=zeros(length(patient_ids),7);   
end

for pid = 1:length(patient_ids) %Cycle through all patients
    %Exclude brain, lung, liver, heart, etc. Also exclude lens and chiasm
    %because the ovh arrays are too small. Maybe include a mean distance
    %metric for them later?
    patient_id=patient_ids(pid);
    [searchROIList searchDistanceResult searchVolumeResult searchOverlap searchDistanceMean searchDoseMean searchDoseMax searchAlpha searchBeta searchGamma] = mysql(horzcat('SELECT stdROIName, ovhDistance_ptv1, ovhVolume_ptv1, PercentageOverlap_ROI_Fraction_ptv1, distanceMean_ptv1, doseMean, doseMax, alpha_ptv1, beta_ptv1, gamma_ptv1 FROM structure_set_roi_sequence_copy WHERE fk_patient_id=',num2str(patient_ids(pid)),' AND stdROIName NOT LIKE "brain" AND stdROIName NOT LIKE "heart" AND stdROIName NOT LIKE "liver" AND stdROIName NOT LIKE "lungRt" AND stdROIName NOT LIKE "lungLt" AND stdROIName NOT LIKE "lungTt" AND stdROIName NOT LIKE "tvc" AND stdROIName NOT LIKE "lensRt" AND stdROIName NOT LIKE "lensLt" AND stdROIName NOT LIKE "chiasm" AND stdROIName NOT LIKE "parotidTt" AND stdROIName NOT LIKE "ptv%"'));
    
    for roiIndex=1:length(searchROIList)
        temp=strcmp(queryROIList,searchROIList{roiIndex});%Check if this search ROI is present in the query ROI List
        if (~isempty(searchDistanceResult))&&(any(temp))%ensure that the ROI is part of the 0bject ROI List
            %Find position of the ROI in the query list
            queryROIListPosition = find(temp);
            %disp(horzcat(num2str(pid),' ',searchROIList{roiIndex},' ',num2str(queryROIListPosition)));
            clear temp;
            clear temp2;            
       
            %********************************* CALCULATE EMD *********************************
            searchDistance = regexp(searchDistanceResult{roiIndex},',','split');
            searchDistance{1}=searchDistance{1}(2:length(searchDistance{1}));
            searchDistance{length(searchDistance)}=searchDistance{length(searchDistance)}(1:length(searchDistance{length(searchDistance)})-1);
            searchDistance=str2double(searchDistance);

            searchVolume = regexp(searchVolumeResult{roiIndex},',','split');
            searchVolume{1}=searchVolume{1}(2:length(searchVolume{1}));
            searchVolume{length(searchVolume)}=searchVolume{length(searchVolume)}(1:length(searchVolume{length(searchVolume)})-1);
            searchVolume=str2double(searchVolume);

            searchElement=[searchDistance' searchVolume'];
            w1=ones(length(ovhQuery{queryROIListPosition}),1);
            w2=ones(length(searchElement),1);
            [x fval] = emd(ovhQuery{queryROIListPosition}, searchElement, w1, w2, @gdf);
            %**********************************************************************************
            
            %*********************** CALCULATE ORIENTATION SIM ********************************
            sim = (1+queryAlpha(queryROIListPosition)*searchAlpha(roiIndex)+queryBeta(queryROIListPosition)*searchBeta(roiIndex)+queryGamma(queryROIListPosition)*searchGamma(roiIndex))/2;
            %**********************************************************************************
        
        results{queryROIListPosition,1}(pid,1)=patient_ids(pid);
        results{queryROIListPosition,1}(pid,2)=fval;
        results{queryROIListPosition,1}(pid,3)=sim;
        results{queryROIListPosition,1}(pid,4)=searchOverlap(roiIndex);
        results{queryROIListPosition,1}(pid,5)=searchDistanceMean(roiIndex);
        results{queryROIListPosition,1}(pid,6)=searchDoseMax(roiIndex);
        results{queryROIListPosition,1}(pid,7)=searchDoseMean(roiIndex);
        
        end

    end
   
end

% emdValues=results(:,:,4);
% emdMax=max(emdValues,[],2);
% emdMean=mean(emdValues,2);
% emdStd=std(emdValues,0,2);
% [~,sortedIndices]=sort(emdMax);
% 
% queryDoseMean=queryDoseMean';
% queryDoseMax=queryDoseMax';
% queryOverlap=queryOverlap';
% 
% for v=1:5
%    if any((queryOverlap<results(sortedIndices(v),:,1))&(queryDoseMean>results(sortedIndices(v),:,2)))
%        disp(horzcat('Patient ',num2str(patient_ids(sortedIndices(v)))));
%        roiIndices=find((queryOverlap<results(sortedIndices(v),:,1))&(queryDoseMean>results(sortedIndices(v),:,2)));
%        for w=1:length(roiIndices)
%            disp(queryROIList{roiIndices(w)});
%            disp(horzcat('Query Overlap: ',num2str(queryOverlap(roiIndices(w))),' Query Dose Mean: ',num2str(queryDoseMean(roiIndices(w)))));
%            disp(horzcat('Search Overlap: ',num2str(results(sortedIndices(v),roiIndices(w),1)),' Search Dose Mean: ',num2str(results(sortedIndices(v),roiIndices(w),2))));
%        end
%    end
% end
% disp(horzcat('Minimum emd: ',num2str(min(emdMax))));    

mysql('close');
clear conn;