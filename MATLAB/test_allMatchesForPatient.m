clear all;

conn = mysql('open','localhost','root');
mysql('use rt_hn_v6');
roi = 'parotidLt';

% %*****************************************************************************

allPatients = [1 3 4 5 7 8 11 12 14 15 16 17 18 19 20 22 23 24 25 27 29 30 31 32 33 34 35 37 38 40 41 45 47 48 49 50 52 53 54 55 56 57 58 60 62 63 65 67 68 69 70 71];
patientsString = sprintf('%.0f,' , allPatients);
patientsString = patientsString(1:end-1);

% [distanceMean, overlap, doseMean] = mysql(horzcat('SELECT DistanceMean_ptv1, OverlapVolume_ptv1, doseMean FROM structure_set_roi_sequence_copy WHERE stdROIName="',roi,'" AND fk_patient_id IN (',patientsString,')'));
% [rho, pval] = corrcoef(overlap,doseMean);
% %*****************************************************************************

ovhArray = [];
dvhArray = [];


for currentIndex = 1:length(allPatients)
   [ovh, dvh] = mysql(horzcat('SELECT emd, dvhDistance FROM ',roi,' WHERE queryPatientID = "',num2str(allPatients(currentIndex)),'"'));
   if ~isempty(ovh)
       closestOVH = min(ovh);
       %disp(closestOVH);
       closestDVH = dvh(ovh==closestOVH);
       ovhArray = [ovhArray closestOVH];
       dvhArray = [dvhArray closestDVH];
   end
end

mysql('close');    
clear conn;