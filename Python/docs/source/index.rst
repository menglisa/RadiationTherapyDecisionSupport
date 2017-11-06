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
.. autofunction:: getImageBlock



OVH Functions
=============

Functions specific to computing the overlap volume histogram (OVH) for a given
Primary target volume (PTV) and a single organ at risk (OAR)


.. automodule:: ovh

.. autofunction:: getHistogram
.. autofunction:: getNormalizedHistogram
.. autofunction:: getOVHDistances

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
