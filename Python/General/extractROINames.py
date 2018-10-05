
def preprocess_roi_name_ucla(name):
    """
    Preprocesses a name based on studying
    the 10 bladder cancer cases from UCLA

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
    return roi_name