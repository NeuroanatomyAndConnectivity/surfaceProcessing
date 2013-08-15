surfaceProcessing
=================

Package with scripts for running surface level comparison of morphometry

##Installation
download a copy of the repository (or clone it). If the files are packed in a  
zip file (i.e. if you haven't cloned the repo), unpack them using tar -xzfv.  
Then, add the following line to the end of your .bashrc file  

    export PYTHONPATH=/Path/To/The/Downloaded/Files
    
While replacing '/Path/To/The/Downloaded/Files' with the actual absolute  
path that you downloaded the files to

In addition to the files in this repository, please also download the files  
in https://github.com/NeuroanatomyAndConnectivity/glyphsets  
From there, choose whichever runGradientFor###.sh file is appropriate for  
your usage scenario and add put the absolute path to it in the configure.py  
file.


##Usage

This is a list of the score options currently implemented for the surface processing  
'pearsonr': pearson correlation between gradient and overlay  
'spearmanr': spearman correlation between gradient and overlay  
'zpear': z-score of correlation p-value of pearson correlation  
'zspear': z-score of correlation p-value of spearman correlation  
