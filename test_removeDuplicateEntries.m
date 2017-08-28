% Remove duplicate entries from the pairwise comparison tables (e.g. 1,3
% and 3,1)

clear all;

conn = mysql('open','localhost','root');
mysql('use rt_hn_v6');
roi = 'pharynx';

[queryPatientIDs] = mysql(horzcat('SELECT DISTINCT queryPatientID FROM ',roi));

for currentQueryPatientIndex = 1:length(queryPatientIDs)
%for currentQueryPatientIndex = 1:1
    currentDBPatientIDs = mysql(horzcat('SELECT dbPatientID FROM ',roi,' WHERE queryPatientID = "',num2str(queryPatientIDs(currentQueryPatientIndex)),'"'));
    for currentDBPatientIndex=1:length(currentDBPatientIDs)
        reverseEntry = mysql(horzcat('SELECT id FROM ',roi,' WHERE queryPatientID="',num2str(currentDBPatientIDs(currentDBPatientIndex)),'" AND dbPatientID = "',num2str(queryPatientIDs(currentQueryPatientIndex)),'"'));
        if (~isempty(reverseEntry))
            mysql(horzcat('DELETE FROM ',roi,' WHERE id = "',num2str(reverseEntry),'"'));
            %disp(horzcat('DELETE FROM ',roi,' WHERE id = "',num2str(reverseEntry),'"'));
        end
    end   
end

mysql('close');    
clear conn;