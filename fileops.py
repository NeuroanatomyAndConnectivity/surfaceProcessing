'''
Created on Jul 18, 2013

@author: surchs

lot's of stuff to load and process surface data

stuff I want to have here:
- loading of any surface related files
- saving of any surface related files (also conversion to other file formats)
- conversion of files into standard data formats (if this will be necessary)
'''
import os
import subprocess
import numpy as np
from surfer import io
import surfaceProcessing as sp
from nibabel import freesurfer as nfs


#===============================================================================
#----------------------------------------------------------------- Loading Files
#===============================================================================
def loadScalar(pathToScalar):
    '''
    Method to read scalar vectors for example in mgh format
    '''
    outVec = io.read_scalar_data(pathToScalar)

    return outVec


def loadVector(pathToVector, drop=0):
    '''
    Loads a vector like a text file and returns a numpy array
    '''
    valList = []
    f = open(pathToVector, 'rb')
    for i in xrange(drop):
        tempVal = f.readline()
    values = f.readlines()
    f.close()

    for value in values:
        valList.append(float(value.strip().split(' ')[0]))

    outVec = np.array(valList)

    return outVec


def loadSurface(pathToSurface):
    '''
    This method loads the surface from a mgh file and returns it. Pretty simple
    stuff
    '''
    print('Loading %s' % (pathToSurface))
    surface = nfs.read_geometry(pathToSurface)

    return surface


def loadLabel(pathToLabel, drop=2):
    '''
    load the label text file
    '''
    f = open(pathToLabel, 'rb')
    for i in xrange(drop):
        f.readline()
    lines = f.readlines()
    f.close()

    verteces = []
    for line in lines:
        useLine = line.strip().split()
        if sp.tools.isNumber(useLine[0]):
            verteces.append(float(useLine[0]))

    return lines, verteces


def loadAnnotation(pathToAnnotation):
    '''
    This loads an annotation file. Format is:
    [0]    - vector of values (len#verteces)
    [1]    - coordinates of annotations... (not sure)
    [2]    - list of names for annotations
    '''
    annot = nfs.read_annot(pathToAnnotation)

    return annot


def loadMorphometry(pathToMorphometry):
    '''
    This loads a morphometry file, like thickness
    '''
    print('Loading %s' % (pathToMorphometry))
    morphometry = nfs.read_morph_data(pathToMorphometry)

    return morphometry


def loadGiftiMorphometry(pathToMorphometry):
    '''
    This loads a gifti morphometry file and turns it into something readable
    '''
    f = open(pathToMorphometry, 'rb')
    lines = f.readlines()
    f.close()

    valueList = []

    for line in lines:
        useLine = line.strip().split()
        # check if only one element and if element is number
        if sp.tools.isNumber(useLine[0]):
            valueList.append(float(useLine[0]))

    outVector = np.array(valueList)

    return outVector


#===============================================================================
#------------------------------------------------------------------ Conversions
#===============================================================================
def convertOneDNiml(inFile, outPath=None):
    '''
    converts AFNI's 1D files into niml.dset files

    If none is specified, just keep the name and path but convert
    '''
    if not outPath:
        outTemp = sp.tools.getBaseName(inFile)
        outPath = os.path.join(os.path.dirname(inFile), outTemp)

    command = ['ConvertDset', '-o_niml', '-add_node_index', '-overwrite',
               '-input', inFile, '-i_1D',
               '-prefix', outPath]
    print('running %s' % (str(command)))
    process = subprocess.Popen(command)
    output = process.communicate()[0]

    return output, outPath


def convertSurfaceGiftiAscii(pathToGifti, outPath=None):
    '''
    Converts a AFNI surface gifti into a freesurfer surface ascii
    '''
    if not outPath:
        tempOut = sp.tools.getBaseName(outPath)
        outPath = tempOut + '.asc'

    command = ['gifti_tool', '-infile', pathToGifti, '-write_asc',
               outPath]
    print('running %s' % (str(command)))
    process = subprocess.Popen(command)
    output = process.communicate()[0]

    return output, outPath


def convertSurfaceAsciiFs(pathToAscii, surfaceType='inflated', outPath=None):
    '''
    Take a ascii surface file and turn it into a freesurfer readable format
    by default takes an inflated surface
    '''
    if not outPath:
        tempOut = sp.tools.getBaseName(pathToAscii)
        outPath = ('%s.%s' % (tempOut, surfaceType))

    command = ['mris_convert', pathToAscii, outPath]
    print('running %s' % (str(command)))
    process = subprocess.Popen(command)
    output = process.communicate()[0]

    return output, outPath


def convertMorphGiftiAscii(pathToCWB, pathToGifti, outPath=None):
    '''
    Method to convert the stupid messy gifti stuff into at least a
    humanly readable xml mess
    '''
    if not outPath:
        outPath = sp.tools.getBaseName(outPath)

    command = [pathToCWB, '-gifti-convert', 'ASCII', pathToGifti, outPath]

    if os.path.isfile(outPath):
        print('%s exists, quitting' % (outPath))
        return outPath

    else:
        # run it

        print('running %s' % (str(command)))
        process = subprocess.Popen(command)
        output = process.communicate()[0]

        return outPath


def convertMorphAsciiMgh(pathToAscii, pathToSurface, outType='mgh',
                         outPath=None):
    '''
    Converts a Morph ascii into an mgh file
    '''
    if not outPath:
        tempOut = sp.tools.getBaseName(pathToAscii)
        outName = ('%s.%s' % (tempOut, outType))
        outDir = os.path.dirname(pathToAscii)
        outPath = os.path.join(outDir, outName)
    else:
        outPath = ("%s.%s" % (outPath, outType))

    command = ['mris_convert', '-c', pathToAscii, pathToSurface, outPath]

    print('running %s' % (str(command)))
    process = subprocess.Popen(command)
    output = process.communicate()[0]

    return output, outPath


def convertGiftiAsciiFsAscii(pathToGiftiAscii, surface, outPath=None):
    '''
    Loads the XML Ascii file and converts it into a freesurfer ascii file
    '''
    # Step 1: read the damn file
    print('giftiPath %s' % (pathToGiftiAscii))
    values = loadGiftiMorphometry(pathToGiftiAscii)
    valueStr = writeVector(surface, values, mode='ascii')

    if not outPath:
        tempOut = sp.tools.getBaseName(outPath)
        outPath = ('%s_fs' % (tempOut))

    # write out the result
    savePath = saveTxt(outPath, valueStr, extension='asc')

    return savePath


def convertLabelAsciiFs(pathToLabelAscii, surface, outPath=None):
    '''
    takes in the dumb gifti label and turns it into a nice freesurfer cortex
    label
    '''
    if not outPath:
        tempOut = sp.tools.getBaseName(pathToLabelAscii)
        outPath = os.path.join(os.path.dirname(pathToLabelAscii, tempOut))
    else:
        tempOut = sp.tools.getBaseName(outPath)
        outPath = os.path.join(os.path.dirname(outPath), tempOut)

    # Load the values from the gifti-ascii-label
    labelLine, labelVector = loadLabel(pathToLabelAscii, drop=0)
    # turn the stupid label into something that I can handle
    cortexVerteces = sp.procops.findNonZeros(surface, labelVector)

    # Now go through all the verteces and get the locations
    outStr = ('#!ascii label  , from subject  vox2ras=TkReg\n%d\n'
              % (len(cortexVerteces)))
    for vertex in cortexVerteces:
        location = surface[0][vertex]
        writeStr = ('%s %s %s %s 0' % (str(vertex),
                                           str(location[0]),
                                           str(location[1]),
                                           str(location[2])))
        outStr = (outStr + '%s\n' % (writeStr))
    # Save the result
    savePath = saveTxt(outPath, outStr, extension='label')

    return savePath


def convertTxtFs(surface, inPath, outPath, makeMgh=None):
    '''
    Method to convert ascii format files into freesurfer readable morphometry
    or mgh files

    an optional command allows to continue transforming the file into .mgh
    '''
    thickPath = ('%s.%s' % (outPath, 'thickness'))
    toThickCom = ['mris_convert', '-c', str(inPath), str(surface), str(thickPath)]
    print(toThickCom)
    thickOut = runSubprocess(toThickCom)
    print('Finished converting %s:\n%s' % (outPath, thickOut))

    if makeMgh:
        mghPath = ('%s.%s' % (makeMgh, 'mgh'))
        toMghCom = ['mri_convert', str(thickPath), str(mghPath)]
        mghOut = runSubprocess(toMghCom)
        print('Finished MGH conversion at %s:\n%s' % (makeMgh, mghOut))

        return thickPath, mghPath

    else:
        thickPath


#===============================================================================
#--------------------------------------------------------------- File Operations
#===============================================================================
def mapToSurface(sourceSub, sourceSurf, targetSub, hemi, outPath):
    '''
    Wrapper for the freesurfer command that registers one surface to another
    '''
    command = ['mri_surf2surf', '--s', sourceSub,
               '--sval', sourceSurf,
               '--trgsubject', targetSub,
               '--tval', outPath,
               '--hemi', hemi,
               '--cortex',
               '--noreshape']
    print('running %s' % (str(command)))
    process = subprocess.Popen(command)
    output = process.communicate()[0]

    return output, outPath


def stackFiles(listOfPaths, outPath):
    '''
    Method that stacks a list of paths and turns it into an mgh stack
    '''
    command = ['mri_concat']

    for path in listOfPaths:
        # print(pathToSurface)
        command.append(path)

    # Add the output to it
    command.append("--o")
    command.append(outPath)

    print command
    process = subprocess.Popen(command)
    output = process.communicate()[0]

    return outPath


def runSubprocess(command):
    # Just runs the subprocess
    # print(('Running command:\n%s' % (str(command)))
    print command
    process = subprocess.Popen(command)
    output = process.communicate()[0]

    return output


#===============================================================================
#--------------------------------------------------------------- Text Operations
#===============================================================================
def writeVector(surface, vector, mode='oneD'):
    '''
    Method that expects a vector of lenght #verteces_on_surface and that paints
    the scores in the vector on the corresponding verteces
    '''
    # sanity check
    numberVerteces = len(surface[0])
    numberElements = len(vector)
    if not numberVerteces == numberElements:
        message = ('The length of the vector (%s) doesn\'t match the' % (str(numberVerteces)
                   + ' number of verteces on the surface (%s)' % (str(numberElements))))

    # Decide what to write to
    if mode == 'oneD':
        # write to AFNI's 1D format
        outStr = ('# Node_ROI\n'
                  + '#  ni_type = "SUMA_1D_ROI_DATUMorint,int?"\n'
                  + '#  ni_dimen = "%i"\n' % (numberVerteces)
                  + '#  ni_datasize = "???"\n'
                  + '#  idcode_str = "XYZ_AP1ICJzdKDY4fa19J8q-KA"\n'
                  + '#  Parent_idcode_str = "XYZ_XvgLHur4aS7vcOJ_txqnxA"\n'
                  + '#  Parent_side = "R"\n'
                  + '#  Label = "0"\n'
                  + '# >')
        # Loop through the verteces and write
        for vertex, score in enumerate(vector):
            # outStr = ('%s\n%s %s' % (outStr, str(vertex).zfill(3), score))
            outStr = ('%s\n%s' % (outStr, score))

    elif mode == 'ascii':
        # write to freesurfer's ascii format
        outStr = ''
        # loop through the verteces and write
        for vertex, score in enumerate(vector):
            location = surface[0][vertex]
            writeStr = ('%s %s %s %s %s' % (str(vertex),
                                               str(location[0]),
                                               str(location[1]),
                                               str(location[2]),
                                               str(score)))
            outStr = (outStr + '%s\n' % (writeStr))
    else:
        # something went wrong
        message = ('The specified format (%s) is not implemented.'
                   % (str(mode)))
        raise Exception(message)

    return outStr


def genCondorString(runFilePath, argument, logFilePath):
    '''
    Write to the meta script to execute all of the models
    '''
    execString = ('executable     = ' + runFilePath + '\n'
                  + 'arguments      = ' + argument + '\n'
                  + 'universe       = vanilla' + '\n'
                  + 'output         = ' + logFilePath + '.out' + '\n'
                  + 'error          = ' + logFilePath + '.error' + '\n'
                  + 'log            = ' + logFilePath + '.log' + '\n'
                  + 'getenv         = True' + '\n'
                  + 'request_memory = 4000' + '\n'
                  + 'notify_user    = surchs@cbs.mpg.de' + '\n'
                  + 'queue\n\n')

    return execString


def vertexLabel(surface, labelLines):
    '''
    Method that generates a dictionary with all surface verteces and sets the
    value to 1 if it is in the label file and 0 otherwise
    '''
    numberVerteces = len(surface[0])
    vertexDict = {}

    for vertex in np.arange(numberVerteces):
        if str(vertex) in labelLines:
            # print('vertex %s is cortex' % (str(vertex)))
            vertexDict[str(vertex)] = 1
        else:
            # print('vertex %s is not cortex' % (str(vertex)))
            vertexDict[str(vertex)] = 0

    return vertexDict


def saveTxt(outPath, text, extension='txt', hemi='lh'):
    '''
    simple write out method. By default saves txt files
    '''
    if not os.path.isdir(os.path.dirname(outPath)):
        os.makedirs(os.path.dirname(outPath))

    if extension == 'asc':
        # doing freesurfer format, prepare
        saveDir = os.path.dirname(outPath)
        saveBase = os.path.basename(outPath)
        saveName = ('%s.%s.%s' % (hemi, saveBase, extension))
        savePath = os.path.join(saveDir, saveName)
    else:
        savePath = ('%s.%s' % (outPath, extension))

    f = open(savePath, 'wb')
    f.write(text)
    f.close()

    return savePath


def genFsgdFile(subjectList, outPath):
    '''
    Just make a very simple, one Group fsgd file from a list of subject Names
    '''
    tempStr = ('GroupDescriptorFile 1 \n'
               + 'Title G1V2\n'
               + 'Class Main')
    for subject in subjectList:
        # add to the String
        tempStr = ('%s\nInput %s Main' % (tempStr, subject))

    f = open(outPath, 'wb')
    f.write(tempStr)
    f.close()

    return outPath


def genGlm(doFTest, contrastPaths, fsgdPath, hemisphere, concatPath,
                modelPath, modelType,
                vertexThresh, clustThresh, posneg):
    '''
    This will generate the string containing the command to run the glmfit
    '''
    print("fsgdPath %s" % (fsgdPath))
    print('modelType %s' % (modelType))
    print('concatPath %s' % (concatPath))
    runStr = ('#!/bin/bash\n'
              + 'mri_glmfit'
              + ' --y %s' % (concatPath)
              + ' --fsgd %s %s' % (fsgdPath, modelType))
    for contrastPath in contrastPaths:
        runStr = (runStr + ' --C ' + contrastPath)

    runStr = (runStr
              + ' --surf fsaverage5 ' + hemisphere
              + ' --cortex'
              + ' --glmdir ' + modelPath
              + '\n')

    if posneg == 'pos':
        # positive
        runStr = (runStr
                  + 'mri_glmfit-sim'
                  + ' --glmdir ' + modelPath
                  + ' --sim mc-z 5000 %f mc-z.%.2f_positive' % (vertexThresh,
                                                                vertexThresh)
                  + ' --sim-sign pos --cwpvalthresh %f' % (clustThresh)
                  + ' --overwrite\n')
    elif posneg == 'neg':
        # negative
        runStr = (runStr
                  + 'mri_glmfit-sim'
                  + ' --glmdir ' + modelPath
                  + ' --sim mc-z 5000 %f mc-z.%.2f_negative' % (vertexThresh,
                                                                vertexThresh)
                  + ' --sim-sign neg --cwpvalthresh %f' % (clustThresh)
                  + ' --overwrite\n')
    elif posneg == 'both':
        # positive
        runStr = (runStr
                  + 'mri_glmfit-sim'
                  + ' --glmdir ' + modelPath
                  + ' --sim mc-z 5000 %f mc-z.%.2f_positive' % (vertexThresh,
                                                                vertexThresh)
                  + ' --sim-sign pos --cwpvalthresh %f' % (clustThresh)
                  + ' --overwrite\n')
        # negative
        runStr = (runStr
                  + 'mri_glmfit-sim'
                  + ' --glmdir ' + modelPath
                  + ' --sim mc-z 5000 %f mc-z.%.2f_negative' % (vertexThresh,
                                                                vertexThresh)
                  + ' --sim-sign neg --cwpvalthresh %f' % (clustThresh)
                  + ' --overwrite\n')
    else:
        message = ('You supplied a silly command for the contrast sign: %s'
                   % (str(posneg)))
        raise Exception(message)

    return runStr


def genContrast(outPath):
    '''
    Currently does only the one level contrast for no covariates
    '''
    conStr = '1'
    f = open(outPath, 'wb')
    f.write(conStr)
    f.close()

    return outPath


def findFileAtPath(fileName, searchPath):
    '''
    Tries to match the fileName at the searchPath

    Returns None if nothing is found, otherwise returns the full path
    '''
    pathItems = os.listdir(searchPath)
    print('searching for %s in %s' % (fileName, searchPath))
    if fileName in pathItems:
        outPath = os.path.join(searchPath, fileName)
        return outPath
    else:
        return None


if __name__ == '__main__':
    pass
