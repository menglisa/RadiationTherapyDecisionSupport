clear all;

conn = mysql('open','localhost','root');
mysql('use rt_hn_v6');
roi = 'mandible';

allPatients = [1 3 4 5 7 8 11 12 14 15 16 17 18 19 20 22 23 24 25 27 29 30 31 32 33 34 35 37 38 40 41 45 47 48 49 50 52 53 54 55 56 57 58 60 62 63 65 67 68 69 70 71];
parotidRtIDs = mysql(horzcat('SELECT DISTINCT fk_patient_id FROM structure_set_roi_sequence_copy WHERE stdROIName="parotidRt"'));
parotidLtIDs = mysql(horzcat('SELECT DISTINCT fk_patient_id FROM structure_set_roi_sequence_copy WHERE stdROIName="parotidLt"'));
cochleaRtIDs = mysql(horzcat('SELECT DISTINCT fk_patient_id FROM structure_set_roi_sequence_copy WHERE stdROIName="cochleaRt"'));
cochleaLtIDs = mysql(horzcat('SELECT DISTINCT fk_patient_id FROM structure_set_roi_sequence_copy WHERE stdROIName="cochleaLt"'));
mandible = mysql(horzcat('SELECT DISTINCT fk_patient_id FROM structure_set_roi_sequence_copy WHERE stdROIName="mandible"'));
tongue = mysql(horzcat('SELECT DISTINCT fk_patient_id FROM structure_set_roi_sequence_copy WHERE stdROIName="tongue"'));

selectedPatients = intersect(intersect(intersect(intersect(intersect(intersect(parotidRtIDs,parotidLtIDs),cochleaLtIDs),cochleaRtIDs),mandible),tongue),allPatients);

for i = 1:1
   
    selectedPatientsString = sprintf('%.0f,' , selectedPatients);
    selectedPatientsString = selectedPatientsString(1:end-1);
    [dbmean1, dbstd1, dbmode1, dbmedian1, dbskewness1, dbmax1, dbmin1, overlap1, alpha1, beta1, gamma1, doseMean1] = mysql(horzcat('SELECT DistanceMean_ptv1, DistanceStdDev_ptv1, DistanceMode_ptv1, DistanceMedian_ptv1, DistanceSkewness_ptv1, DistanceMax_ptv1, DistanceMin_ptv1, PercentageOverlap_ROI_Fraction_ptv1, alpha_ptv1, beta_ptv1, gamma_ptv1, doseMean FROM structure_set_roi_sequence_copy WHERE stdROIName="parotidRt" AND fk_patient_id IN (',selectedPatientsString,')'));
    [dbmean2, dbstd2, dbmode2, dbmedian2, dbskewness2, dbmax2, dbmin2, overlap2, alpha2, beta2, gamma2, doseMean2] = mysql(horzcat('SELECT DistanceMean_ptv1, DistanceStdDev_ptv1, DistanceMode_ptv1, DistanceMedian_ptv1, DistanceSkewness_ptv1, DistanceMax_ptv1, DistanceMin_ptv1, PercentageOverlap_ROI_Fraction_ptv1, alpha_ptv1, beta_ptv1, gamma_ptv1, doseMean FROM structure_set_roi_sequence_copy WHERE stdROIName="parotidLt" AND fk_patient_id IN (',selectedPatientsString,')'));
    [dbmean3, dbstd3, dbmode3, dbmedian3, dbskewness3, dbmax3, dbmin3, overlap3, alpha3, beta3, gamma3, doseMean3] = mysql(horzcat('SELECT DistanceMean_ptv1, DistanceStdDev_ptv1, DistanceMode_ptv1, DistanceMedian_ptv1, DistanceSkewness_ptv1, DistanceMax_ptv1, DistanceMin_ptv1, PercentageOverlap_ROI_Fraction_ptv1, alpha_ptv1, beta_ptv1, gamma_ptv1, doseMean FROM structure_set_roi_sequence_copy WHERE stdROIName="cochleaRt" AND fk_patient_id IN (',selectedPatientsString,')'));
    [dbmean4, dbstd4, dbmode4, dbmedian4, dbskewness4, dbmax4, dbmin4, overlap4, alpha4, beta4, gamma4, doseMean4] = mysql(horzcat('SELECT DistanceMean_ptv1, DistanceStdDev_ptv1, DistanceMode_ptv1, DistanceMedian_ptv1, DistanceSkewness_ptv1, DistanceMax_ptv1, DistanceMin_ptv1, PercentageOverlap_ROI_Fraction_ptv1, alpha_ptv1, beta_ptv1, gamma_ptv1, doseMean FROM structure_set_roi_sequence_copy WHERE stdROIName="cochleaRt" AND fk_patient_id IN (',selectedPatientsString,')'));
    [dbmean5, dbstd5, dbmode5, dbmedian5, dbskewness5, dbmax5, dbmin5, overlap5, alpha5, beta5, gamma5, doseMean5] = mysql(horzcat('SELECT DistanceMean_ptv1, DistanceStdDev_ptv1, DistanceMode_ptv1, DistanceMedian_ptv1, DistanceSkewness_ptv1, DistanceMax_ptv1, DistanceMin_ptv1, PercentageOverlap_ROI_Fraction_ptv1, alpha_ptv1, beta_ptv1, gamma_ptv1, doseMean FROM structure_set_roi_sequence_copy WHERE stdROIName="mandible" AND fk_patient_id IN (',selectedPatientsString,')'));
    [dbmean6, dbstd6, dbmode6, dbmedian6, dbskewness6, dbmax6, dbmin6, overlap6, alpha6, beta6, gamma6, doseMean6] = mysql(horzcat('SELECT DistanceMean_ptv1, DistanceStdDev_ptv1, DistanceMode_ptv1, DistanceMedian_ptv1, DistanceSkewness_ptv1, DistanceMax_ptv1, DistanceMin_ptv1, PercentageOverlap_ROI_Fraction_ptv1, alpha_ptv1, beta_ptv1, gamma_ptv1, doseMean FROM structure_set_roi_sequence_copy WHERE stdROIName="tongue" AND fk_patient_id IN (',selectedPatientsString,')'));
  
    %training_inputs = [ones(length(dbmean1),1) dbmean1 dbstd1 dbmode1 dbmedian1 dbskewness1 dbmax1 dbmin1 overlap1 dbmean2 dbstd2 dbmode2 dbmedian2 dbskewness2 dbmax2 dbmin2 overlap2 dbmean3 dbstd3 dbmode3 dbmedian3 dbskewness3 dbmax3 dbmin3 overlap3 dbmean4 dbstd4 dbmode4 dbmedian4 dbskewness4 dbmax4 dbmin4 overlap4 dbmean5 dbstd5 dbmode5 dbmedian5 dbskewness5 dbmax5 dbmin5 overlap5 dbmean6 dbstd6 dbmode6 dbmedian6 dbskewness6 dbmax6 dbmin6 overlap6];
    %training_inputs_noOnes = [dbmean1 dbstd1 dbmode1 dbmedian1 dbskewness1 dbmax1 dbmin1 overlap1 dbmean2 dbstd2 dbmode2 dbmedian2 dbskewness2 dbmax2 dbmin2 overlap2 dbmean3 dbstd3 dbmode3 dbmedian3 dbskewness3 dbmax3 dbmin3 overlap3 dbmean4 dbstd4 dbmode4 dbmedian4 dbskewness4 dbmax4 dbmin4 overlap4 dbmean5 dbstd5 dbmode5 dbmedian5 dbskewness5 dbmax5 dbmin5 overlap5 dbmean6 dbstd6 dbmode6 dbmedian6 dbskewness6 dbmax6 dbmin6 overlap6];
    training_inputs = [ones(length(dbmean1),1) dbmean1 dbstd1 dbmode1 dbskewness1 dbmax1 dbmin1 overlap1 dbmean2 dbstd2 dbmode2 dbskewness2 dbmax2 dbmin2 overlap2];
    training_inputs_noOnes = [dbmean1 dbstd1 dbmode1 dbskewness1 overlap1 dbmean2 dbstd2 dbmode2 dbskewness2 overlap2 dbmean5 dbstd5 dbmode5 dbskewness5 overlap5];
    training_outputs = [doseMean1 doseMean2 doseMean3 doseMean4 doseMean5 doseMean6];
    training_inputs_cell = cell(1);
    training_inputs_cell{1} = training_inputs;
    %[beta,Sigma,E,CovB,logL]=mvregress(training_inputs, training_outputs)
    lm=LinearModel.fit(training_inputs_noOnes, doseMean5,'purequadratic')
    %[b,bint,r,rint,stats]=regress(doseMean1, training_inputs)
end

mysql('close');    
clear conn;