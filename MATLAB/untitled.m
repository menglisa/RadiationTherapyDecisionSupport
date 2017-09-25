clear all;
conn = mysql('open','localhost','root');
mysql('use rt_hn_v6');
fk_patient_id=1;
%Since every contour has an associated CT Slice, extract the first ct image
%for the first roi
[sampleCTSOP, ct_series_id] = mysql(horzcat('SELECT fk_sop_id, fk_series_id FROM ct_image WHERE fk_patient_id = "1" LIMIT 1'));
numCTs = mysql(horzcat('SELECT numCTifCT FROM series WHERE id = "',num2str(ct_series_id),'"'));%Get number of CT Images

%Get row spacing, slice spacing etc based on the sample ct image
[rowSpacing, columnSpacing, sliceSpacing, width, height]=mysql(horzcat('SELECT pixelSpacingRow, pixelSpacingColumn, sliceThickness, columns, rows FROM image_plane_pixel WHERE fk_sop_id="',num2str(sampleCTSOP),'"'));
rowSpacing=str2double(rowSpacing{1,1});columnSpacing=str2double(columnSpacing{1,1});sliceSpacing=str2double(sliceSpacing{1,1});
imageBlock=zeros(height, width, numCTs);

%imgPosPatZ gives the z indices of all CT images. This is useful in
%assembling the CT Block
imgPosPatZ = sort(str2double(mysql(horzcat('SELECT imgPosPatZ FROM image_plane_pixel WHERE fk_series_id="',num2str(ct_series_id),'"'))));
allCTs = mysql(horzcat('SELECT id FROM sop WHERE fk_series_id="',num2str(ct_series_id),'"'));
for vv=1:length(allCTs)
        [ser,st,pat]=mysql(horzcat('SELECT fk_series_id,fk_study_id,fk_patient_id FROM sop WHERE id="',num2str(allCTs(vv)),'"'));
        ct_z=str2double(mysql(horzcat('SELECT imgPosPatZ FROM image_plane_pixel WHERE fk_sop_id="',num2str(allCTs(vv)),'"')));
        imageBlock(:,:,imgPosPatZ==ct_z)=im2double(dicomread(horzcat('/Users/ruchi/Documents/python/rt/test/dicom/',num2str(pat),'/',num2str(st),'/',num2str(ser),'/',num2str(allCTs(vv)),'.dcm')));
        
end;

[dose_sop_id, dose_series_id, dose_study_id, doseGridScaling]=mysql(horzcat('SELECT fk_sop_id, fk_series_id, fk_study_id, doseGridScaling FROM dose WHERE fk_patient_id="1"'));
doseGrid = dicomread(horzcat('/Users/ruchi/Documents/python/rt/test/dicom/',num2str(fk_patient_id),'/',num2str(dose_study_id),'/',num2str(dose_series_id),'/',num2str(dose_sop_id),'.dcm'));
doseGrid=doseGrid.*str2double(doseGridScaling{1,1});
doseGrid=reshape(doseGrid,size(doseGrid,1),size(doseGrid,2),size(doseGrid,4));
maxDose=max(max(max(doseGrid)));
imageBlockRGB=repmat(reshape(imageBlock,[height width 1 numCTs]),[1 1 3 1]);%Change to RGB
imageBlockRGB=imageBlockRGB/max(max(max(max(imageBlockRGB))));

isodoseValues=[40;50;60;70;80;90;95];
isodoseRows = cell(7,1);
isodoseColumns = cell(7,1);

for j=1:length(isodoseValues)
    tempDoseMask = zeros(size(doseGrid));
    doseOutline = zeros(size(doseGrid));
    tempDoseMask(doseGrid>(isodoseValues(j)*0.01*maxDose))=1;
    for i=1:size(doseGrid,3)
        doseOutline(:,:,i) = bwperim(tempDoseMask(:,:,i));
    end
    [r,c]=find(doseOutline);
    isodoseRows{j} = strrep(mat2str(r),';',',');
    isodoseColumns{j} = strrep(mat2str(c),';',',');
end;

clear conn;

