'''
Created on Jul 19, 2013

@author: surchs

Here goes everything for visualizing surfaces with pysurfer and other things
that I like.
such as:
- showing a surface
- showing an overlay

'''
import numpy as np
import networkx as nx
from surfer import Brain


def drawROI(surface, source, radius, graph, paintDistance=False):
    '''
    Paint a ROI on the surface. Radius refers to radius in weighted or
    unweighted surfaces.

    Expects a graph, a source that is member of the graph and a radius
    '''
    neighbourDict = nx.single_source_dijkstra_path_length(graph,
                                                          source,
                                                          radius)

    # prepare roi vector
    numberVertices = len(surface[0])
    roiVector = np.zeros(numberVertices)

    for node in neighbourDict.keys():
        if paintDistance:
            roiVector[node] = neighbourDict[node]
        else:
            roiVector[node] = 1

    return roiVector


def drawVerteces(surface, verteces, paintValues=None):
    '''
    Method to highlight verteces of interest. Expects a pre-calculated list
    of verteces (such as neighbours)
    '''
    # if paintValues is set, check if we have enough values
    if paintValues and not len(paintValues) == len(verteces):
        message = ('You specified %s verteces but only %s paint values'
                   % (str(len(verteces)), str(len(paintValues))))
        raise Exception(message)

    numberVertices = len(surface[0])
    neighbourVector = np.zeros(numberVertices)
    # loop through the connected nodes (i.e. are within a cutoff distance)
    for index, node in enumerate(verteces):
        if paintValues:
            neighbourVector[node] = paintValues[index]
        else:
            neighbourVector[node] = 1

    return neighbourVector


def visMorph(pathToSurface, overlay, outputPath, hemi):
    '''
    Display anything morphometric
    '''
    # check the overlay
    if (not overlay == 'sulc' and not overlay == 'thickness'
        and not overlay == 'curv'):
        message = ('You specified %s as overlay, this doesn\'t make sense'
                     % (overlay))
        raise Exception(message)

    brain = Brain(pathToSurface, hemi, 'white')
    brain.add_morphometry(overlay)
    brain.save_montage(outputPath, ['l', 'm'], orientation='v')
    brain.close()


def visMontage(pathToSurface, overlay, outputPath, hemi, type='white'):
    brain = Brain(pathToSurface, hemi, type)
    brain.add_overlay(overlay, -5, 3)
    brain.save_montage(outputPath, ['l', 'm'], orientation='v')
    brain.close()

    return outputPath


def visOverlay(pathToSurface, overlay, outputPath, hemi, type='white'):
    brain = Brain(pathToSurface, hemi, type)
    brain.add_overlay(overlay, -1, 1)
    brain.show_view('lateral')
    brain.save_imageset(outputPath, ['med', 'lat'], 'png')
    brain.close()

if __name__ == '__main__':
    pass
