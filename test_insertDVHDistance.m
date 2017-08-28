% Update pairwise comparison tables with distances between DVHs

clear all;

conn = mysql('open','localhost','root');
mysql('use rt_hn_v6');
roi = 'pharynx';

[ids, queryPatientIDs, dbPatientIDs] = mysql(horzcat('SELECT id, queryPatientID, dbPatientID FROM ',roi));

for currentIndex = 1:length(ids)
    dvhDistance = emdforDVH(queryPatientIDs(currentIndex),dbPatientIDs(currentIndex),roi);
    mysql(horzcat('UPDATE ',roi,' SET dvhDistance = "',num2str(dvhDistance),'" WHERE id ="',num2str(ids(currentIndex)),'"'));
end

mysql('close');    
clear conn;