# Structure of the SQL Database for RTDS

Radiation Therapy Decision Support uses a SQL database to store extracted features and user / patient data for the website.
This document is designed to show the structure of the SQL database and what each table's headers mean on the database.

## Accessing a copy of the database. 

Go to [this link]() and download the database `dsrt.sql`. Alternatively, for the most bleeding-edge version of the 
server:
1) Log into the server
2) In the terminal prompt, type
```
$ mysqldump -u root -p ipilab dsrt > dsrt.sql
```
This will dump all the contents to `dsrt.sql`. 
3) Download `dsrt.sql` to your computer and delete it from the server.

To view the database, go to MySQL Workbench or similar, and perform a data import. This will import all the 
tables into a schema of your choice in naming (Note that schemas are like MySQL database- MySQL workbench just
uses a different name for them)

## Database Tables + Headers

#### `auth_group`
An `auth_group` is a set of permissions for all users given a specific group type.
For example, one row of the `auth_group` table might be `admins`, which we may have
users assigned to, for example, `admin1` and `admin2`. 

Headers:

**id**, `int(11)` -> The unique id for the group. Used as a marker in other tables to signify a
        User's group.

**name** `varchar(80)` -> The name of the group, e.g. `admins`, `doctors`, etc. Note that in a multi-hospital
        setting this would need to also differentiate between doctors from different hospitals
        and such, so you may have `UCLA doctors`, `TUM doctors` and so on.

#### `auth_group_permissions`
This assigns the permissions to each `auth_group` based on the permission id in `auth_permission`.
For example, one row of the `auth_group_permissions` table might be to assign the `UCLA_doctors`
group the ability to read UCLA patient's data, marked by permission id 12.

Headers

**id** `int(11)`-> unique ID for the permission

**group_id** `int(11)`-> The `auth_group` for whom the permission id should be granted

**permission_id** `int(11)` -> Specific permission by permission_id from `auth_permission`. 

#### `auth_permission`
This contains all the permission types available in RTDS. Examples include being able
to add or delete patients, beign able to add, change or delete groups and being able 
to view patient information.

Headers

**id** `int(11)`-> Unique ID for the permission

**name** `varchar(255)` -> Specific name of the permission. Follows naming `can [ACTION WORD] [VARIABLE TYPE]`,
        no uppercase

**content_type_id** `int(11)` -> id of the `[VARIABLE TYPE]` from the name. For example, all permissions 
        relating to `log_entry` may have `content_type_id` 1.

**codename** `varchar(100)` -> name without starting `can`

#### `auth_user`
This contains all the registered users for RTDS, including admins, doctors and clinicians.

Headers

**id** `int(11)`-> User's unique ID

**password** `varchar(128)` -> SHA 256 hashed password of user

**last_login** `datetime` -> last time user logged in

**is_superuser** `tinyint(1)` -> whether the user is an admin

**username** `varchar(150)` -> user's username

**first_name** `varchar(30)` -> user's first name

**last_name** `varchar(30)` -> user's last name

**email** `varchar(254)` -> user's email

**is_staff** `tinyint(1)` -> whether user is a (developer of RTDS?)

**is_active** `tinyint(1)` -> Whether the account has been deleted (unsure)

**date_joined** `datetime` -> date of account creation

#### `auth_user_groups`
This links users by id to groups by id.

Headers
**id** `int(11)` -> id of linkage. Not really needed by anything.

**user_id** `int(11)` -> id of user from `auth_user`. 

**group_id** `int(11)` -> id of group from `auth_group` which the user identified
    by `user_id` should belong to. 

#### `auth_user_user_permissions`
This assigns permissions to user that are already not assigned from
the group.

Headers

**id** `int(11)`-> not really needed, id of linkage

**user_id** `int(11)` -> id of user from `auth_user`

**permission_id** `int(11)` -> id of permission from `auth_permission`

#### `ct_images`
This stores CT image data for a given patient

Headers

**id** `int(11)` -> id of a given CT image

**SOPInstanceUID** `varchar(200)` -> DICOM id for the CT image

**SOPClassUID** `varchar(100)` -> typically "CT IMAGE"

**ImageType** `varchar(100)` -> typically "CT IMAGE"

**PhotometricInterpretation** `varchar(20)` -> DICOM field from CT image file

**RescaleSlope** `int(11)` -> DICOM field from CT image file

**RescaleIntercept** `int(11)` -> DICOM field from CT image file

**SliceLocation** `int(11)` -> DICOM field from CT image file

**PixelSpacing** `varchar(50)` -> DICOM field from CT image file

**ImageOrientationPatient** `varchar(100)` -> DICOM field from CT image file

**ImagePositionPatient** `varchar(100)` -> DICOM field from CT image file

**SliceThickness** `varchar(100)` -> DICOM field from CT image file

**BodypartExamined** `varchar(100)` -> DICOM field from CT image file

**Rows** `int(11)` -> DICOM field from CT image file. Number of rows of pixels in CT image.

**Columns** `int(11)` -> DICOM field from CT image file. Number of columns of pixels in CT image.

**fk_patient_id_id** `int(11)` -> Patient ID from database who CT image belongs to

**fk_series_id_id** `int(11)` -> Series ID from database who CT image belongs to

**fk_study_id_id** `int(11)` -> Study ID from database who CT image belongs to

**fk_user_id_id** `int(11)` -> not needed

#### `django_admin_log`

Headers

**id** `int(11)`

**action_flag** `smallint(5) UNSIGNED`

**action_time** `datetime`

**change_message** `longtext`

**content_type_id** `int(11)`

**object_id** `longtext`

**object_repr** `varchar(200)`

**user_id** `int(11)`

#### `django_content_type`

Headers

**id** `int(11)`

**app_label** `varchar(100)`

**model** `varchar(100)`

#### `django_migrations`

Headers

**id** `int(11)`

**app** `varchar(255)`

**name** `varchar(255)`

**applied** `datetime`

#### `django_session`

Headers

**session_key** `varchar(40)`

**session_data** `longtext`

**expire_date** `datetime`

#### `oar_dictionary`
This links names of specific oars against a unique id. Note that
OAR in this context refers to an ROI - it can be either an OAR
or a PTV. 

Headers

**id** `int(11)`-> Unique database-assigned ID for the given ROI

**ROIName** `varchar(100)`-> Name of the ROI (full name)

**ROIDisplayColor** `varchar(100)`-> What color the contour should be for the ROI when flushed to the GUI. 
                    Should be a tuple of RGB values. In the event users can change the 
                    color of the ROI in the GUI, this would be the default colors. 

#### `ovh`
This stores extracted OVH information for a given PTV-OAR pair for a given patient's study.

Headers

**id** `int(11)` -> not really needed, unique id assigned to OVH

**binValue** `longtext` -> supposed to be binValues(?) - values for each bin OVH histogram

**binAmount** `longtext` -> amount of pixels in each bin

**OverlapArea** `int(11)` -> unsure

**ptv_id** `int(11)` -> id of ptv from `oar_dictionary`

**OAR_id** `int(11)` -> id of oar from `oar_dictionary`

**fk_study_id_id** `int(11)` -> DICOM study id for which the OVH was extracted from 

#### `patients`
This is basic patient metadata.

Headers

**id** `int(11)` -> database-assigned id for the patient. If two patients from different
        hospitals have the same `fk_user_id_id`, this should be used
        as the deciding factor as to which patient information belongs to. 

**PatientName** `varchar(200)` -> name of patient (full)

**BirthDate** `date` -> Patient date of birth, `null` if not known

**Gender** `varchar(20)` -> Single character: `M` for Male, `F` for female, `O` for other

**EnthicGroup** `varchar(200)` -> Ethnic Group of patient, e.g. `White`, `Asian` etc

**fk_user_id_id** `int(11)` -> user id by hospital. Probably used as a unique patient
                identifier. Id is typically extracted from DICOM files
                for a patient.

#### `rt_contour`
Stores the contour data to be overlaid over a given slice of a CT object
for a given patient.

Headers

**id** `int(11)` -> not needed, database assigned id for contour

**ContourGeometricType** `varchar(100)` -> from the DICOM object, typically "CLOSED PLANAR"

**NumberOfContourPoints** `int(11)` -> Number of points in the contour data. Used
                        to preallocate array to store contour data.

**ContourData** `longtext` -> x y z points for a contour. All z coordinates should be 
                the same in a given contour as it will correspond with a 
                given slice

**ReferencedSOPClassUID** `varchar(100)` -> "CT Image Storage"

**ReferencedSOPInstanceUID** `varchar(100)` -> the CT image which the contour data is to be
                            overlaid on 

**fk_roi_id_id** `int(11)` -> id of ROI which the contour belongs to, database id

**fk_structureset_id_id** `int(11)` -> ID of RT Struct which the contour belongs to, database id

#### `rt_dose`
Stores dose data from an RT dose object

Headers

**id** `int(11)` -> database ID for the dose information

**SOPClassUID** `varchar(100)` -> typically the same for all RT dose objects

**SOPInstanceUID** `varchar(100)` -> DICOM assigned ID for dose object

**DoseGridScaling** `varchar(100)` -> Directly extracted from the dose object, needed for calculations
                    relating to the dose.

**DoseSummationType** `varchar(100)` -> Directly extracted from the dose object, needed for calculations
                    relating to the dose.

**DoseType** `varchar(100)` -> Directly extracted from the dose object, needed for calculations
                    relating to the dose.

**DoseUnits** `varchar(100)` -> Directly extracted from the dose object, needed for calculations
                    relating to the dose.  

**eferencedRTPlanSequence** `varchar(100)` -> Directly extracted from the dose object, needed for calculations
                    relating to the dose.

**ReferencedStructureSetSequence** `varchar(100)` -> Directly extracted from the dose object, needed for calculations
                    relating to the dose.

**fk_patient_id_id** `int(11)` -> database ID for patient who the RT dose object belongs to

**fk_series_id_id** `int(11)` -> database ID for series which the RT dose object belongs to

**fk_study_id_id** `int(11)` -> database ID for study which the RT dose object belongs to

**fk_user_id_id** `int(11)` -> not needed

#### `rt_dose_image`
Stores dose image data from an RT Dose object

Headers

**id** `int(11)` not needed, db unique id for rt dose image

**columns** `int(11)` of image

**rows** `int(11)` of image

**ImageOrientationPatient** `varchar(20)` Raw header extracted from DICOM file

**ImagePositionPatient** `varchar(20)` Raw header extracted from DICOM file

**PhotometricInterpretation** `varchar(20)` Raw header extracted from DICOM file

**PixelSpacing** `varchar(20)` Raw header extracted from DICOM file

**NumberOfFrames** `int(11)` Raw header extracted from DICOM file

**ImageData** `longtext` Raw image data from the DICOM file

**fk_dose_id_id** `int(11)` db id of rt dose object

**fk_patient_id_id** `int(11)` patient id who rt dose image belongs to

**fk_series_id_id** `int(11)` series which rt dose belongs to

**fk_study_id_id** `int(11)` study which rt dose belongs to

**fk_user_id_id** `int(11)` not needed

#### `rt_dvh` 

Stores the Dose Volume Histogram (DVH) for an RT dose object

**id** `int(11)` -> unique ID assigned to rt dose object by db, not needed

**DVHDoseScaling** `varchar(20)` -> unsure

**DVHMaximumDose** `double` -> unsure

**DVHMeanDose** `double` -> unsure

**DVHMinimumDose** `double` -> unsure

**DVHNumberOfBins** `double` -> unsure

**DVHReferencedROI** `varchar(10)` -> the ROI which a DVH is describing by db id

**DVHType** -> `varchar(10)` unsure

**DVHVolumeUnits** `varchar(10)` -> unsure

**DoseType** `varchar(10)` -> Unsure

**DoseUnits** `varchar(10)` -> unsure

**DVHData** `longtext` -> unsure

**fk_dose_id_id** `int(11)` -> database id of the rt dose object which the dvh is describing

**fk_patient_id_id** `int(11)`-> database id of the patient which the dvh belongs to

**fk_series_id_id** `int(11)`-> database id of the series which the dvh belongs to

**fk_study_id** `int(11)`-> database id of the study which the dvh belongs to

**fk_user_id_id** `int(11)`-> not needed

#### `rt_isdose`
RT Isodose data stored after processing by the program. Stores each value
by pixel.

Headers

**id** `int(11)`-> not needed, unique db assigned id for the RT isodose data

**RowPosition** `longtext` -> row position wrt CT image rows and columns where isodose pixel is

**ColumnPosition** `longtext` -> column position wrt CT image rows and columns where isodose pixel is   

**IsDoseValue** `int(11)` -> value of isodose at pixel position

**fk_ct_image_id_id** `int(11)`-> ct image which isodose is to be overlaid on

**fk_dose_id_id** `int(11)`-> dose object database id isodose data was extracted from

**fk_patient_id_id** `int(11)`-> patient database id which rt isodose data belongs to

**fk_series_id_id** `int(11)`-> series database id for isodose data

**fk_study_id_id** `int(11)`-> study databae id for isodose data
               
#### `rt_rois`
Stores the ROIs for a given RT Struct object

Headers

**id** `int(11)` -> not needed, ID assigned to an ROI from a given RT Struct object

**ROIName** `varchar(100)` -> Name of the ROI 

**Volume** `double` -> volume of ROI (in what measurement?)

**TotalContours** `int(11)`-> How many 2D contours have been drawn for the ROI

**fk_structureset_id_id** `int(11)` -> RT Struct which the roi belongs to, database id

**fk_patient_id_id** `int(11)`-> patient to which the ROI belongs to

**fk_series_id_id** `int(11)`-> series to which the ROI belongs to

**fk_study_id_id**`int(11)` -> study to which the ROI belongs to

**fk_user_id_id** `int(11)`-> not needed

**ROINumber** `varchar(200)` -> directly extracted raw from the DICOM file. 

#### `rt_structureset`
This stores information on the ROIs in an RT STRUCT object

Headers

**id** `int(11)`-> unique id assigned by db for RT STRUCT

**SOPInstanceUID** `varchar(200)` -> DICOM UID for the RT structure object

**SOPClassUID** `varchar(200)` -> Defaults to "RT Structure Set Storage". Acts as a failsafe
                in making sure correct files are uploaded to the correct DB table.

**TotalROIs** `int(11)`-> Number of ROIs in RT Struct object

**fk_patient_id_id** `int(11)`-> DICOM id for the patient which the RT Struct belongs to

**fk_series_id_id**`int(11)` -> DICOM id for the series which the RT Struct belongs to

**fk_study_id_id** `int(11)`-> DICOM id for the study which the RT Struct belongs to

**fk_user_id_id**`int(11)` -> not needed

#### `series`
Stores the DICOM series ID for a given series of images. Types of series
include CT image series and RT structure series. Typically one study
will have multiple series in it. 

Headers

**id** `int(11)`-> database assigned id for the series

**SeriesInstanceUID** `varchar(200)` -> raw UID from the DICOM files for the series. All DICOM
                    files of the same series have the same SeriesInstanceUID

**SeriesDate** `date` -> Date series was acquired. 

**SeriesDescription** `varchar(200)` -> Type of Series + manufacturer. For example, one might be
                    "Oncentra Structure Set"

**SeriesType** `varchar(100)` -> Either "CT" or "RTSTRUCT" typically

**Modality** `varchar(100)` -> raw field from DICOM file- either "CT" or "RTSTRUCT"

**SeriesNumber** `varchar(100)` -> raw field from DICOM file

**PhysicianOfRecord** `varchar(100)` -> Physician who was involved in acquiring DICOM series. From DICOM
                    files themselves.

**Manufacturer** `varchar(50)` -> who manufactured the device the DICOM series was acquired on. 

**fk_patient_id_id** `int(11)` -> DICOM id for the patient who the series belongs to

**fk_study_id_id**`int(11)` -> DICOM id for the study which the series belongs to

**fk_user_id_id**`int(11)` -> not needed?

#### `similarity`
This is used to store similarity values for the OVH, STS and target dose for 
a pair of patients. These values are generated by the Python scripts and 
stored here.

Headers

**id**-> `int(11)` not really needed, ID of similarity pair

**DBStudyID** `varchar(100)` -> The "Historical" patient in the pair. Typically at the time
    of this calculation, one of the patients is newly-uploaded, who is
    considered the current patient. The other patient in the pair is considered
    the historical patient. This is the study ID of the historical patient,
    from `studies`

**Similarity** `double` -> Target Dose similarity (unsure)

**OVHDissimilarity** `double` -> Similarity between two Overlap Volume Histograms for the two patients

**STSDissimilarity** `double` -> Similarity between two Spatial Target Signature histograms

**TargetOAR** `varchar(200)` -> the OAR the OVH / STS are between, identified by id in `oar_dictionary`

**fk_study_id_id** `int(11)` -> the study ID of the current patient

#### `sts`
Stores values for the Spatial Target Signature Histogram for a specified patient.

Headers

**id** `int(11)` -> not really needed, unique id of STS histogram for a patient and given PTV-OAR pair in DB

**elevation_bins** `longtext` -> amounts for the elevation bins in the STS histogram

**distance_bins** `longtext` -> amounts for the distance bins in the STS histogram

**azimuth_bins** `longtext` -> amounts for the azimuth bins in the STS histogram

**amounts** `longtext` -> flattened array (unsure) storing the values for each (elevation, distance, azimuth)
            tuple. 

**ptv_id** `int(11)`-> id of primary target volume from `oar_dictionary`

**OAR_id** `int(11)`-> id of organ at risk from `oar_dictionary`

**fk_study_id_id** `int(11)`-> id of study (DICOM) from `studies` for which the STS histogram belongs to. 

#### `studies`
This stores which study belongs to which patient. 

Headers

**id** `int(11)`-> database assigned id for the study

**StudyInstanceUID** `varchar(200)` -> from a DICOM file, what the study UID is

**StudyDate** `date` -> Extracted from DICOM file with specified StudyInstanceUID

**StudyDescription** `varchar(200)` -> What the study scanned for 

**TotalSeries** `int(11)`-> unsure

**fk_patient_id_id** `int(11)`-> DICOM patient ID for whom the study belongs to. 

**fk_user_id_id** `int(11)`-> unsure. This should probably not exist

#### `userprofile_userprofile`
This is general user information on each person.

Headers

**id** `int(11)`-> not really needed, id of metadata

**occupation** `varchar(30)` -> occupation of user by id

**institution** `varchar(30)` -> place where the user works

**birthday** `date` -> user date of birth

**location** `varchar(30)` -> location where the user works

**bio** `longtext` -> biographical statement on the user. For example,
        one might write. "Dr. something, formerly worked at UCLA,
        now works at Roswell Park as a Radiation Oncologist"

**user_id** `int(11)`-> id for which the profile information belongs, user id from
            `auth_user`.