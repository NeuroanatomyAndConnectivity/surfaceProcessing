#!/bin/bash

# This script unpacks the annotation file of the given template at the
# specified location where it will be picked up by the processing scripts

templateName=${1}
outDir=${2}/${templateName}

if [ ! -d "${outDir}" ]
then
    mkdir -pv ${outDir}
fi


for hemi in lh rh
do
    labelList=${subjectDir}'/labelList'_${hemi}'.txt'
    mri_annotation2label --subject ${templateName} --hemi ${hemi} --annotation aparc.a2009s --outdir ${outDir}
    ls ${outDir}/*${hemi}*.label > ${labelList}
    echo ${labelList}
done
