%test 20 and 8
clear all;
object_patient_id=57;
roiName='mandible';
color = [65 105 225; 124 252 0; 135 206 250; 255 255 0; 255 165 0; 255 20 147; 255 0 0; 51 255 255; 0 128 0; 32 178 170; 102 102 102; 51 0 0; 204 102 102; 153 0 102; 51 204 51; 255 204 0; 204 255 51; 102 51 0; 201 153 153; 204 255 51; 51 102 0; 204 204 204;102 102 0; 102 0 51; 255 204 255; 255 204 153; 102 0 102]/255; 

conn = mysql('open','localhost','root');
mysql('use rt_hn_v5');

[ovhObjectDistance ovhObjectVolume] = mysql(horzcat('SELECT ovhDistance_ptv1, ovhVolume_ptv1 FROM structure_set_roi_sequence_copy WHERE fk_patient_id=',num2str(object_patient_id),' AND stdROIName="',roiName,'"'));
ovhObjectDistance = regexp(ovhObjectDistance{1,1},',','split');
ovhObjectDistance{1}=ovhObjectDistance{1}(2:length(ovhObjectDistance{1}));
ovhObjectDistance{length(ovhObjectDistance)}=ovhObjectDistance{length(ovhObjectDistance)}(1:length(ovhObjectDistance{length(ovhObjectDistance)})-1);
ovhObjectDistance=str2double(ovhObjectDistance);
ovhObjectVolume = regexp(ovhObjectVolume{1,1},',','split');
ovhObjectVolume{1}=ovhObjectVolume{1}(2:length(ovhObjectVolume{1}));
ovhObjectVolume{length(ovhObjectVolume)}=ovhObjectVolume{length(ovhObjectVolume)}(1:length(ovhObjectVolume{length(ovhObjectVolume)})-1);
ovhObjectVolume=str2double(ovhObjectVolume);  
ovhObject = [ovhObjectDistance' ovhObjectVolume'];

[dvhObjectDistance dvhObjectVolume] = mysql(horzcat('SELECT ovhDistance_ptv1, ovhVolume_ptv1 FROM structure_set_roi_sequence_copy WHERE fk_patient_id=',num2str(object_patient_id),' AND stdROIName="',roiName,'"'));
dvhObjectDistance = regexp(dvhObjectDistance{1,1},',','split');
dvhObjectDistance{1}=dvhObjectDistance{1}(2:length(dvhObjectDistance{1}));
dvhObjectDistance{length(dvhObjectDistance)}=dvhObjectDistance{length(dvhObjectDistance)}(1:length(dvhObjectDistance{length(dvhObjectDistance)})-1);
dvhObjectDistance=str2double(dvhObjectDistance);
dvhObjectVolume = regexp(dvhObjectVolume{1,1},',','split');
dvhObjectVolume{1}=dvhObjectVolume{1}(2:length(dvhObjectVolume{1}));
dvhObjectVolume{length(dvhObjectVolume)}=dvhObjectVolume{length(dvhObjectVolume)}(1:length(dvhObjectVolume{length(dvhObjectVolume)})-1);
dvhObjectVolume=str2double(dvhObjectVolume);  
dvhObject = [dvhObjectDistance' dvhObjectVolume'];

% figure;
% legendList={num2str(object_patient_id)};
% p=plot(objectDistance,objectVolume);
% set(p,'Color',color(1,:),'LineWidth',2);
% hold on;
% counter=2;
            
patient_ids=mysql(horzcat('SELECT DISTINCT fk_patient_id FROM structure_set_roi_sequence_copy WHERE fk_patient_id NOT LIKE "',num2str(object_patient_id),'" AND ptv1 IS NOT NULL'));
ids_ovh=[];
emdValues_ovh=[];
ids_dvh=[];
emdValues_dvh=[];


for pid = 1:length(patient_ids)
    
    [OVHDistance OVHVolume DVHDose DVHVolume] = mysql(horzcat('SELECT ovhDistance_ptv1, ovhVolume_ptv1, dvhDose, dvhVolume FROM structure_set_roi_sequence WHERE fk_patient_id=',num2str(patient_ids(pid)),' AND stdROIName="',roiName,'"'));
    
    if (~isempty(OVHDistance))
        
        OVHDistance = regexp(OVHDistance{1,1},',','split');
        OVHDistance{1}=OVHDistance{1}(2:length(OVHDistance{1}));
        OVHDistance{length(OVHDistance)}=OVHDistance{length(OVHDistance)}(1:length(OVHDistance{length(OVHDistance)})-1);
        OVHDistance=str2double(OVHDistance);

        OVHVolume = regexp(OVHVolume{1,1},',','split');
        OVHVolume{1}=OVHVolume{1}(2:length(OVHVolume{1}));
        OVHVolume{length(OVHVolume)}=OVHVolume{length(OVHVolume)}(1:length(OVHVolume{length(OVHVolume)})-1);
        OVHVolume=str2double(OVHVolume);

        poolElement=[OVHDistance' OVHVolume'];
        w1=ones(length(ovhObject),1);
        w2=ones(length(poolElement),1);
        [xOVH fvalOVH] = emd(ovhObject, poolElement, w1, w2, @gdf);
        
%         if fval<3
%             p=plot(OVHDistance,OVHVolume);
%             set(p,'Color',color(counter,:),'LineWidth',2);
%             hold on; 
%             legendList{counter} = horzcat('Patient ',num2str(patient_ids(pid)));
%             counter=counter+1;
%         end;
       

        ids_ovh=[ids_ovh patient_ids(pid)];
        emdValues_ovh = [emdValues_ovh fvalOVH];
    end;
    
%     if (~isempty(DVHDose))
%         
%         DVHDose = regexp(DVHDose{1,1},',','split');
%         DVHDose{1}=DVHDose{1}(2:length(DVHDose{1}));
%         DVHDose{length(DVHDose)}=DVHDose{length(DVHDose)}(1:length(DVHDose{length(DVHDose)})-1);
%         DVHDose=str2double(DVHDose);
% 
%         DVHVolume = regexp(DVHVolume{1,1},',','split');
%         DVHVolume{1}=DVHVolume{1}(2:length(DVHVolume{1}));
%         DVHVolume{length(DVHVolume)}=DVHVolume{length(DVHVolume)}(1:length(DVHVolume{length(DVHVolume)})-1);
%         DVHVolume=str2double(DVHVolume);
% 
%         poolElement=[DVHDose' DVHVolume'];
%         w1=ones(length(dvhObject),1);
%         w2=ones(length(poolElement),1);
%         [x fvalDVH] = emd(dvhObject, poolElement, w1, w2, @gdf);
%         
% %         if fval<3
% %             p=plot(OVHDistance,OVHVolume);
% %             set(p,'Color',color(counter,:),'LineWidth',2);
% %             hold on; 
% %             legendList{counter} = horzcat('Patient ',num2str(patient_ids(pid)));
% %             counter=counter+1;
% %         end;
%        
% 
%         ids_dvh=[ids_dvh patient_ids(pid)];
%         emdValues_dvh = [emdValues_dvh fvalDVH];
%     end;
    
    
end

%legend(legendList,'Location','BestOutside');
mysql('close');