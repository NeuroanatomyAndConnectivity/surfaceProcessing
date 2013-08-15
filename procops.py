'''
Created on Jul 18, 2013

@author: surchs

This contains all computation operations

'''
import subprocess
import numpy as np
import networkx as nx
import multiprocessing
from scipy import stats as st
from nipy.labs import utils as nu


def computeDistance(vertexLocations, vertex1, vertex2):
    '''
    Method computes the distance between two vertices given that their
    volumetric coordinates are given in a list that is strictly ordered by
    vertex ID

    ____
    usage: computeDistance(vertexLocations, vertex1, vertex2)
    ----
    '''
    vertex1Loc = vertexLocations[vertex1]
    vertex2Loc = vertexLocations[vertex2]
    offset = vertex1Loc - vertex2Loc
    distance = np.sqrt(np.sum(np.square(offset)))

    return distance


def work(cmd):
    return subprocess.Popen(cmd)


def buildGraph(surface, weighted=True):
    '''
    This method generates the graph by generating edges between known nodes
    and weighting them by their distance
    '''
    # Load values from the surface
    numberVertices = len(surface[0])
    vertexLocations = surface[0]
    numberTriangles = len(surface[1])
    vertexTriangles = surface[1]

    # Generate the (empty) Graph
    graph = nx.Graph()

    # Loop through all the triangles, this is going to include redundant
    # edges but we don't care
    for triangle in vertexTriangles:
        # get the verteces that make up the triangle
        vertex1 = triangle[0]
        vertex2 = triangle[1]
        vertex3 = triangle[2]

        if weighted:
            # get the distances
            distance12 = computeDistance(vertexLocations, vertex1, vertex2)
            distance13 = computeDistance(vertexLocations, vertex1, vertex3)
            distance23 = computeDistance(vertexLocations, vertex2, vertex3)
        else:
            distance12, distance13, distance23 = (1, 1, 1)

        # and generate the edges
        graph.add_edge(vertex1, vertex2, weight=distance12)
        graph.add_edge(vertex1, vertex3, weight=distance13)
        graph.add_edge(vertex2, vertex3, weight=distance23)

    return graph, numberVertices


def buildNeighbors(graph, cutoff, source=None):
    '''
    This method returns a dictionary keyed by node source index that contains
    another dictionary keyed by target node index. The values are the weighted
    shortest path lengths from source to target that are below a certain
    cutoff value

    if a source is set, then neighbours are only calculated for this node
    '''
    if source:
        distanceDict = nx.single_source_dijkstra(graph, source, cutoff)
    else:
        print('Begin calculating for all nodes with radius %.2f.' % (cutoff))
        distanceDict = nx.all_pairs_dijkstra_path_length(graph, cutoff)
        print('Done calculating for all nodes with radius %.2f.' % (cutoff))

    return distanceDict


def findNonZeros(surface, vector):
    '''
    returns a list of verteces for which the vector has non-zero values.
    I'll use this to handle stupid label files. Obviously the vector has to
    have entries for each vertex in the surface
    '''
    # sanity check
    if not len(vector) == len(surface[0]):
        message = ('vector (%d) is not of same length as surface (%d)'
                   % (len(vector), len(surface[0])))
        raise Exception(message)

    vertexList = []

    for vertex in xrange(len(vector)):
        if vector[vertex] != 0:
            vertexList.append(vertex)

    outVector = np.array(vertexList)

    return outVector


def keepNodes(graph, vertecesToKeep):
    '''
    Method keeps only the specified verteces in the graph
    '''
    count = 0
    print('Begin removing nodes from Graph. Will keep %d of %d nodes'
          % (len(vertecesToKeep), len(graph.nodes())))
    # find the nodes that are not in the the vertexList
    graphNodeSet = set(graph.nodes())
    vertexSet = set(vertecesToKeep)
    removeNodes = np.array(list(graphNodeSet - vertexSet))
    graph.remove_nodes_from(removeNodes)

    print('removed %d verteces' % (len(removeNodes)))
    return graph


def removeNodes(graph, vertecesToRemove):
    '''
    Method removes the specified verteces from the graph
    '''
    graph.remove_nodes_from(vertecesToRemove)

    return graph


def getRoiMorph(neighbours, morphVec):
    '''
    Method that returns a set of morphometric values for verteces in the set
    of neighbours (ROI)
    '''
    morphVals = morphVec[map(int, neighbours)]

    return morphVals


def getScore(valSet, score, valSet2=None):
    '''
    Gets the score for one or two sets of values. Currently implemented are:
    for single sets:
        - sum
        - mean
        - SD
    for two sets:
        - pearson r
        - z-scored p-value for pearson r
    '''
    if score == 'sum':
        return np.sum(valSet)

    elif score == 'mean':
        return np.mean(valSet)
    elif score == 'sd':
        return np.std(valSet)
    elif score == 'pearsonr':
        r, p = st.pearsonr(valSet, valSet2)
        if np.isnan(r):
            r = 0
        return r
    elif score == 'spearmanr':
        r, p = st.spearmanr(valSet, valSet2)
        if np.isnan(r):
            r = 0
        return r
    elif score == 'zpear':
        r, p = st.pearsonr(valSet, valSet2)
        k = 0
        if np.isnan(r):
            k = 0
        elif np.isnan(p):
            k = 0
        elif np.isnan(nu.zscore(p)):
            k = 0
        elif r > 0:
            k = nu.zscore(p)
        elif r < 0:
            k = -nu.zscore(p)
        return k
    elif score == 'zspear':
        r, p = st.spearmanr(valSet, valSet2)
        k = 0
        if np.isnan(r):
            k = 0
        elif np.isnan(p):
            k = 0
        elif np.isnan(nu.zscore(p)):
            k = 0
        elif r > 0:
            k = nu.zscore(p)
        elif r < 0:

            k = -nu.zscore(p)
        return k


def slideRoiValues(numberVerteces, verteces, neighbourDict,
                   morphVec, morphVec2=None, score='zspear'):
    '''
    Method that loops through all verteces in the surface and gets the
    morphometry values from its neighbours.

    returns a vector of # verteces with the summed scores of the neighbours
    '''
    outVec = np.zeros(numberVerteces)

    for vertex in verteces:
        neighbours = neighbourDict[int(vertex)].keys()
        neighbourVals = getRoiMorph(neighbours, morphVec)
        if not morphVec2 == None:
            neighbourVals2 = getRoiMorph(neighbours, morphVec2)
            vertexVal = getScore(neighbourVals, score,
                                 valSet2=neighbourVals2)
        else:
            vertexVal = getScore(neighbourVals, 'sum')
        outVec[int(vertex)] = vertexVal

    return outVec


def mapBack(vector, indices, numberOriginalVerteces):
    '''
    This maps back a vector of a truncated graph into the original graph size
    by using a list of vertex indices
    '''
    outVector = np.zeros(numberOriginalVerteces)
    outVector[indices] = vector

    return outVector


def makeMask(vector, values):
    '''
    given a vector of values and an iterable of values to keep, this return a
    mask vector with the same length as the input vector that will be 1 where
    vector == value and 0 elsewhere
    '''
    maskVector = np.zeros_like(vector, dtype=int)
    print('invec min: %s max: %s' % (str(vector.min()), str(vector.max())))
    for value in values:
        print('%s of %s verteces are in cluster %s'
              % (str(len(maskVector[np.where(vector == value)])),
                 str(len(vector)), str(value)))
        maskVector[np.where(vector == value)] = 1

    return maskVector


def maskVector(vector, mask):
    '''
    given a vector and a binary mask vector of the same length, returns the
    masked vector...
    pretty basic stuff
    '''
    maskedVector = vector * mask

    return maskedVector


if __name__ == '__main__':
    pass
