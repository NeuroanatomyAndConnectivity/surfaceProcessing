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
import os


def makePaths(inputs, outputs):
    '''
    This method is here to ensure that all input paths exist and all output
    paths are generated where necessary
    '''
    # inputs
    inBreak = False
    for inPath in inputs:
        if not os.path.isdir(inPath) or not os.path.isfile(inPath):
            print('Input %s does not exist' % (inPath))
    if inBreak:
        message = 'not all inputs were satisfied. Cannot start'
        raise Exception(message)

    # outputs
    for outPath in outputs:
        if not os.path.isdir(outPath):
            print('Creating output path %s now' % (outPath))
            os.makedirs(outPath)


#===============================================================================
# General Configuration
#===============================================================================
# full path to a textfile containing only subject names
subjectListFile = '/scr/kansas1/surchs/testSurface/subjects.txt'
# a python list containing the hemispheres to run on (like so: ['lh', 'rh'])
hemipsheres = ['lh', 'rh']
# a python list containing the radii for the sliding window (like so: [3, 6])
radii = [3, 6, 9, 12]
# full path to the base directory - if not specified otherwise, all other paths
# are generated as subdirectories of this one
baseDir = '/scr/kansas1/surchs/testSurface'
# full path to the template directory - the templates are expected to be full
# freesurfer sets stored as subdirectories to this path and with their name as
# the directory name
templateDir = '/afs/cbs.mpg.de/software/freesurfer/5.1.0/amd64/2.15/subjects/'
# full path to the auxiliary script directory
scriptDir = '/scr/kansas1/surchs/testSurface/scripts'


# set this variable to True if you want to work on the level of individual
# cortical regions as defined by freesurfer label files
doLabel = True

# full path to temporary working directory
tempDir = os.path.join(baseDir, 'temp')
# full path to the log directory
logDir = os.path.join(baseDir, 'log')
# full path to the directory where the condor scripts will be stored
condorScriptDir = os.path.join(baseDir, 'scripts')
# full path to the directory where the labels will be unpacked if applicable
labelDir = os.path.join(baseDir, 'labels')
labelScript = 'unpackLabels.sh'
pathToLabelScript = os.path.join(scriptDir, labelScript)

#===============================================================================
# Condor Configuration
#===============================================================================
# full path to a directory where the condor submit files will be saved
condorDir = os.path.join(tempDir, 'condor')

#===============================================================================
# Gradient Configuration
#===============================================================================
# full path to the script that runs the gradient generation - you will have
# to download these scripts separately and also set execution permission
gradientScript = 'runGradientForNifti.sh'
# name for the condor submit file for the gradient calculation
gradientCondorName = 'run_gradients'

# full path to the output directory for the gradients (each subject will be
# in a separate sub-directory)
gradientOutPutDir = os.path.join(baseDir, 'gradientOut')
# full path to the script that computes the gradient maps
pathToGradientScript = os.path.join(scriptDir, gradientScript)

#===============================================================================
# Surface Correlation Configuration
#===============================================================================
# name template for the gradient file - best to be left untouched as this is
# hardcoded in the gradient scripts ('%s_rfMRI_gradient.%s')
gradientTemp = '%s_rfMRI_gradient.%s'
# name template for the overlay, curvature and sulci information are available
# in the gradient directory
overlayTemp = 'sulc_%s_%s2fsaverage5_6'

# name template for the surface file - the %s part get's replaced with the
# appropriate hemisphere - best to be left untouched for now
templateName = 'fsaverage5'
# specify the surface rendering of the template (inflated, pial, white, sphere)
templateSurface = 'inflated'

# score that is used for the surface computation. There are a number of scores
# available, refer to the readme file for a list
score = 'zspear'

# Set this to true if you want to use the absolute values of the overlay
useAbsVals = True

# name template for the output of the surface computation
# the placeholders get filled out like this (subject nami, radius, hemisphere)
correlationOutName = '%s_correlation_%d_%s'


# full path to the directory where the gradients and overlays are stored in
# subdirectories for each subject - should be equivalent to the output dir
# for the gradient generation. you can also specify a full path
correlationInputDir = gradientOutPutDir
# full path to the output directory where the surface processing will be saved
# in subdirectories for each subject
correlationOutDir = os.path.join(baseDir, 'corrOut')

# do not change this, this is part of a fixed template
templateTemp = '%%s.%s' % (templateSurface)
# only change the next line if you want to specify the full path to a freesurfer
# surface manually
templatePath = os.path.join(templateDir, templateName, 'surf', templateTemp)

# same goes for the template mask file - only change if you have a full manual
# path
maskTemp = os.path.join(templateDir, templateName, 'label', '%s.cortex.label')

# set the path to the label file
labelPath = os.path.join(labelDir, 'labelFile.txt')

#===============================================================================
# GLM Configuration
#===============================================================================
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

# full path to the directory where the glm files are prepared (design matrix...)
glmPrepDir = os.path.join('glmPrep')
# full path to the directory where the glm outputs will be saved
glmOutDir = os.path.join('glmOut')

#===============================================================================
# Call the path checkin function
#===============================================================================
inputs = [scriptDir, templateDir, pathToGradientScript, pathToLabelScript,
          subjectListFile]

outputs = [condorDir, glmPrepDir, glmOutDir, correlationOutDir,
               gradientOutPutDir, labelDir, logDir, tempDir]

makePaths(inputs, outputs)


