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
id -> The unique id for the group. Used as a marker in other tables to signify a
        User's group.
name -> The name of the group, e.g. `admins`, `doctors`, etc. Note that in a multi-hospital
        setting this would need to also differentiate between doctors from different hospitals
        and such, so you may have `UCLA doctors`, `TUM doctors` and so on.

#### `auth_group_permissions`
This assigns the permissions to each `auth_group` based on the permission id in `auth_permission`.
For example, one row of the `auth_group_permissions` table might be to assign the `UCLA_doctors`
group the ability to read UCLA patient's data, marked by permission id 12.

Headers:
id -> unique ID for the permission
group_id -> The `auth_group` for whom the permission id should be granted
permission_id -> Specific permission by permission_id from `auth_permission`. 

#### `auth_permission`
This contains all the permission types available in RTDS. Examples include being able
to add or delete patients, beign able to add, change or delete groups and being able 
to view patient information.

Headers
id -> Unique ID for the permission
name -> Specific name of the permission. Follows naming `can [ACTION WORD] [VARIABLE TYPE]`,
        no uppercase
content_type_id -> id of the `[VARIABLE TYPE]` from the name. For example, all permissions 
        relating to `log_entry` may have `content_type_id` 1.
codename -> name without starting `can`

#### `auth_user`
This contains all the registered users for RTDS, including admins, doctors and clinicians.

Headers
id -> User's unique ID
password -> SHA 256 hashed password of user
last_login -> last time user logged in
is_superuser -> whether the user is an admin
username -> user's username
first_name -> user's first name
last_name -> user's last name
email -> user's email
is_staff -> whether user is a (developer of RTDS?)
is_active -> Whether the account has been deleted (unsure)
date_joined -> date of account creation

#### `auth_user_groups`
This links users by id to groups by id.

Headers
id -> id of linkage. Not really needed by anything.
user_id -> id of user from `auth_user`. 
group_id -> id of group from `auth_group` which the user identified
    by `user_id` should belong to. 

#### `auth_user_user_permissions`
This assigns permissions to user that are already not assigned from
the group.

Headers
id -> not really needed, id of linkage
user_id -> id of user from `auth_user`
permission_id -> id of permission from `auth_permission`

#### `oar_dictionary`
This links names of specific oars against a unique id. Note that
OAR in this context refers to an ROI - it can be either an OAR
or a PTV. 

Headers
id -> Unique database-assigned ID for the given ROI
ROIName -> Name of the ROI (full name)
ROIDisplayColor -> What color the contour should be for the ROI when flushed to the GUI. 
                    Should be a tuple of RGB values. In the event users can change the 
                    color of the ROI in the GUI, this would be the default colors. 

#### `ovh`
This stores extracted OVH information for a given PTV-OAR pair for a given patient's study.

Headers
id -> not really needed, unique id assigned to OVH
binValue -> supposed to be binValues(?) - values for each bin OVH histogram
binAmount -> amount of pixels in each bin
OverlapArea -> unsure
ptv_id -> id of ptv from `oar_dictionary`
OAR_id -> id of oar from `oar_dictionary`
fk_study_id_id -> DICOM study id for which the OVH was extracted from 

#### `patients`
This is basic patient metadata.

Headers
id -> database-assigned id for the patient. If two patients from different
        hospitals have the same `fk_user_id_id`, this should be used
        as the deciding factor as to which patient information belongs to. 
PatientName -> name of patient (full)
BirthDate -> Patient date of birth, `null` if not known
Gender -> Single character: `M` for Male, `F` for female, `O` for other
EnthicGroup -> Ethnic Group of patient, e.g. `White`, `Asian` etc
fk_user_id_id -> user id by hospital. Probably used as a unique patient
                identifier. Id is typically extracted from DICOM files
                for a patient.

#### `rt_contour`
Stores the contour data to be overlaid over a given slice of a CT object
for a given patient.

Headers
id -> not needed, database assigned id for contour
ContourGeometricType -> from the DICOM object, typically "CLOSED PLANAR"
NumberOfContourPoints -> Number of points in the contour data. Used
                        to preallocate array to store contour data.
ContourData -> x y z points for a contour. All z coordinates should be 
                the same in a given contour as it will correspond with a 
                given slice
ReferencedSOPClassUID -> "CT Image Storage"
ReferencedSOPInstanceUID -> the CT image which the contour data is to be
                            overlaid on 
fk_roi_id_id -> id of ROI which the contour belongs to, database id
fk_structureset_id_id -> ID of RT Struct which the contour belongs to, database id


#### `rt_rois`
Stores the ROIs for a given RT Struct object

Headers
id -> not needed, ID assigned to an ROI from a given RT Struct object
ROIName -> Name of the ROI 
Volume -> volume of ROI (in what measurement?)
TotalContours -> How many 2D contours have been drawn for the ROI
fk_structureset_id_id -> RT Struct which the roi belongs to, database id
fk_patient_id_id -> patient to which the ROI belongs to
fk_series_id_id -> series to which the ROI belongs to
fk_study_id_id -> study to which the ROI belongs to
fk_user_id_id -> not needed
ROINumber -> directly extracted raw from the DICOM file. 

#### `rt_structureset`
This stores information on the ROIs in an RT STRUCT object

Headers
id -> unique id assigned by db for RT STRUCT
SOPInstanceUID -> DICOM UID for the RT structure object
SOPClassUID -> Defaults to "RT Structure Set Storage". Acts as a failsafe
                in making sure correct files are uploaded to the correct DB table.
TotalROIs -> Number of ROIs in RT Struct object
fk_patient_id_id -> DICOM id for the patient which the RT Struct belongs to
fk_series_id_id -> DICOM id for the series which the RT Struct belongs to
fk_study_id_id -> DICOM id for the study which the RT Struct belongs to
fk_user_id_id -> not needed

#### `series`
Stores the DICOM series ID for a given series of images. Types of series
include CT image series and RT structure series. Typically one study
will have multiple series in it. 

Headers
id -> database assigned id for the series
SeriesInstanceUID -> raw UID from the DICOM files for the series. All DICOM
                    files of the same series have the same SeriesInstanceUID
SeriesDate -> Date series was acquired. 
SeriesDescription -> Type of Series + manufacturer. For example, one might be
                    "Oncentra Structure Set"
SeriesType -> Either "CT" or "RTSTRUCT" typically
Modality -> raw field from DICOM file- either "CT" or "RTSTRUCT"
SeriesNumber -> raw field from DICOM file
PhysicianOfRecord -> Physician who was involved in acquiring DICOM series. From DICOM
                    files themselves.
Manufacturer -> who manufactured the device the DICOM series was acquired on. 
fk_patient_id_id -> DICOM id for the patient who the series belongs to
fk_study_id_id -> DICOM id for the study which the series belongs to
fk_user_id_id -> not needed?

#### `similarity`
This is used to store similarity values for the OVH, STS and target dose for 
a pair of patients. These values are generated by the Python scripts and 
stored here.

Headers
id -> not really needed, ID of similarity pair
DBStudyID -> The "Historical" patient in the pair. Typically at the time
    of this calculation, one of the patients is newly-uploaded, who is
    considered the current patient. The other patient in the pair is considered
    the historical patient. This is the study ID of the historical patient,
    from `studies`
Similarity -> Target Dose similarity (unsure)
OVHDissimilarity -> Similarity between two Overlap Volume Histograms for the two patients
STSDissimilarity -> Similarity between two Spatial Target Signature histograms
TargetOAR -> the OAR the OVH / STS are between, identified by id in `oar_dictionary`
fk_study_id_id -> the study ID of the current patient

#### `sts`
Stores values for the Spatial Target Signature Histogram for a specified patient.

Headers
id -> not really needed, unique id of STS histogram for a patient and given PTV-OAR pair in DB
elevation_bins -> amounts for the elevation bins in the STS histogram
distance_bins -> amounts for the distance bins in the STS histogram
azimuth_bins -> amounts for the azimuth bins in the STS histogram
amounts -> flattened array (unsure) storing the values for each (elevation, distance, azimuth)
            tuple. 
ptv_id -> id of primary target volume from `oar_dictionary`
OAR_id -> id of organ at risk from `oar_dictionary`
fk_study_id_id -> id of study (DICOM) from `studies` for which the STS histogram belongs to. 

#### `studies`
This stores which study belongs to which patient. 

Headers
id -> database assigned id for the study
StudyInstanceUID -> from a DICOM file, what the study UID is
StudyDate -> Extracted from DICOM file with specified StudyInstanceUID
StudyDescription -> What the study scanned for 
TotalSeries -> unsure
fk_patient_id_id -> DICOM patient ID for whom the study belongs to. 
fk_user_id_id -> unsure. This should probably not exist

#### `userprofile_userprofile`
This is general user information on each person.

Headers
id -> not really needed, id of metadata
occupation -> occupation of user by id
institution -> place where the user works
birthday -> user date of birth
location -> location where the user works
bio -> biographical statement on the user. For example,
        one might write. "Dr. something, formerly worked at UCLA,
        now works at Roswell Park as a Radiation Oncologist"
user_id -> id for which the profile information belongs, user id from
            `auth_user`.



#### TODO: 
* Permission to access patient data by Hospital
* Set up initial auth_groups for `UCLA Doctor`, `UCLA admin`, and later on,
    `Roswell Park Doctor`, `Roswell Park Admin`.
* Add features on GUI to add first name, last name to account
* Add features on GUI to change email address or password. 
* Add features on GUI to retire account. Retiring the account should force
    the user to also re-assign all patients that are only assigned to one doctor,
    and should only be performable by an admin or developer.
* Add features on GUI to be able to assign permissions to a user (only should be visible
from admin login)
* Differentiation between developer, superuser, admin and user
    * Developers should be able to see all hospitals but not patient info
    * Superusers should be able to see all hospitals and patient info
    * admins should be able to see patient info only for their hospital (+ admin
        privileges should only apply to patients / users from their hospital)
    * users should also have privileges which apply only to their hospital
* Add column to `patients` table that identifies to which hospital they belong. This
    may need to be accompanied by a new table that links each hospital against a
    unique id. `userprofile` may also need to link institution then by hospital id. 
* Determine whether patient name should be split into first/last name fields.
* should we link studies in `studies` by database or DICOM patient ID? database patient
    ID seems less prone to errors. 
* Purpose of `fk_user_id_id` in `studies` table?
* How are `amounts` in the `sts` table going to be stored? For a large histogram, we risk
    having to store at low precision to stay within data limits of the table. 
* Create parser to dump all UCLA patient data into the database. `patients`, `series`, all the
    tables the start with `rt`, `ct_images` and `studies` will need to be updated with raw
    data. `similarity` and `sts` and `ovh` will need to be updated with calculation
* Rerunning a calculation for `sts`, `ovh` or `similarity` should overwrite the calculation
    in the database. 
* Patient Dashboard GUI for both all types of users to view the patients they have been assigned
* A user should automatically be given rights to patients whose DICOM files they upload
* Add `ROI_ID` field to `rt_rois` table
* Dashboard for the Contour data for a given patient, DVH data and Isodose contours for a given patient
