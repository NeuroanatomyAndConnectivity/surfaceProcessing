'''
Created on Aug 15, 2013

@author: surchs

Configuration file.

This file contains all the parameters that have to be set in order to run
the surface level scripts correctly

The sections correspond to the three different processing steps that are
currently implemented. It is advisable to set all parameters before running
even a subset of the processing as there are some cross-dependencies
'''

#===============================================================================
# General Configuration
#===============================================================================
# full path to a textfile containing only subject names
subjectListFile = '/scr/kansas1/surchs/testSurface/subjects.txt'
# a python list containing the hemispheres to run on (like so: ['lh', 'rh'])
hemipsheres = ['lh', 'rh']
# a python list containing the radii for the sliding window (like so: [3, 6])
radii = [3, 6, 9, 12]
# full path to a temporary directory (file conversion temp files are dumped)
tempDir = '/scr/kansas1/surchs/testSurface/temp'

#===============================================================================
# Condor Configuration
#===============================================================================
# full path to a directory where the condor submit files will be saved
condorDir = '/scr/kansas1/surchs/testSurface/condor'

#===============================================================================
# Gradient Configuration
#===============================================================================
# full path to the script that runs the gradient generation - you will have
# to download these scripts separately and also set execution permission
pathToGradientScript = '/scr/kansas1/surchs/testSurface/scripts/runGradientForNifti.sh'
# full path to the output directory for the gradients (each subject will be
# in a separate sub-directory)
gradientOutPutDir = '/scr/kansas1/surchs/testSurface/gradienOut'
# name for the condor submit file for the gradient calculation
gradientCondorName = 'run_gradients'

#===============================================================================
# Surface Correlation Configuration
#===============================================================================
# name template for the gradient file - best to be left untouched as this is
# hardcoded in the gradient scripts ('%s_rfMRI_gradient.%s')
gradientTemp = '%s_rfMRI_gradient.%s'
# name template for the overlay, curvature and sulci information are available
# in the gradient directory
overlayTemp = 'sulc_%s_%s2fsaverage5_6'
# full path to the directory where the gradients and overlays are stored in
# subdirectories for each subject - should be equivalent to the output dir
# for the gradient generation. you can also specify a full path
correlationInputDir = gradientOutPutDir
# full path to the output directory where the surface processing will be saved
# in subdirectories for each subject
correlationOutDir = '/scr/kansas1/surchs/testSurface/corr'

# name template for the surface file - the %s part get's replaced with the
# appropriate hemisphere - best to be left untouched for now
surfaceTemp = '/afs/cbs.mpg.de/software/freesurfer/5.1.0/amd64/2.15/subjects/fsaverage5/surf/%s.inflated'
# same as with surface template
maskTemp = '/afs/cbs.mpg.de/software/freesurfer/5.1.0/amd64/2.15/subjects/fsaverage5/label/%s.cortex.label'

# score that is used for the surface computation. There are a number of scores
# available, refer to the readme file for a list
score = 'zspear'

# Set this to true if you want to use the absolute values of the overlay
useAsbVals = True

# name template for the output of the surface computation
correlationOutName = '%s_correlation_%d_%s'

#===============================================================================
# GLM Configuration
#===============================================================================
# full path to the directory where the glm files are prepared (design matrix...)
glmPrepDir = '/scr/kansas1/surchs/testSurface/glm_prep'
# full path to the directory where the glm outputs will be saved
glmOutDir = '/scr/kansas1/surchs/testSurface/glm_out'

# A set of name templates for glm related files - %d gets replaced with the
# radius, %s with the hemisphere
glmStackName = 'glmStack_node_gradsulc_%d_%s.mgh'
glmContrastName = 'contrast_node_gradsulc_%d_%s'
glmDesigMatName = 'fsgd_node_gradsulc_%d_%s.fsgd'
glmScriptName = 'script_node_gradsulc_%d_%s'

# parameters for cluster level correction of the glm results
vertexThresh = '0.99'
clustThresh = '0.05'
posneg = 'both'

# name for the glm condor file
glmCondorName = 'runall_fsaverage5_node_correlation'

