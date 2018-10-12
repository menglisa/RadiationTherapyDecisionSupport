
def preprocess_roi_name_ucla(name):
    """
    Preprocesses a name based on studying
    the 10 bladder cancer cases from UCLA and
    the several head and neck and cancer cases too 

    Parameters
    ----------
    name : str
        The raw ROI name from the DICOM file
    
    Returns
    -------
    roi_name : str
        The processed ROI name
    """
    roi_name = name.lower()
    roi_name = roi_name.replace("_", "").strip()

    # preprocess different ways of writing left femoral head , right femoral head
    # preprocess out underscores
    # preprocess - think seminal vesicle and sv are the same
    if roi_name == "l femoral head" or roi_name == "lt fmrl head" or roi_name == "lt femrl head" or roi_name == "l femrl head":
        roi_name = "left femoral head"
    elif roi_name == "r femoral head" or roi_name == "r femrl head" or roi_name == "rt femrl head":
        roi_name = "right femoral head"
    elif roi_name == "sv":
        roi_name = "seminal vesicle"
    
    
    roi_name_original = roi_name
    roi_name = roi_name.replace(" ", "")
    # Preprocess the head and neck cancer names
    if roi_name == "cord+5mm" or roi_name == "cord+5" or roi_name=="cordplus5mm" or roi_name=="cordand5mm" or roi_name == "opti+cord +5mm":
        roi_name_original = "cord + 5mm"
    elif roi_name == "optiltprtd" or roi_name == "optiltparotid" or roi_name == "optiprtdlt" or roi_name == "optiprtlt":
        roi_name_original = "opti parotid left"
    elif roi_name == "postavoidance" or roi_name == "postavoid":
        roi_name_original = "post avoidance"
    elif roi_name == "medavoid" or roi_name == "medialaviod" or roi_name == "medialavoid" or roi_name == "medial_avoid":
        roi_name_original = "medial avoid"
    elif roi_name == "gpetpositive":
        roi_name_original = "gpet positive"
    
    return roi_name_original