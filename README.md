surfaceProcessing
=================

Package with scripts for running surface level comparison of morphometry

##Installation
download a copy of the repository (or clone it). If the files are packed in a  
zip file (i.e. if you haven't cloned the repo), unpack them using tar -xzfv.  
Then, add the following line to the end of your .bashrc file  

    export PYTHONPATH=/Path/To/The/Downloaded/Files
    
While replacing '/Path/To/The/Downloaded/Files' with the actual absolute  
path to the directory where the package folder is stored. For example,
if you unpacked your files in /home/brainmaster/packages/surfaceProcessing
then you should use

    export PYTHONPATH=/home/brainmaster/packages
    
This will allow python to find the package and load all it's functions as
long as you start python under your user account.

In addition to the files in this repository, please also download the files  
in https://github.com/NeuroanatomyAndConnectivity/glyphsets  
From there, choose whichever runGradientFor###.sh file is appropriate for  
your usage scenario and add put the absolute path to it in the configure.py  
file.


##Usage
Make sure that all dependencies are available when executing the script
and when starting the condor process. 

###Condor usage
Before starting the condor process make sure that AFNI, connectome workbench  
and freesurfer binaries are available in your current terminal
environment (e.g. by typing AFNI, freesurfer).

To submit your job order to condor, go to the condorDir and look for the
appropriate .submit file that you would like to run. Then type

    condor_submit nameOfCondorFile.submit

to submit the process to condor. You can type

    condor_q [-global]

to check the processes (the -global flag is optional and will show an
overview of all currently running processes on the condor server).

Start using the scripts by executing

    python wrapper.py
    
and reading the help file. An example subject list is located at  
/scr/kansas1/surchs/testSurface/subjects.txt and this path is also ideal for  
testing.

If you would like to generate your own subject list, the nifti files are  
located here:

    /scr/melisse1/NKI_enhanced/results/


This is a list of the score options currently implemented for the surface processing  
'pearsonr': pearson correlation between gradient and overlay  
'spearmanr': spearman correlation between gradient and overlay  
'zpear': z-score of correlation p-value of pearson correlation  
'zspear': z-score of correlation p-value of spearman correlation  

## Dependencies
The gradient scripts used to generate the gradients depend on:
* [the connectome workbench of the human connectome project](http://www.humanconnectome.org/connectome/connectome-workbench.html)
* [freesurfer](http://ftp.nmr.mgh.harvard.edu/fswiki/Download)
* [AFNI](http://afni.nimh.nih.gov/afni/download)

The python modules need a couple of packages that usually come with every  
larger python distribution (like [EPD](https://www.enthought.com/products/epd/))  
but might need to install
* [nipy](http://nipy.org/)
* [pysurfer](http://pysurfer.github.io/)

If you want to go for all packages individually then you should have access to:
* numpy
* matplotlib
* sklearn
* scipy
* nibabel
* networkx
