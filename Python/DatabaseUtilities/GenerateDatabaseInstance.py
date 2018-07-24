import MySQLdb as ms


def generate_database_instance(IP, USER, PASSWORD, DB_NAME):
    """
    Generates a database and the Django framework permissions
    
    
    Parameters
    ----------
    IP : String
        IP address to connect to mysql on
    USER : String
        Username for MySQL
    PASSWORD : String
        Password for MySQL
    DB_NAME : String
        Name for the created database. Typically "dsrt" 
    """
    
    # Connect to server
    db1 = ms.connect(host=IP, user=USER, password=PASSWORD)
    cur = db1.cursor()
    try:    
        cur.execute("CREATE DATABASE " + DB_NAME)
    except Exception:
        print("Database exists")
    cur.execute("use " + DB_NAME + ";")
    
    # Add tables to MySQL DB
    tables = []
    table = "auth_group (name VARCHAR(80), id INT(11));"
    tables.append(table)
    table = "auth_group_permissions (id INT(11), group_id INT(11), permission_id INT(11));"
    tables.append(table)
    table = "auth_permission (id INT(11), name VARCHAR(255), content_type_id INT(11), codename VARCHAR(100));"
    tables.append(table)
    table = "auth_user (id INT(11), password VARCHAR(128), last_login DATETIME, is_superuser TINYINT(1), \
    username VARCHAR(150), first_name VARCHAR(30), last_name VARCHAR(30), email VARCHAR(254), is_staff TINYINT(1), \
    is_active TINYINT(1), date_joined DATETIME);"
    tables.append(table)
    table = "auth_user_user_permissions (id INT(11), user_id INT(11), permission_id INT(11));"
    tables.append(table)
    table = "ct_images (id INT(11), SOPInstanceUID VARCHAR(200), SOPClassUID VARCHAR(100), \
    ImageType VARCHAR(100), PhotometricInterpretation VARCHAR(20), RescaleSlope INT(11), \
    RescaleIntercept INT(11), SliceLocation INT(11), PixelSpacing VARCHAR(50), ImageOrientationPatient VARCHAR(100), \
    ImagePositionPatient VARCHAR(100), SliceThickness VARCHAR(100), BodypartExamined VARCHAR(100), \
    Rows INT(11), Columns INT(11), fk_patient_id_id INT(11), fk_series_id_id INT(11), \
    fk_study_id_id INT(11), fk_user_id_id INT(11));"
    tables.append(table)
    table = "django_admin_log (id INT(11), action_time DATETIME, object_id LONGTEXT, object_repr VARCHAR(200), \
    action_flag SMALLINT(5) UNSIGNED, change_message LONGTEXT, content_type_id INT(11), user_id INT(11))"
    tables.append(table)
    table = "django_content_type (id INT(11), app_label VARCHAR(100), model VARCHAR(100))"
    tables.append(table)
    table = "django_migrations (id INT(11), app VARCHAR(255), name VARCHAR(255), applied DATETIME)"
    tables.append(table)
    table = "django_session (session_key VARCHAR(40), session_data LONGTEXT, expire_date DATETIME)"
    tables.append(table)
    table = "oar_dictionary (id INT(11), ROIName VARCHAR(100), ROIDisplayColor VARCHAR(100));"
    tables.append(table)
    table = "ovh (id INT(11), binValue LONGTEXT, binAmount LONGTEXT, OverlapArea INT(11), ptv_id INT(11), \
    OAR_id INT(11), fk_study_id_id INT(11));"
    tables.append(table)
    table = "patients (id INT(11), PatientName VARCHAR(200), BirthDate DATE, Gender VARCHAR(20),\
    EnthicGroup VARCHAR(200), fk_user_id_id INT(11));"
    tables.append(table)
    table = "rt_contour (id INT(11), ContourGeometricType VARCHAR(100), NumberOfContourPoints INT(11), \
    ContourData LONGTEXT, ReferencedSOPClassUID VARCHAR(100), ReferencedSOPInstanceUID VARCHAR(100), \
    fk_roi_id_id INT(11), fk_structureset_id_id INT(11));"
    tables.append(table)
    table = "rt_dose (id INT(11), SOPClassUID VARCHAR(100), SOPInstanceUID VARCHAR(100), DoseGridScaling VARCHAR(100), \
    DoseSummationType VARCHAR(100), DoseType VARCHAR(100), DoseUnits VARCHAR(100), referencedRTPlanSequence VARCHAR(100), \
    ReferencedStructureSetSequence VARCHAR(100), fk_patient_id_id INT(11), fk_series_id_id INT(11), \
    fk_study_id_id INT(11), fk_user_id_id INT(11));"
    tables.append(table)
    table = "rt_dose_image (id INT(11), columns INT(11), rows INT(11), ImageOrientationPatient VARCHAR(20), \
    ImagePositionPatient VARCHAR(20), PhotometricInterpretation VARCHAR(20), PixelSpacing VARCHAR(20), \
    NumberOfFrames INT(11), ImageData LONGTEXT, fk_dose_id_id INT(11), fk_patient_id_id INT(11), \
    fk_series_id_id INT(11), fk_study_id_id INT(11), fk_user_id_id INT(11));"
    tables.append(table)
    table = "rt_dvh (id INT(11), DVHDoseScaling VARCHAR(20), DVHMaximumDose DOUBLE, DVHMeanDose DOUBLE, \
    DVHMinimumDose DOUBLE, DVHReferencedROI VARCHAR(10), DVHType VARCHAR(10), DVHVolumeUnits VARCHAR(10), \
    DoseType VARCHAR(10), DoseUnits VARCHAR(10), DVHData LONGTEXT, fk_dose_id_id INT(11), \
    fk_patient_id_id INT(11), fk_series_id_id INT(11), fk_study_id INT(11), fk_user_id_id INT(11));"
    tables.append(table)
    table = "rt_isodose (id INT(11), RowPosition LONGTEXT, ColumnPosition LONGTEXT, IsDoseValue INT(11), \
    fk_ct_image_id_id INT(11), fk_dose_id_id INT(11), fk_patient_id_id INT(11), fk_series_id_id INT(11), \
    fk_study_id_id INT(11));"
    tables.append(table)
    table = "rt_rois (id INT(11), ROIName VARCHAR(100), Volume DOUBLE, TotalContours INT(11), \
    fk_structureset_id_id INT(11), fk_patient_id_id INT(11), fk_series_id_id INT(11), fk_study_id_id INT(11), \
    fk_user_id_id INT(11), ROINumber VARCHAR(200));"
    tables.append(table)
    table = "rt_structureset (id INT(11), SOPInstanceUID VARCHAR(200), SOPClassUID VARCHAR(200), TotalROIs INT(11), \
    fk_patient_id_id INT(11), fk_series_id_id INT(11), fk_study_id_id INT(11), fk_user_id_id INT(11));"
    tables.append(table)
    table = "series (id INT(11), SeriesInstanceUID VARCHAR(200), SeriesDate DATE, SeriesDescription VARCHAR(200), \
    SeriesType VARCHAR(100), Modality VARCHAR(100), SeriesNumber VARCHAR(100), PhysicianOfRecord VARCHAR(100), \
    Manufacturer VARCHAR(50), fk_patient_id_id INT(11), fk_study_id_id INT(11), fk_user_id_id INT(11));"
    tables.append(table)
    table = "similarity (id INT(11), DBStudyID VARCHAR(100), Similarity DOUBLE, OVHDissimilarity DOUBLE, \
    STSDissimilarity DOUBLE, TargetOAR VARCHAR(200), fk_study_id_id INT(11));"
    tables.append(table)
    table = "sts (id INT(11), elevation_bins LONGTEXT, distance_bins LONGTEXT, azimuth_bins LONGTEXT, \
    amounts LONGTEXT, ptv_id INT(11), OAR_id INT(11), fk_study_id_id INT(11));"
    tables.append(table)
    table = "studies (id INT(11), StudyInstanceUID VARCHAR(200), StudyDate DATE, StudyDescription VARCHAR(200), \
    TotalSeries INT(11), fk_patient_id_id INT(11), fk_user_id_id INT(11));"
    tables.append(table)
    table = "userprofile_userprofile (id INT(11), occupation VARCHAR(30), institution VARCHAR(30), \
    birthday DATE, location VARCHAR(30), bio LONGTEXT, user_id INT(11));"
    tables.append(table)

    already_created_tables = 0
    for table in tables:
        try:
            cur.execute("CREATE TABLE " + table)
        except Exception:
            already_created_tables += 1
            print("Table " + table.split(" ")[0] + " already exists")
    print("created tables: " + str(len(tables) - already_created_tables))
    inserts = []

    # Create Django permissions
    permissions = ("logentry", "permission", "group", "user", "contenttype", "session", \
                  "patient", "study", "series", "ctimages", "rtstructureset", \
                  "roi", "rtroi", "rtcontour", "rtdose", "rtdoseimage", "rtdvh", \
                  "rtisodose", "ovh", "sts", "similarity", "userprofile")

    for i, permission in enumerate(permissions):
        for action in ["add ", "change ", "delete "]:
            insert = (str(i + 1), action + permission)
            inserts.append(insert)

    for i, insert in enumerate(inserts):
        cur.execute("select 1 from auth_permission where codename='" + insert[1] + "'")
        if len(cur.fetchall()) < 1:
            statement = "('" + str(i + 1) + "', 'can " + insert[1] + "', '" \
                + insert[0] + "', '" + insert[1] + "');"
            cur.execute("INSERT INTO auth_permission VALUES " + "('" + insert[0] + "', 'can " + insert[1] + "', '" \
                + insert[0] + "', '" + insert[1] + "');")