#!/bin/bash

# This is nanoAOD based sample making condor executable for CondorTask of ProjectMetis. Passed in arguments are:
# arguments = [outdir, outname_noext, inputs_commasep, index, cmssw_ver, scramarch, self.arguments]

OUTPUTDIR=$1
OUTPUTNAME=$2
INPUTFILENAMES=$3
IFILE=$4
CMSSW_VERSION=$5
SCRAM_ARCH=$6

CARDFILE=$7
MODELPOINT=$8

OUTPUTNAME=$(echo $OUTPUTNAME | sed 's/\.root//')

echo -e "\n--- begin header output ---\n" #                     <----- section division
echo "OUTPUTDIR: $OUTPUTDIR"
echo "OUTPUTNAME: $OUTPUTNAME"
echo "INPUTFILENAMES: $INPUTFILENAMES"
echo "IFILE: $IFILE"
echo "CMSSW_VERSION: $CMSSW_VERSION"
echo "SCRAM_ARCH: $SCRAM_ARCH"

echo "hostname: $(hostname)"
echo "uname -a: $(uname -a)"
echo "time: $(date +%s)"
echo "args: $@"

echo -e "\n--- end header output ---\n" #                       <----- section division
ls -ltrha
echo ----------------------------------------------

tar -xzf package.tar.gz
ls -ltrha
MYDIR=`pwd`

# Setup Enviroment
export SCRAM_ARCH=$SCRAM_ARCH
source /cvmfs/cms.cern.ch/cmsset_default.sh
#pushd /cvmfs/cms.cern.ch/$SCRAM_ARCH/cms/cmssw/$CMSSW_VERSION/src/ > /dev/null
#eval `scramv1 runtime -sh`
#popd > /dev/null
scramv1 project CMSSW $CMSSW_VERSION
cd $CMSSW_VERSION/src
eval `scramv1 runtime -sh`


# checkout the package
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v8.0.1
scramv1 b clean; scramv1 b # always make a clean build

cd $MYDIR

combine --saveWorkspace -M AsymptoticLimits --rMin -10 --rMax 10 --cminDefaultMinimizerStrategy 0 $CARDFILE

mv higgsCombineTest.AsymptoticLimits.mH120.root ${MODELPOINT}_1.root


# Copy back the output file

mkdir -p ${OUTPUTDIR}
#echo cp ${MODELPOINT}.root ${OUTPUTDIR}/${MODELPOINT}.root
#cp ${MODELPOINT}.root ${OUTPUTDIR}/${MODELPOINT}.root

export LD_PRELOAD=/usr/lib64/gfal2-plugins//libgfal_plugin_xrootd.so
gfal-copy -p -f -t 4200 --verbose file://`pwd`/${MODELPOINT}_1.root gsiftp://gftp.t2.ucsd.edu${OUTPUTDIR}/${MODELPOINT}_1.root --checksum ADLER32

echo "Directory after running"

ls -ltrha

echo -e "\n--- cleaning up ---\n" #                             <----- section division

rm -r $CMSSW_VERSION/
rm package.tar.gz
rm *.root
rm *.txt
