.. Radiation Therapy Decision Support documentation master file, created by
   sphinx-quickstart on Sat Oct 28 15:25:47 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Radiation Therapy Decision Support Documentation
================================================

This page contains API documentation from all functions in RadiationTherapyDecisionSupport
project. 


General Functions
=================

Designed to be reused between categories of function (OVH, STS, Similarity).

.. toctree::
   :maxdepth: 3
   :caption: Contents:

.. automodule:: utils

.. autofunction:: getVolume
.. autofunction:: getContours
.. autofunction:: getIsodose
.. autofunction:: getMeanTargetDose
.. autofunction:: getImageBlock
.. autofunction:: convertROIToCTSpace
.. autofunction:: _convertIsodoseCoordinates


OVH Functions
=============

Functions specific to computing the overlap volume histogram (OVH) for a given
Primary target volume (PTV) and a single organ at risk (OAR)


.. automodule:: ovh

.. autofunction:: getHistogram
.. autofunction:: getNormalizedHistogram
.. autofunction:: getOVHDistances
.. autofunction:: getOVH


STS Functions
=============

Functions specific to computing the Spatial Transform Signature (STS) for a given
Primary target volume (PTV) and a single organ at risk (OAR)


.. automodule:: sts

.. autofunction:: getSTSHistogram
.. autofunction:: getDistance
.. autofunction:: getElevation
.. autofunction:: getAzimuth
.. autofunction:: getCentroid


Similarity Functions
====================

Functions designed to compute the earth mover's distance between OVH histograms and STS Histograms,
and the absolute difference between target doses.


.. automodule:: similarity

.. autofunction:: getOVHEmd
.. autofunction:: getSTSEmd
.. autofunction:: getTDDistance



DataFetcher Class
=================

Class designed to facilitate easy connection to the remote MySQL database.


.. automodule:: DataFetcher




__init__ AlgoManager Class
==========================

Class designed to wrap the OVH, STS and similarity functions.

..automodule:: __init__











