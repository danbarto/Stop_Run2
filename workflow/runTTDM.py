import glob
import ROOT
import os
import shutil
import subprocess
import tarfile
import time

replaceDict = [\
    # processes
    ('sig   ',          'signal'),
    ('znunu',           'TTZ  '),

    # systematics
    ('ISRSystsignal',   'ISR_Weight'),
    ('ISRSystBG',       'ISR_Weight_background'), # can have either name
    ('ISRSyst',         'ISR_Weight_background'),
    ('jesSyst',          'JES'),
    ('q2Syst',          'LHEScale'),
    ('SigGenMETunc',    'MET_Unc'),
    ('pdfSystBG',       'PDF_Weight'), # can have either name
    ('pdfSyst',         'PDF_Weight'),
    ('pileupSyst',      'PU_Weight'),
    ('L1prefireSyst',   'Prefire_Weight'),
    ('bTagEffHFSyst',   'b_heavy'),
    ('bTagEffLFSyst',   'b_light'),
    ('bTagFSEffSystsignal', 'b_fast'),
    ('resttagSFSyst',   'eff_restoptag'),
    ('merttagSFSyst',   'eff_toptag'),
    ('LumiSyst',        'lumi'),
    ('softbSFSyst',     'ivfunc'),
    ('TrigSyst',        'trigger_err'),
    ('ttZxsecSystZ',    'TTZ_SF'),
    ('lnU',             'lnN')
]
    

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

stop_1l_cards = glob.glob(os.path.abspath('./cards/TTbarDM/1l/*.txt'))

signals = [ {'spin': s.replace('.txt','').split('/')[-1].split('_')[3], 'mChi':s.replace('.txt','').split('/')[-1].split('_')[5], 'mPhi':s.replace('.txt','').split('/')[-1].split('_')[4], 'name':'_'.join(s.replace('.txt','').split('/')[-1].split('_')[3:6]), '1l': s} for s in stop_1l_cards ]

#signals = signals[:1]

for signal in signals:
    sig = signal['name']
    dilep_card = os.path.abspath('./cards/TTbarDM/2l/TTDM_%s_combination_shapeCard.txt'%sig)
    dilep_card = dilep_card.replace('pseudo', 'pseudoscalar')
    signal['2l'] = dilep_card


    allhad_cards = os.path.abspath('./cards/TTbarDM/0l/TTbarDMJets_Inclusive_%s_%s_%s.txt'%(signal['spin'], signal['mChi'], signal['mPhi']) )
    allhad_card = "TTbarDMJets_Inclusive_%s_%s_%s"%(signal['spin'], signal['mChi'], signal['mPhi'])
    allhad_cards = allhad_cards.replace('pseudo', 'pseudoscalar') # this is the path
    allhad_card = allhad_card.replace('pseudo', 'pseudoscalar') # this is the file name

    if not os.path.isfile(allhad_cards):
        print 'combining card', allhad_card
        subprocess.call("cd cards/TTbarDM/0l/; combineCards.py %s/*.txt > %s.txt"%(allhad_card, allhad_card), shell=True)
    
    signal['0l'] = allhad_cards
    signal['0l_name'] = allhad_card
    signal['0l_shapes'] = os.path.abspath('./cards/TTbarDM/0l/%s/'%allhad_card) if allhad_card else False

# now do the work

from metis.Sample import DirectorySample, FilelistSample, DummySample
from metis.CondorTask import CondorTask
from metis.StatsParser import StatsParser
from metis.Utils import do_cmd

tasks = []

overwriteTar = True

for signal in signals:
    sig = signal['name']
    tmpDir = 'tmp/%s'%sig
    if not os.path.isdir(tmpDir):
        os.makedirs(tmpDir)

    datacard = "datacard_combined_%s.txt"%sig
    print "Using datacard: %s for signal: %s"%(datacard, sig)

    datacard_0l = "datacard_0l_%s.txt"%sig
    datacard_1l = "datacard_1l_%s.txt"%sig
    datacard_2l = "datacard_2l_%s.txt"%sig

    if not os.path.isdir(tmpDir+'/'+signal['0l_name']):
        os.makedirs(tmpDir+'/'+signal['0l_name'])

    if overwriteTar or not os.path.isfile("%s.tar.gz"%tmpDir):
        print "Making combined card and tarball."
        # fix the 1l card
        replaceTextInFile(signal['1l'], replaceDict)

        # copy the cards over. need to keep the structure for shape files
        print signal['0l']
        print tmpDir
        shutil.copy(signal['0l'], tmpDir)
        for shapeFile in glob.glob(signal['0l_shapes']+'/*.root'):
            shutil.copy(shapeFile, tmpDir+'/'+signal['0l_name'])
        shutil.copy(signal['1l'], tmpDir)
        shutil.copy(signal['2l'], tmpDir)
        print signal['2l']
        print signal['2l'].replace('Card.txt','.root')
        shutil.copy(signal['2l'].replace('Card.txt','.root'), tmpDir)

        # now make the names uniform
        shutil.move(os.path.join(tmpDir, signal['0l'].split('/')[-1]), os.path.join(tmpDir, datacard_0l))
        shutil.move(os.path.join(tmpDir, signal['1l'].split('/')[-1]), os.path.join(tmpDir, datacard_1l))
        shutil.move(os.path.join(tmpDir, signal['2l'].split('/')[-1]), os.path.join(tmpDir, datacard_2l))
        
        # combine the vards
        subprocess.call("cd %s; combineCards.py dc_0l=datacard_0l_%s.txt dc_1l=datacard_1l_%s.txt dc_2l=datacard_2l_%s.txt > %s"%(tmpDir, sig, sig, sig, datacard), shell=True)
        with tarfile.open("%s.tar.gz"%tmpDir, "w:gz") as tar:
            tar.add(tmpDir, arcname=os.path.sep)

    tag = 'v8'
    outDir = '/hadoop/cms/store/user/dspitzba/TTDM/%s/'%tag

    #raise NotImplementedError

    # create a fake sample from the shape card(s), and hijack the monitoring/resubmission of metis 
    touch(os.path.abspath(tmpDir+"/combined.root"))
    combined_task = CondorTask(
        sample                  = FilelistSample(dataset=sig+'_combined', filelist=glob.glob(tmpDir+"/combined.root")[:1]),
        executable              = "executable.sh",
        arguments               = " %s %s"%(datacard, sig),
        tarfile                 = "tmp/%s.tar.gz"%sig,
        files_per_output        = 1,
        output_dir              = outDir+'/combined/',
        output_name             = '%s.root'%sig,
        output_is_tree          = True,
        tag                     = tag,
        condor_submit_params    = {"sites":"T2_US_UCSD,UAF"},
        cmssw_version           = "CMSSW_10_2_9",
        scram_arch              = "slc6_amd64_gcc700",
        min_completion_fraction = 1.00,
    )
    
    tasks.append(combined_task)

    # 
    touch(os.path.abspath(tmpDir+"/allhad.root"))
    allhad_task = CondorTask(
        sample                  = FilelistSample(dataset=sig+'_allhad', filelist=glob.glob(tmpDir+"/allhad.root")[:1]),
        executable              = "executable.sh",
        arguments               = " %s %s"%(datacard_0l, sig),
        tarfile                 = "tmp/%s.tar.gz"%sig,
        files_per_output        = 1,
        output_dir              = outDir+'/0l/',
        output_name             = '%s.root'%sig,
        output_is_tree          = True,
        tag                     = tag,
        condor_submit_params    = {"sites":"T2_US_UCSD,UAF"},
        cmssw_version           = "CMSSW_10_2_9",
        scram_arch              = "slc6_amd64_gcc700",
        min_completion_fraction = 1.00,
    )
    
    tasks.append(allhad_task)

    touch(os.path.abspath(tmpDir+"/singlelep.root"))
    singlelep_task = CondorTask(
        sample                  = FilelistSample(dataset=sig+'_singlelep', filelist=glob.glob(tmpDir+"/singlelep.root")[:1]),
        executable              = "executable.sh",
        arguments               = " %s %s"%(datacard_1l, sig),
        tarfile                 = "tmp/%s.tar.gz"%sig,
        files_per_output        = 1,
        output_dir              = outDir+'/1l/',
        output_name             = '%s.root'%sig,
        output_is_tree          = True,
        tag                     = tag,
        condor_submit_params    = {"sites":"T2_US_UCSD,UAF"},
        cmssw_version           = "CMSSW_10_2_9",
        scram_arch              = "slc6_amd64_gcc700",
        min_completion_fraction = 1.00,
    )
    
    tasks.append(singlelep_task)


    touch(os.path.abspath(tmpDir+"/dilep.root"))
    dilep_task = CondorTask(
        sample                  = FilelistSample(dataset=sig+'_dilep', filelist=glob.glob(tmpDir+"/dilep.root")[:1]),
        executable              = "executable.sh",
        arguments               = " %s %s"%(datacard_2l, sig),
        tarfile                 = "tmp/%s.tar.gz"%sig,
        files_per_output        = 1,
        output_dir              = outDir+'/2l/',
        output_name             = '%s.root'%sig,
        output_is_tree          = True,
        tag                     = tag,
        condor_submit_params    = {"sites":"T2_US_UCSD,UAF"},
        cmssw_version           = "CMSSW_10_2_9",
        scram_arch              = "slc6_amd64_gcc700",
        min_completion_fraction = 1.00,
    )
    
    tasks.append(dilep_task)



    signal['workspace_combined'] = outDir+'/combined/%s_1.root'%sig
    signal['workspace_0l'] = outDir+'/0l/%s_1.root'%sig
    signal['workspace_1l'] = outDir+'/1l/%s_1.root'%sig
    signal['workspace_2l'] = outDir+'/2l/%s_1.root'%sig

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
    for channel in ['combined', '0l', '1l', '2l']:
        try:
            res = readResFile(signal['workspace_%s'%channel])
            for k in res.keys():
                signal[channel+'_%s'%k] = res[k]
        except:
            print "No results yet for %s, %s, %s in channel %s"%(signal['spin'], signal['mStop'], signal['mLSP'], channel)
            
 
import pandas
import pickle
pickle.dump(signals, file('results/TTDM_all.pkl','w'))

df = pandas.DataFrame(signals)   

# print df[['mStop', 'mLSP', 'spin', '0l_0.500', '1l_0.500', '2l_0.500', 'combined_0.500']]

