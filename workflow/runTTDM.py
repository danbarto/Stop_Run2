import glob
import ROOT
import os
import shutil

replaceDict = [\
    # processes
    ('sig   ',          'signal'),

    # systematics
    ('ISRSystsignal',   'ISR_Weight'),
    ('ISR16SystBG',     'ISR_Weight_background'),
    ('jesSystBG',       'JES'),
    ('q2Syst',          'LHEScale'),
    ('SigGenMETunc',    'MET_Unc'),
    ('pdfSystBG',       'PDF_Weight'),
    ('pileupSyst',      'PU_Weight'),
    ('L1prefireSyst',   'Prefire_Weight'),
    ('bTagEffHFSyst',   'b'),
    ('bTagFSEffSystsignal', 'b_fast'),
    ('resttagSFSyst',   'eff_restoptag'),
    ('merttagSFSyst',   'eff_toptag'),
    ('LumiSyst',        'lumi')
]
    

def replaceTextInFile(f, d):
    with open(f, 'r') as source:
        lines = source.readlines()
    with open(f, 'w') as output:
        for line in lines:
            for find, replace in d:
                line = line.replace(find, replace)
            output.write(line)


stop_1l_cards = glob.glob(os.path.abspath('./cards/TTbarDM/1l/*.txt'))

signals = [ {'name':'_'.join(s.replace('.txt','').split('/')[-1].split('_')[3:6]), '1l': s} for s in stop_1l_cards ]

#signals = signals[:1]

for signal in signals:
    sig = signal['name']
    dilep_card = os.path.abspath('./cards/TTbarDM/2l/TTDM_%s_combination_shapeCard.txt'%sig)
    dilep_card = dilep_card.replace('pseudo', 'pseudoscalar')
    signal['2l'] = dilep_card

# now do the work
import subprocess
import tarfile
import time

from metis.Sample import DirectorySample, FilelistSample, DummySample
from metis.CondorTask import CondorTask
from metis.StatsParser import StatsParser
from metis.Utils import do_cmd

tasks = []

overwriteTar = False

for signal in signals:
    sig = signal['name']
    if not os.path.isdir(sig):
        os.makedirs(sig)

    datacard = "datacard_combined_%s.txt"%sig
    
    if overwriteTar:
        # fix the 1l card
        replaceTextInFile(signal['1l'], replaceDict)

        # copy the cards over
        shutil.copy(signal['1l'], sig)
        shutil.copy(signal['2l'], sig)
        shutil.copy(signal['2l'].replace('Card.txt','.root'), sig)

        # combine the vards
        subprocess.call("cd %s; combineCards.py dc_1l=%s dc_2l=%s > %s"%(sig, signal['1l'].split('/')[-1], signal['2l'].split('/')[-1], datacard), shell=True)
        with tarfile.open("%s.tar.gz"%sig, "w:gz") as tar:
            tar.add(sig, arcname=os.path.sep)

    outDir = '/hadoop/cms/store/user/dspitzba/TTDM/'

    # create a fake sample from the shape card(s), and hijack the monitoring/resubmission of metis 
    task = CondorTask(
        sample                  = FilelistSample(dataset=sig, filelist=glob.glob(sig+"/*.root")[:1]),
        executable              = "executable.sh",
        arguments               = " %s %s"%(datacard, sig),
        tarfile                 = "%s.tar.gz"%sig,
        files_per_output        = 1,
        output_dir              = outDir,
        output_name             = '%s.root'%sig,
        output_is_tree          = True,
        tag                     = 'v2',
        condor_submit_params    = {"sites":"T2_US_UCSD,UAF"},
        cmssw_version           = "CMSSW_10_2_9",
        scram_arch              = "slc6_amd64_gcc700",
        min_completion_fraction = 1.00,
    )
    
    signal['workspace'] = outDir+'%s_1.root'%sig
    
    tasks.append(task)


if True:
    for i in range(100):
        total_summary = {}
        fracs = []
    
        for task in tasks:
        #for maker_task in maker_tasks:
            task.process()
    
            frac = task.complete(return_fraction=True)
    
            total_summary[task.get_sample().get_datasetname()] = task.get_task_summary()
 
            fracs.append(frac)
   
        # parse the total summary and write out the dashboard
        StatsParser(data=total_summary, webdir="~/public_html/dump/metis_TTDM/").do()
    
        if sum(fracs)/len(fracs)==1:
            print "Done."
            break

        # 15 min power nap
        time.sleep(15.*60)


## Harvest the results
def readResFile(fname):
    f = ROOT.TFile.Open(fname)
    t = f.Get("limit")
    l = t.GetLeaf("limit")
    qE = t.GetLeaf("quantileExpected")
    limit = {}
    preFac = 1.
    for i in range(t.GetEntries()):
        t.GetEntry(i)
        limit["{0:.3f}".format(round(qE.GetValue(),3))] = preFac*l.GetValue()
    f.Close()
    return limit

for signal in signals:
    signal['spin'] = signal['name'].split('_')[0]
    signal['mStop'] = int(signal['name'].split('_')[1])
    signal['mLSP'] = int(signal['name'].split('_')[2])
    res = readResFile(signal['workspace'])
    for k in res.keys():
        signal[k] = res[k]
 
import pandas
import pickle
pickle.dump(signals, file('results/TTDM.pkl','w'))

df = pandas.DataFrame(signals)   

