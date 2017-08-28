clear all;

conn = mysql('open','localhost','root');
mysql('use rt_hn_v6');
roi = 'parotidLt';

allPatients = [1 3 4 5 7 8 11 12 14 15 16 17 18 19 20 22 23 24 25 27 29 30 31 32 33 34 35 37 38 40 41 45 47 48 49 50 52 53 54 55 56 57 58 60 62 63 65 67 68 69 70 71];
realValues = [];
predictedValues = [];

for i = 1:length(allPatients)
    qPatient = allPatients(i);
    dbPatients = allPatients(allPatients ~= qPatient);
    dbPatientsString = sprintf('%.0f,' , dbPatients);
    dbPatientsString = dbPatientsString(1:end-1);
    [dbmean, dbstd, dbmode, dbmedian, dbskewness, dbmax, dbmin, overlap, alpha, beta, gamma, doseMean] = mysql(horzcat('SELECT DistanceMean_ptv1, DistanceStdDev_ptv1, DistanceMode_ptv1, DistanceMedian_ptv1, DistanceSkewness_ptv1, DistanceMax_ptv1, DistanceMin_ptv1, PercentageOverlap_ROI_Fraction_ptv1, alpha_ptv1, beta_ptv1, gamma_ptv1, doseMean FROM structure_set_roi_sequence_copy WHERE stdROIName="',roi,'" AND fk_patient_id IN (',dbPatientsString,')'));
    [qmean, qstd, qmode, qmedian, qskewness, qmax, qmin, qoverlap, qalpha, qbeta, qgamma, qdoseMean] = mysql(horzcat('SELECT DistanceMean_ptv1, DistanceStdDev_ptv1, DistanceMode_ptv1, DistanceMedian_ptv1, DistanceSkewness_ptv1, DistanceMax_ptv1, DistanceMin_ptv1, PercentageOverlap_ROI_Fraction_ptv1, alpha_ptv1, beta_ptv1, gamma_ptv1, doseMean FROM structure_set_roi_sequence_copy WHERE stdROIName="',roi,'" AND fk_patient_id = "',num2str(qPatient),'"'));
    if ~isempty(qmean)
        %training_inputs = [mean std mode median skewness max min overlap alpha beta gamma];
        training_inputs = [dbmean dbstd dbmode dbskewness dbmax dbmin overlap alpha beta gamma];
        training_output = doseMean;
        [b,bint]=regress(training_output, training_inputs);
        mdl = LinearModel.fit(training_inputs,training_output);

        %prediction_inputs = [qmean qstd qmode qmedian qskewness qmax qmin qoverlap qalpha qbeta qgamma];
        prediction_inputs = [qmean qstd qmode qskewness qmax qmin qoverlap qalpha qbeta qgamma];
        %predicted_output = predict(mdl,prediction_inputs);
        predicted_output = b'*prediction_inputs';
        realValues = [realValues qdoseMean];
        predictedValues = [predictedValues predicted_output];
    end
end
figure;
plot(1:length(realValues),realValues, 'black');
hold on;
plot(1:length(realValues),predictedValues,'red');
[h,p] = ttest(realValues',predictedValues');
[rho, rhop] = corr(realValues',predictedValues');

result=[realValues' predictedValues'];

mysql('close');    
clear conn;