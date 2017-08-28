% Find regression models relating anatomy and mean dose to critical
% structures

% Use either regress, or LinearModel.fit with 'linear','quadratic' or
% 'purequadratic'. 

% Error: Regression design matrix is rank deficient to within machine precision. 
% Reduce the number of features

clear all;

conn = mysql('open','localhost','root');
mysql('use rt_hn_v6');
roi = 'parotidLt';

allPatients = [1 3 4 5 7 8 11 12 14 15 16 17 18 19 20 22 23 24 25 27 29 30 31 32 33 34 35 37 38 40 41 45 47 48 49 50 52 53 54 55 56 57 58 60 62 63 65 67 68 69 70 71];
%allPatients = [1 8 11 12 14 15 16 17 18 19 20 22 23 24 25 27 29 30 31 32 33 34 35 37 38 40 41 45 47 48 49 50 52 53 54 55 56 57 58 60 62 63 65 67 68 69 70 71];

realValues = [];
predictedValues = [];

for i = 1:1
    qPatient = allPatients(i);
    dbPatients = allPatients(allPatients ~= qPatient);
    dbPatientsString = sprintf('%.0f,' , dbPatients);
    dbPatientsString = dbPatientsString(1:end-1);
    [dbmean, dbstd, dbmode, dbmedian, dbskewness, dbmax, dbmin, overlap, alpha, beta, gamma, doseMean] = mysql(horzcat('SELECT DistanceMean_ptv1, DistanceStdDev_ptv1, DistanceMode_ptv1, DistanceMedian_ptv1, DistanceSkewness_ptv1, DistanceMax_ptv1, DistanceMin_ptv1, PercentageOverlap_ROI_Fraction_ptv1, alpha_ptv1, beta_ptv1, gamma_ptv1, doseMean FROM structure_set_roi_sequence_copy WHERE stdROIName="',roi,'" AND fk_patient_id IN (',dbPatientsString,')'));
    [qmean, qstd, qmode, qmedian, qskewness, qmax, qmin, qoverlap, qalpha, qbeta, qgamma, qdoseMean] = mysql(horzcat('SELECT DistanceMean_ptv1, DistanceStdDev_ptv1, DistanceMode_ptv1, DistanceMedian_ptv1, DistanceSkewness_ptv1, DistanceMax_ptv1, DistanceMin_ptv1, PercentageOverlap_ROI_Fraction_ptv1, alpha_ptv1, beta_ptv1, gamma_ptv1, doseMean FROM structure_set_roi_sequence_copy WHERE stdROIName="',roi,'" AND fk_patient_id = "',num2str(qPatient),'"'));

    %training_inputs = [ones(length(dbmean),1) dbmean dbstd dbmode dbmedian dbskewness dbmax dbmin overlap];
    %training_inputs_noOnes = [dbmean dbstd dbmode dbmedian dbskewness dbmax dbmin overlap alpha beta gamma];
    training_inputs = [ones(length(dbmean),1) dbmean dbstd dbmode dbskewness dbmax dbmin overlap alpha beta gamma];
    training_inputs_noOnes = [dbmean dbstd dbmode dbskewness dbmax dbmin overlap alpha beta gamma];
    training_output = doseMean;
    [b,bint,r,rint,stats]=regress(training_output, training_inputs)
    rcoplot(r,rint);
    lm=LinearModel.fit(training_inputs_noOnes, training_output,'linear')
    %figure;
    %plotDiagnostics(lm,'contour');
    
%     %prediction_inputs = [qmean qstd qmode qmedian qskewness qmax qmin qoverlap qalpha qbeta qgamma];
%     prediction_inputs = [qmean qstd qmode qmedian qskewness qmax qmin qoverlap];
%     predicted_output = predict(mdl,prediction_inputs);
%     realValues = [realValues qdoseMean];
%     predictedValues = [predictedValues predicted_output];
end


mysql('close');    
clear conn;