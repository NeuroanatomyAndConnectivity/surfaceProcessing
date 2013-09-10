#!/bin/bash

# This script unpacks the annotation file of the given template at the
# specified location where it will be picked up by the processing scripts

# Check the inputs
if [ $# -eq 0 ]
then
    echo You supplied nuthin, please supply the template name, the output directory and the hemisphere

elif [ -z "$2" ]
then
    echo You did not supply enough arguments, please also supply the the output directory and the hemisphere

elif [ -z "$3" ]
then
    echo You did not supply the hemisphere. Please specify the hemisphere as either lh or rh
    
else
    templateName=${1}
    outDir=${2}/${templateName}
    hemi=${3}
fi


if [ ! -d "${outDir}" ]
then
    mkdir -pv ${outDir}
fi

labelList=${subjectDir}'/labelList'_${hemi}'.txt'
mri_annotation2label --subject ${templateName} --hemi ${hemi} --annotation aparc.a2009s --outdir ${outDir}
ls ${outDir}/*${hemi}*.label > ${labelList}
echo ${labelList}
