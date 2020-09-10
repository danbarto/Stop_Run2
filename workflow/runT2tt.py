import glob
import ROOT
import os
import shutil
import pandas
import pickle

import subprocess
import tarfile
import time

replaceDict = [\
    # processes
    ('sig   ',          'signal'),
    ('znunu',           'TTZ  '),

    # systematics
    ('ISRSystSig',      'ISR_Weight'),
    ('ISRSystBG',       'ISR_Weight_background'), # can have either name
    ('ISRSyst',         'ISR_Weight_background'),
    ('jesSyst',         'JES'),
    ('q2Syst',          'LHEScale'),
    ('SigGenMETunc',    'MET_Unc'),
    ('pdfSystBG',       'PDF_Weight'), # can have either name
    ('pdfSyst',         'PDF_Weight'),
    ('pileupSyst',      'PU_Weight'),
    ('L1prefireSyst',   'Prefire_Weight'),
    ('bTagEffHFSyst',   'b_heavy'),
    ('bTagEffLFSyst',   'b_light'),
    ('bTagFSEffSystSig', 'b_fast'),
    ('resttagSFSyst',   'eff_restoptag'),
    ('merttagSFSyst',   'eff_toptag'),
    ('LumiSyst',        'lumi'),
    ('softbSFSyst',     'ivfunc'),
    ('TrigSyst',        'trigger_err'),
    ('ttZxsecSystZ',    'TTZ_SF'),
    ('lnU',             'lnN')
]

model           = 'T2bW'
small           = False
submit          = True
overwriteTar    = False

    
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

def replaceTextInFile(f, d):
    with open(f, 'r') as source:
        lines = source.readlines()
    with open(f, 'w') as output:
        for line in lines:
            for find, replace in d:
                line = line.replace(find, replace)
            output.write(line)

def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)



stop_1l_card_dir = os.path.abspath('./cards/%s/1l/'%model)
stop_1l_cards = glob.glob(stop_1l_card_dir+'/*.txt')

if small:
    stop_1l_cards = stop_1l_cards[1:4]


# get all the cards from 1l analysis - one card per mass point. Nice!
signals_noDuplicates = {'_'.join(s.replace('.txt','').split('/')[-1].split('_')[2:5]) for s in stop_1l_cards }
signals = []
for signal in signals_noDuplicates:
    mStop = int(signal.split('_')[1])
    mLSP  = int(signal.split('_')[2])
    card = stop_1l_card_dir + '/datacard_std_%s.txt'%signal
    if mStop - mLSP < 225 and model=='T2tt': card = card.replace('std', 'tcor')
    if mStop - mLSP <= 150 and model=='T2tt': card = card.replace('tcor', 'Wcor')
    if  not os.path.isfile(card):
        raise NameError("Card file not found, this should not happen")
    signals.append({'name': signal, 'mStop': mStop, 'mLSP': mLSP, '1l': card})


for nJob, signal in enumerate(signals):
    found = True
    print
    print "Job %s/%s: %s"%(nJob+1, len(signals), signal['name'])
    sig     = signal['name']
    mStop   = signal['mStop']
    mLSP    = signal['mLSP']
    

    ## get the 2l cards. need to take care of rounding
    allCards = [ x.split('/')[-1].replace('.txt','') for x in glob.glob(os.path.abspath('./cards/%s/2l/*.txt'%model)) ]
    if sig in allCards:
        dilep_card = os.path.abspath('./cards/%s/2l/%s_combination_shapeCard.txt'%(model, sig))
    else:
        masses = [ (int(x.split('_')[1]), int(x.split('_')[2]))  for x in allCards ]
        closestPointIndex = -1
        dM1, dM2 = 9999, 9999
        for i, t in enumerate(masses):
            m1, m2 = t
            if abs(mStop-m1) <= dM1 and abs(mLSP-m2) <= dM2:
                dM1 = abs(mStop-m1)
                dM2 = abs(mLSP-m2)
                closestPointIndex = i
        dilep_card = os.path.abspath('./cards/%s/2l/%s_%s_%s_combination_shapeCard.txt'%(model, model, masses[closestPointIndex][0], masses[closestPointIndex][1]))
        if dM1>4 or dM2>4:
            found = False
            dilep_card = False

    signal['2l'] = dilep_card

    # get the 0l cards. need to take care of rounding
    ## first, check that there's a directory for the cards
    allDirs = [ x.split('/')[-1] for x in glob.glob(os.path.abspath('./cards/%s/0l/*'%model)) if not 'txt' in x ]
    if sig in allDirs:
        allhad_card = sig
    else:
        masses = [ (int(x.split('_')[1]), int(x.split('_')[2]))  for x in allDirs ]
        closestPointIndex = -1
        dM1, dM2 = 9999, 9999
        for i, t in enumerate(masses):
            m1, m2 = t
            if abs(mStop-m1) <= dM1 and abs(mLSP-m2) <= dM2:
                dM1 = abs(mStop-m1)
                dM2 = abs(mLSP-m2)
                closestPointIndex = i

        allhad_card = model+'_%s_%s'%masses[closestPointIndex]
        if dM1>4 or dM2>4:
            found = False
            allhad_card = False

    allhad_cards = os.path.abspath('./cards/%s/0l/%s.txt'%(model,allhad_card)) if allhad_card else False
    if allhad_card:
        if not os.path.isfile(allhad_cards):
            print 'combining card', allhad_card
            subprocess.call("cd cards/%s/0l/; combineCards.py %s/*.txt > %s.txt"%(model, allhad_card, allhad_card), shell=True)
    
    signal['0l'] = allhad_cards
    signal['0l_name'] = allhad_card
    signal['0l_shapes'] = os.path.abspath('./cards/%s/0l/%s/'%(model, allhad_card)) if allhad_card else False

    signal['allChannels'] = found

# now do the work

from metis.Sample import DirectorySample, FilelistSample, DummySample
from metis.CondorTask import CondorTask
from metis.StatsParser import StatsParser
from metis.Utils import do_cmd

tasks = []

for signal in signals:
    sig = signal['name']
    tmpDir = 'tmp/%s'%sig

    print sig
    datacard = "datacard_combined_%s.txt"%sig
    
    if (signal['2l'] == False or signal['0l']==False) and signal['mStop']<=1200:
        print "Mass point missing in some channel. Skipping."
        print signal['name']
        continue

    if signal['0l']==False:
        print "Mass point missing in some channel. Skipping."
        print signal['name']
        continue

    if not os.path.isdir(tmpDir+'/'+signal['0l_name']):
        os.makedirs(tmpDir+'/'+signal['0l_name'])

    if overwriteTar or not os.path.isfile("%s.tar.gz"%tmpDir):
        print "Making combined card and tarball."
        # fix the 1l card
        replaceTextInFile(signal['1l'], replaceDict)

        # copy the cards over. need to keep the structure for shape files
        shutil.copy(signal['0l'], tmpDir)
        for shapeFile in glob.glob(signal['0l_shapes']+'/*.root'):
            shutil.copy(shapeFile, tmpDir+'/'+signal['0l_name'])
        shutil.copy(signal['1l'], tmpDir)
        if signal['mStop']<=1200:
            shutil.copy(signal['2l'], tmpDir)
            shutil.copy(signal['2l'].replace('Card.txt','.root'), tmpDir)

            # combine the cards
            subprocess.call("cd %s; combineCards.py dc_0l=%s dc_1l=%s dc_2l=%s > %s"%(tmpDir, signal['0l'].split('/')[-1], signal['1l'].split('/')[-1], signal['2l'].split('/')[-1], datacard), shell=True)
        elif signal['0l']:
            # no results for stop-2l for high mStop
            subprocess.call("cd %s; combineCards.py dc_0l=%s dc_1l=%s > %s"%(tmpDir, signal['0l'].split('/')[-1], signal['1l'].split('/')[-1], datacard), shell=True)
        else:
            print "No 0l card found, skipping"
            continue

        with tarfile.open("%s.tar.gz"%tmpDir, "w:gz") as tar:
            tar.add(tmpDir, arcname=os.path.sep)

    tag = 'v4'
    outDir = '/hadoop/cms/store/user/dspitzba/stopCombination/%s/%s/'%(model, tag)

    lowmass = True if signal['mStop'] <= 400 else False

    signal['workspace'] = outDir+'%s_1.root'%sig

    if submit:
        # create a fake sample from the shape card(s), and hijack the monitoring/resubmission of metis 
        if len(glob.glob(os.path.abspath(tmpDir+"/*.root")))==0: touch(os.path.abspath(tmpDir+"/dummy.root"))
        dummy = FilelistSample(dataset=sig, filelist=glob.glob(os.path.abspath(tmpDir+"/*.root"))[:1])
        task = CondorTask(
            sample                  = dummy,
            executable              = "executable.sh",
            arguments               = " %s %s %s"%(datacard, sig, lowmass),
            tarfile                 = "tmp/%s.tar.gz"%sig,
            files_per_output        = 1,
            output_dir              = outDir,
            output_name             = '%s.root'%sig,
            output_is_tree          = True,
            tag                     = tag,
            condor_submit_params    = {"sites":"T2_US_UCSD,UAF"},
            cmssw_version           = "CMSSW_10_2_9",
            scram_arch              = "slc6_amd64_gcc700",
            min_completion_fraction = 1.00,
        )
        
        
        tasks.append(task)


if submit:
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
        StatsParser(data=total_summary, webdir="~/public_html/dump/metis_%s/"%model).do()
        
        print "%s/%s jobs are completed."%(sum(fracs),len(fracs))

        if sum(fracs)/len(fracs)==1:
            print "Done."
            break

        # 15 min power nap
        time.sleep(15.*60)



for signal in signals:
    #signal['spin'] = signal['name'].split('_')[0]
    print signal['name']
    try:
        res = readResFile(signal['workspace'])
        for k in res.keys():
            signal[k] = res[k]
    except:
        print "Couldn't open Workspace"
        pass
 
pickle.dump(signals, file('results/%s.pkl'%model,'w'))

df = pandas.DataFrame(signals)   
