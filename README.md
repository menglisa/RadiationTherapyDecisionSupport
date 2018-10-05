# Radiation Therapy Decision Support

This readme is designed to highlight aspects of the development of 
this project in Python.

1) Modules Used + Versions
2) Virtual Machine (and how to pull Repo this to the VM)
3) Documentation
4) Tests
5) TODO

## Modules Used + Versions

One of the main differences between MATLAB and python is that in
Python, functions are determined by installable modules. The
versions and installed modules each developer has should
be the same so that code written by one developer can be used by
all.  

Tentatively, these modules will be used:

* [Numpy](www.numpy.org) - For utilizing arrays in Python- v.1.13
* [PyDicom](https://github.com/pydicom/pydicom)- For reading
DICOM files - v0.99
* [MatPlotLib](matplotlib.org) - For plotting graphs (OVH, DVH, etc)- v2.0.2
* [OpenCV](opencv.org/opencv-3-0.html) - For image processing functions- v3.x
* [Scipy](https://www.scipy.org) - For showing images- version not specified
* [Scikit-Image](scikit-image.org) - For additional image processing functions - v1.13
* [Sphinx](www.sphinx-doc.org) - So that I can compile pdf documentation- version not specified
* [Numpydoc](https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt)
Sort of an extension to Sphinx, allows us to write documentation in the code itself - version not specified
* [Jupyter Notebook](jupyter.readthedocs.io/en/latest/install.html) - For showing results of python functions in
html-like file.
* [pymysql](https://pymysql.readthedocs.io/en/latest/) - To connect to the MySQL server that stores intermediate
data for the program
* [sshtunnel](https://sshtunnel.readthedocs.io/en/latest/) - For connecting to the remote server where the MySQL
database is stored

#### The Version of Python To Use

Two versions of Python exist- Python 2.x (2.7) and 3.x. While some
py files can be run effectively in both versions, it is best to test
your code in Python 3.x as that is the version on the VM that
will run with Jupyter Notebook. 

To run python functions in Python 3 in the terminal type:
```bash
$ python3 FILENAME.py
```

## Virtual Machine (and how to pull Github Repo to VM)

Some of the modules are difficult to install, particularly OpenCV
which, as a primarily C-based library, requires compilation. I 
provide a VM on Google Drive for your use. It has all the modules installed on it,
with correct versions. It also has the text editor sublime for editing files in drive.

Link to Google Drive folder with VM is [here](https://drive.google.com/drive/folders/0ByJci3kRjjbsbmRGeDlvNko5Ulk?usp=sharing)

(You will need to be signed into a USC edu account for access)

You can then download the VM, and import it into Oracle VirtualBox.

The virtual machine contains a single user account ``radiation``. The 
password for the account is also ``radiation`` if needed (e.g. for running
``sudo`` command in terminal). 

*Note* You may need to enable Virtualization for the virtual machine to work. In windows 10 [this link](https://answers.microsoft.com/en-us/windows/forum/windows_10-other_settings-winpc/cannot-find-the-option-to-enable-intel-vt-x-in/c9203f8a-da57-43be-8c75-cfe43d55cd70) should tell you how to set that up.

In order to get this github repo on the VM, please run the following commands at the terminal:

```shell
git clone https://github.com/vvmurthy/RadiationTherapyDecisionSupport
cd RadiationTherapyDecisionSupport 
git remote rename origin upstream
git remote add origin https://github.com/<github_username>/RadiationTherapyDecisionSupport
```

As an example, I would clone a repo for the GitHub account `SlevinZhang` using
```
git clone https://github.com/vvmurthy/RadiationTherapyDecisionSupport
cd RadiationTherapyDecisionSupport 
git remote rename origin upstream
git remote add origin https://github.com/SlevinZhang/RadiationTherapyDecisionSupport
```

What these commands will do is allow you to update the shared repository
by using:
```shell
git add -A
git commit -m "COMMIT_COMMENT_HERE"
git push upstream master

```

or your own fork of the repo by using 

```shell
git add -A
git commit -m "COMMIT_COMMENT_HERE"
git push origin master
```

NOTE: The first time you do a commit on the VM,
you will need to run the following functions prior
to ``git commit``:
```shell
git config --global user.email "YOUR_GITHUB_EMAIL"
git config --global user.name "YOUR_ACTUAL_NAME"
```

Occasionally, you will need to update your own personal fork of this repo with the edits pushed onto the shared repo by others.
You can do this using the command:

```shell
git pull upstream master
```

If your edits are major and currently buggy, it is probably best
not to push to the shared repo, hence the command to push to your own
fork.

To develop the python function, you can run 

```bash
subl NAME_OF_FILE.py
```

or you can develop the files in jupyter notebook by running
```bash
jupyter notebook
```

at the terminal. When you confirm that your function's output
is correct, then it can be converted to a .py file.

## Data

Download the data from [This link](https://drive.google.com/drive/folders/1YwzKKxY9evcj_MxbuCr-RSCuN3CwmUAt?usp=sharing).
Do note that the cases `UCLA_PR_26` and `UCLA_PR_27` are corrupted, so they cannot be accessed. 

## Documentation

One of the main drawbacks of the MATLAB code is that we have no
way of knowing what is a draft and what is final code, nor what
each function needs in terms of params.

Once your code is developed, it is good
practice to write a small string below the function define statement
describing what it does. Please follow the format of the example near
exactly because this will help me compile a pdf / html file of all docs
later on.

An example would be
```python
def squared(x):
    """
    returns the square of a number ( x ** 2)

    Parameters
    ----------
    x : double
        The input to be squared

    Returns
    -------
    square : double
        The input squared (x ** 2)
    """
    
    square = x * x
    return square

```

This may seem a little excessive now, but for functions more complex
than pure python (e.g. those that require numpy, OpenCV) writing documentation
will help anyone reading the code months from now.

## Tests

One of the main drawbacks with the MATLAB code is that we have
no way to test it. We should attempt to avoid similar scenario with
the Python files.

Because of this, it is generally a good idea to write / draft
your functions in jupyter notebook to confirm they work as intended.
Then you can copy them to a py file for use in program.

See `getContours.ipynb` for an example- the inputs are loaded in the notebook, 
passed to the function defined in `getContours.py`, then
the results are displayed in the notebook again.
