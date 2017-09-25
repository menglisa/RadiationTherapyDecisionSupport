clear all;

conn = mysql('open','localhost','root');
mysql('use rt_hn_v6');

patient=58;

doseCell = mysql(horzcat('SELECT dvhDose FROM structure_set_roi_sequence_copy WHERE fk_patient_id = "',num2str(patient),'" AND stdROIName = "cochleaLt"'));
dose = regexp(doseCell{1},',','split');
dose{1}=dose{1}(2:length(dose{1}));
dose{length(dose)}=dose{length(dose)}(1:length(dose{length(dose)})-1);
dose=str2double(dose);
doseCumulative = cumsum(dose);
