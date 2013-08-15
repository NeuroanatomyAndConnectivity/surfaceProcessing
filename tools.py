'''
Created on Jul 29, 2013

@author: surchs
'''
import os
import re


def getBaseName(path):
    '''
    returns the baseName of the file without extension
    '''
    tempBase = re.search('^.*\.', os.path.basename(path))
    if not tempBase:
        # there is no dot at the end of the file Name
        baseName = os.path.basename(path)
    else:
        print(tempBase.group())
        baseName = tempBase.group().strip('.')

    return baseName


def isNumber(testString):
    '''
    A method to check if a string can be converted to a number
    Not my creation, took it from http://stackoverflow.com/
    '''
    try:
        float(testString)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    pass
