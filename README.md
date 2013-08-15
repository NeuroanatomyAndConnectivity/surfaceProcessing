surfaceProcessing
=================

Package with scripts for running surface level comparison of morphometry

###########
Installation
###########
download a copy of the repository (or clone it). If the files are packed in a 
zip file (i.e. if you haven't cloned the repo), unpack them using tar -xzfv.
Then, add the following line to the end of your .bashrc file
    export PYTHONPATH=/Path/To/The/Downloaded/Files
While replacing '/Path/To/The/Downloaded/Files' with the actual absolute
path that you downloaded the files to



This is a list of the score options currently implemented for the surface processing
'pearsonr': pearson correlation between gradient and overlay
'spearmanr': spearman correlation between gradient and overlay
'zpear': z-score of correlation p-value of pearson correlation
'zspear': z-score of correlation p-value of spearman correlation