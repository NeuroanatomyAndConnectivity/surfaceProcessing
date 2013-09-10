'''
Created on Aug 14, 2013

@author: surchs

Wrapper script to take care of business

Things I would like to do with this code:
1) Call the gradient generator
2) Correlate the gradient and the overlay
3) Make a GLM that tests an overlay file against 0 mean
4) Convert any file to any other file format
5) Have all of these options available as a commandline interface as well as a
   config option with a text file

'''
import os
import sys
import shutil
import numpy as np
import configure as cf
import surfaceProcessing as sp
from nibabel import freesurfer as nfs


def makeGradient():
    '''
    This method collects the necessary information to run the gradient script
    Running the script is done with condor to speed up processing

    The script needs these inputs:
        1) subject ID
        2) output directory - where the outputs are going to be stored
        3) smoothing - surface smoothing kernel

    At the moment, we still expect the files to be stored in the format
    specified by Alex (i.e. /scr/melisse1/NKI_enhanced/results/${subName}...

    I will make this more flexible once it is running
    '''
    # Stuff that should be supplied dynamically
    subjectListFile = cf.subjectListFile
    outPutDir = cf.gradientOutPutDir
    pathToScript = cf.pathToGradientScript
    condorDir = cf.condorDir
    condorName = cf.gradientCondorName
    logDir = os.path.join(condorDir, 'log')

    # Check if paths exist
    if not os.path.isdir(outPutDir):
        os.makedirs(outPutDir)
    if not os.path.isdir(condorDir):
        os.makedirs(condorDir)
    if not os.path.isdir(logDir):
        os.makedirs(logDir)

    # Load subject list
    f = open(subjectListFile, 'rb')
    subjectLines = f.readlines()
    f.close()

    subjectList = []
    for line in subjectLines:
        subject = line.strip()
        subjectList.append(subject)

    # Start generating the condor file
    condorStr = ''
    for subject in subjectList:
        # Put the arguments for the script in one string
        arguments = ('%s %s' % (subject, outPutDir))
        logFilePath = os.path.join(logDir, subject)
        # generate a temporary condor string and then append it
        tempStr = sp.fileops.genCondorString(pathToScript, arguments, logFilePath)
        condorStr = ('%s%s' % (condorStr, tempStr))

    condorOut = os.path.join(condorDir, condorName)
    condorOut = sp.fileops.saveTxt(condorOut, condorStr, 'submit')
    print('Written condor file at %s' % (condorOut))


def doSurfaceCorrelation():
    '''
    This method correlates two surfaces with one another within a certain
    radius and writes out the result as a third surface file

    The input format of all files should be mgh.
    The mask should be an overlay of zeroes and ones.

    Notes:
        To run the whole thing on individual labels, we need to specify the
        path to the label directory that contains the labels for the correct
        hemisphere and template. Then, we can cut out the appropriate part and
        store it in the file.

    Testing:
    - can I load the files that I have transformed with nibabel as morph files?
    '''
    # Stuff that should be defined dynamically elsewhere
    gradientTemp = cf.gradientTemp
    overlayTemp = cf.overlayTemp
    maskTemp = cf.maskTemp
    surfaceTemp = cf.surfaceTemp
    inputDir = cf.correlationInputDir
    radii = cf.radii
    hemispheres = cf.hemipsheres
    score = cf.score
    tempDir = cf.tempDir
    outDir = cf.correlationOutDir
    outName = cf.correlationOutName
    subjectListFile = cf.subjectListFile
    useAbsVals = cf.useAbsVals
    labelPath = None
    doLabel = cf.doLabel

    # Load subject list
    f = open(subjectListFile, 'rb')
    subjectLines = f.readlines()
    f.close()

    subjectList = []
    for line in subjectLines:
        subject = line.strip()
        subjectList.append(subject)

    # Load the label list
    f = open(labelPath, 'rb')
    labels = f.readlines()
    f.close()

    labelList = []
    for line in labels:
        label = line.strip()
    labelList.append(label)

    for hemi in hemispheres:
        if hemi == 'lh':
            altHemi = 'L'
        elif hemi == 'rh':
            altHemi = 'R'
        else:
            message = ('Your specified hemisphere (%s) is invalid. Ending' % (hemi))
            raise Exception(message)
        # Load the template, we only need it once
        surfacePath = (surfaceTemp % (hemi))
        surface = sp.fileops.loadSurface(surfacePath)

        for subID in subjectList:
            subDir = os.path.join(inputDir, subID)
            subOutDir = os.path.join(outDir, subID)

            if not os.path.isdir(subOutDir):
                os.makedirs(subOutDir)

            # Generate the paths that we want to look at
            gradientName = (gradientTemp % (subID, altHemi))
            overlayName = (overlayTemp % (subID, hemi))
            overlayName = ('%s.mgh' % overlayName)
            overlayPath = os.path.join(subDir, overlayName)

            maskPath = (maskTemp % (hemi))

            # Check if we have the overlay
            if not os.path.isfile(overlayPath):
                message = ('Could not find overlay at %s.\nQuitting!' % (overlayPath))
                raise Exception(message)

            # Check if we already have the gradient in mgh format
            gradientMgh = ('%s.mgh' % gradientName)
            gradientMghOutPath = os.path.join(subDir, gradientName)
            gradientMghPath = os.path.join(subDir, gradientMgh)
            if not os.path.isfile(gradientMghPath):
                # Get the oneD file
                gradientOneD = ('%s.1D' % (gradientName))
                gradientOneDPath = os.path.join(subDir, gradientOneD)
                if not os.path.isfile(gradientOneDPath):
                    message = ('Could not find either 1D or mgh gradient in %s\n(%s / %s)' % (subDir, gradientOneDPath, gradientMghPath))
                    raise Exception(message)
                # Generate the mgh file
                tempOneD = sp.fileops.loadVector(gradientOneDPath)
                tempOutName = ('%s_temp' % gradientName)
                tempOut = os.path.join(tempDir, tempOutName)
                outStr = sp.fileops.writeVector(surface, tempOneD, mode='ascii')
                savePath = sp.fileops.saveTxt(tempOut, outStr, 'asc',
                                              hemi=hemi)
                sp.fileops.convertMorphAsciiMgh(savePath, surfacePath,
                                                outType='mgh',
                                                outPath=gradientMghOutPath)

            # Get the files loaded
            gradient = sp.fileops.loadScalar(gradientMghPath)
            overlay = sp.fileops.loadScalar(overlayPath)
            if useAbsVals:
                overlay = np.abs(overlay)
            keepVerteces = sp.fileops.loadVector(maskPath, drop=2)

            # Construct a graph to represent the surface
            graph, numberVerteces = sp.procops.buildGraph(surface,
                                                          weighted=True)
            # Truncate the graph based on the mask
            truncGraph = sp.procops.keepNodes(graph, keepVerteces)

            # For each radius, correlate the two values
            for radius in radii:
                # Generate the distance dictionary for the current radius
                distanceDict = sp.procops.buildNeighbors(truncGraph, radius)
                vertVec = sp.procops.slideRoiValues(numberVerteces, keepVerteces,
                                                    distanceDict, gradient,
                                                    morphVec2=overlay, score=score)
                # Generate the output paths
                tempName = (outName % (subID, radius, hemi))
                saveName = (outName % (subID, radius, hemi))

                if doLabel:
                    # Get the label vector and take the average of the
                    # correlation map
                    #
                    # make a storage vector for the label processing
                    labelVec = np.zeros_like(vertVec)
                    for label in labelList:
                        # make label name
                        labelName = os.path.basename(label)
                        # read the label
                        labVec = nfs.read_label(label)
                        # use the indices to take a slice out of the overlay
                        sliceVec = vertVec[labVec]
                        # take the average of that slice
                        avgSlice = np.mean(sliceVec)
                        # and write it back into the appropriate verteces
                        labelVec[labVec] = avgSlice

                    # Adjust the names for the save files
                    tempName = ('%s_label' % tempName)
                    saveName = ('%s_label' % outName)

                    outVec = labelVec
                else:
                    # If we are not using label computation, just write the
                    # vertex-vise vector
                    outVec = vertVec

                # Generate the paths for the output
                tempOut = os.path.join(tempDir, tempName)
                saveOut = os.path.join(subOutDir, saveName)

                # Generate the output files
                outStr = sp.fileops.writeVector(surface, outVec, mode='ascii')
                savePath = sp.fileops.saveTxt(tempOut, outStr, 'asc',
                                              hemi=hemi)
                sp.fileops.convertMorphAsciiMgh(savePath, surfacePath,
                                                outType='mgh',
                                                outPath=saveOut)


def makeGlm():
    '''
    This method generates the necessary files for running a glm for testing
    a surface file across subjects against a mean of 0
    '''
    # Stuff to be supplied dynamically
    glmPrepDir = cf.glmPrepDir
    glmOutDir = cf.glmOutDir
    glmScriptTemp = cf.glmScriptName
    glmStackTemp = cf.glmStackName
    glmContrastTemp = cf.glmContrastName
    glmFsgdTemp = cf.glmDesigMatName

    searchDir = cf.correlationOutDir
    searchFile = cf.correlationOutName
    condorFile = cf.glmCondorName
    condorDir = cf.condorDir
    subjectListFile = cf.subjectListFile
    vertexThresh = cf.vertexThresh
    clustThresh = cf.clustThresh
    posneg = cf.posneg
    radii = cf.radii
    scriptDir = os.path.join(glmPrepDir, 'script')
    logDir = os.path.join(glmPrepDir, 'log')

    # See if the folders exist already, if not, create them
    if not os.path.isdir(glmPrepDir):
        os.makedirs(glmPrepDir)
    if not os.path.isdir(glmOutDir):
        os.makedirs(glmOutDir)
    if not os.path.isdir(scriptDir):
        os.makedirs(scriptDir)
    if not os.path.isdir(logDir):
        os.makedirs(logDir)

    # Load subject list
    f = open(subjectListFile, 'rb')
    subjectLines = f.readlines()
    f.close()

    subjectList = []
    for line in subjectLines:
        subject = line.strip()
        subjectList.append(subject)

    scriptList = []

    for radius in radii:
        for hemi in ['lh', 'rh']:
            fileList = []
            useList = []
            for subject in subjectList:
                # first find the appropriate file#
                fileName = (searchFile % (subject, radius, hemi))
                fileName = ('%s.mgh' % (fileName))
                subSearchDir = os.path.join(searchDir, subject)
                # subSearchDir = searchDir
                fileDir = sp.fileops.findFileAtPath(fileName, subSearchDir)
                if not fileDir:
                    print('Did not find subject %s %s rad %d' % (subject, hemi,
                                                                 radius))
                    # Leave this subject
                    continue
                useList.append(subject)
                fileList.append(fileDir)

            # Make the GLM stack
            glmStackName = (glmStackTemp % (radius, hemi))
            glmOut = os.path.join(glmPrepDir, glmStackName)
            glmOut = sp.fileops.stackFiles(fileList, glmOut)
            # Make the contrast
            contrastBaseName = (glmContrastTemp % (radius, hemi))
            contrastName = ('%s.mtx' % (contrastBaseName))
            contrastOut = os.path.join(glmPrepDir, contrastName)
            contrastOut = sp.fileops.genContrast(contrastOut)
            # Make the FSGD file
            fsgdGroupName = (glmFsgdTemp % (radius, hemi))
            fsgdOut = os.path.join(glmPrepDir, fsgdGroupName)
            fsgdOut = sp.fileops.genFsgdFile(useList, fsgdOut)

            # Generate the script to execute the whole shebang
            scriptName = (glmScriptTemp % (radius, hemi))
            scriptOut = os.path.join(scriptDir, scriptName)
            modelDir = os.path.join(glmOutDir, contrastBaseName)
            if not os.path.isdir(modelDir):
                os.makedirs(modelDir)
            shutil.copy2(glmOut, modelDir)
            glmStr = sp.fileops.genGlm(False, [contrastOut], fsgdOut, hemi,
                                            glmOut, modelDir, 'dods',
                                            vertexThresh, clustThresh, posneg)
            scriptOut = sp.fileops.saveTxt(scriptOut, glmStr, 'sh')
            os.chmod(scriptOut, 0775)
            scriptList.append(scriptOut)

    # Now add all the scripts to a condor script
    condorOut = os.path.join(condorDir, condorFile)
    condorStr = ''
    for scriptDir in scriptList:
        tempStr = sp.fileops.genCondorString(scriptDir, '', logDir)
        condorStr = ('%s\n%s' % (condorStr, tempStr))

    condorOut = sp.fileops.saveTxt(condorOut, condorStr, 'submit')
    print('Written condor file at %s' % (condorOut))


def convertFile():
    '''
    This method is supposed to convert any input file to any other file type

    Conversions that I can do at the moment:
        - mgh morphometry to
            - AFNI 1D Vector
            - AFNI niml.dset
            - numpy vector save
        - AFNI 1D Vector
            - mgh morphometry
            - AFNI niml.dset
        - Gifti Surface
            - mgh surface
        - Gifti Morphometry
            - mgh morphometry
            - AFNI niml.dset (2)
    '''
    # Stuff to be supplied dynamically
    inFilePath = ''
    inFileType = ''
    outFileName = ''
    outPath = ''
    outFileType = ''
    allowedType = ['mgh_morph', 'mgh_surf',
                   'anfi_1d', 'afni_niml',
                   'gifti_morph', 'gifti_surf']

    # Make a quick check if the file types conform to the allowed types
    if not inFileType in allowedType:
        message = ('The specified input type (%s) is not supported' % (inFileType))
        raise Exception(message)

    if not outFileType in allowedType:
        message = ('The specified output type (%s) is not supported' % (outFileType))
        raise Exception(message)

    # Decide what to do
    if inFileType == 'afni_1d':
        if outFileType == 'mgh_morph':
            pass
        elif outFileType == 'afni_niml':
            pass
        pass

    elif inFileType == 'mgh_morph':
        if outFileType == 'afni_1d':
            pass
        elif outFileType == 'afni_niml':
            pass
        pass

    elif inFileType == 'gifti_surf':
        if outFileType == 'mgh_surf':
            pass
        pass

    elif inFileType == 'gifti_morph':
        if outFileType == 'mgh_morph':
            pass
        elif outFileType == 'afni_niml':
            pass
        pass

    else:
        message = ('I don\'t understand the input file type \'%s\'' % (inFileType))
        raise Exception(message)

    pass


if __name__ == '__main__':
    welcomeString = ('Hi, this is the wrapper for the surface processing'
                     + ' scripts\nTo begin, you should manually edit the'
                     + ' configure.py file, located in this directory.\n'
                     + 'Once you have set up the configure.py file, start'
                     + ' the wrapper by adding one of these arguments:\n'
                     + '    \'gradient\' - creates the gradient files\n'
                     + '    \'surface\' - do the surface computation\n'
                     + '    \'glm\' - run the glm on the surface'
                     + ' computation outputs\n'
                     + 'Supply no argument to see this message.')
    if len(sys.argv) == 1:
        # Somebody just started the thing without supplying arguments
        print(welcomeString)
    elif len(sys.argv) > 2:
        message = 'You supplied too many arguments, I can only handle one'
        raise Exception(message)
    else:
        if sys.argv[1] == 'gradient':
            makeGradient()
        elif sys.argv[1] == 'surface':
            doSurfaceCorrelation()
        elif sys.argv[1] == 'glm':
            makeGlm()
        else:
            message = ('I did not understand the argument of %s' % (sys.argv[1])
                       + '\nI will print the helpfile now:\n\n')
            print(message)
            print(welcomeString)
