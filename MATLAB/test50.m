conn = mysql('open','localhost','root');
mysql('use pt_pr_v1');
pid=mysql(horzcat('select distinct PatientID from iod_patient'));

for p=1:length(pid)
    if ~strcmp(pid{p},'051')
        x=PT_getContoursFull2(pid{p},'Bladder');
    end;
end;