clear all;

conn = mysql('open','localhost','root');
mysql('use rt_hn_v6');
roi = 'parotidRt';

%*****************************************************************************
allPatients = [1 3 4 5 7 8 11 12 14 15 16 17 18 19 20 22 23 24 25 27 29 30 31 32 33 34 35 37 38 40 41 45 47 48 49 50 52 53 54 55 56 57 58 60 62 63 65 67 68 69 70 71];
patientsString = sprintf('%.0f,' , allPatients);
patientsString = patientsString(1:end-1);
[ovh50, ovh75, ovh95, distanceMean, distanceMedian, overlap, doseMean, d50, d75, d90, doseMax] = mysql(horzcat('SELECT ptv1_ovh50, ptv1_ovh75, ptv1_ovh95, DistanceMean_ptv1, DistanceMedian_ptv1, PercentageOverlap_ROI_Fraction_ptv1, doseMean, d50, d75, d90, doseMax FROM structure_set_roi_sequence_copy WHERE stdROIName="',roi,'" AND fk_patient_id IN (',patientsString,')'));
[rho_doseMean, pval_doseMean] = corr(ovh50,doseMean);
[rho_d50, pval_d50] = corr(overlap,d50);
[rho_d75, pval_d75] = corr(overlap,d75);
[rho_d90, pval_d90] = corr(overlap,d90);
%*****************************************************************************
figure; scatter(overlap,doseMean),title('Dose Mean');
% figure; scatter(ovh95,d50),title('D50');
% figure; scatter(ovh95,d75),title('D75');
% figure; scatter(ovh95,d90),title('D90');

mysql('close');    
clear conn;