import ROOT, os, math

import pickle, shutil
from RootTools.core.standard                import *
from array import array

import pandas
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--spin',           action='store',      default='scalar',            nargs='?', choices=['scalar','pseudo'], help="scalar (S) or pseudo (PS)?")
argParser.add_argument('--scan',               action='store',      default='mPhi',           help='Which DM particle mass to scan? mChi or mPhi')
argParser.add_argument('--plot_directory',     action='store',      default='DMLimits')
argParser.add_argument('--blinded',            action='store_true')
argParser.add_argument('--cardDir',            action='store',      default='TTbarDM_preAppFix_DYttZflat')
argParser.add_argument('--xsec',            action='store_true')
argParser.add_argument('--LO',            action='store_true')
argParser.add_argument('--logy',            action='store_true')
args = argParser.parse_args()

#ROOT.gROOT.SetBatch(True)
ROOT.gROOT.LoadMacro('../../RootTools/plot/scripts/tdrstyle.C')
ROOT.setTDRStyle()

categories = []
mChi_list = []
mPhi_list = []

def getTTDMXSec(spin, mPhi, mChi, order='NLO'):
    import yaml

    if order=='LO':
        results_file = '$CMSSW_BASE/src/Stop_Run2/tools/data/xsec_DM_LO.yml'
    else:
        results_file = '$CMSSW_BASE/src/Stop_Run2/tools/data/xsec_DM.yml'

    with open(os.path.expandvars(results_file), 'r') as f:
        xsec = yaml.load(f)
    res = pandas.DataFrame(xsec)

    return res[((res['spin']==spin)&(res['mChi']==mChi)&(res['mPhi']==mPhi))]

#for s in DMsamples:
#    if not s[0] in mChi_list: mChi_list.append(s[0])
#    if not s[1] in mPhi_list: mPhi_list.append(s[1])
#    if not s[2] in categories: categories.append(s[2])

#res = pickle.load(file(os.path.join(analysis_results,"fitAll","cardFiles",args.cardDir,"calculatedLimits.pkl")))
res = pickle.load(file('../workflow/results/TTDM_all.pkl'))
#resDL = pickle.load(file('../workflow/results/TTDM_DL.pkl'))

if args.scan == 'mPhi':
    scanVar = 'mStop'
    fixedVar = 'mLSP'
    fixedMass = 1
else:
    scanVar = 'mLSP'
    fixedVar = 'mStop'
    fixedMass = 100

df = pandas.DataFrame(res)
#dfDL = pandas.DataFrame(resDL)

#mChi = int(args.mChi)
tp = args.spin

print "Filtering: spin %s fixedMass %s fixedVar %s scanVar %s"%(tp, fixedMass, fixedVar, scanVar)

filteredResults = df[((df['spin']==tp)&(df[fixedVar]==fixedMass))].sort_values(by=scanVar)
#filteredResultsDL = dfDL[((dfDL['spin']==tp.replace('pseudo','pseudoscalar'))&(dfDL[fixedVar]==fixedMass))].sort_values(by=scanVar)

mass        = []
obs         = []
obsUp       = []
obsDown     = []
exp         = []
expDL       = []
expSL       = []
expZL       = []
exp1Up      = []
exp2Up      = []
exp1Down    = []
exp2Down    = []
xsecs       = []
zeros       = []

#from StopsDilepton.tools.xSecDM import *
#xSecDM_ = xSecDM()

print args.scan, tp

for s in filteredResults[scanVar].tolist():
    if args.scan == 'mPhi':
        mChi = s
        mPhi = fixedMass
    else:
        mChi = fixedMass
        mPhi = s
    try:
        tmp = filteredResults[filteredResults[scanVar]==s]#['0.500']
        #tmpDL = filteredResultsDL[filteredResultsDL[scanVar]==s]#['0.500']
        if args.xsec:
            if args.LO:
                try:
                    xsec = float(getTTDMXSec(tp.replace('pseudo','pseudoscalar'), int(mChi), int(mPhi), order='LO')['xsec'])
                    print 'LO', xsec, mPhi, mChi
                except TypeError:
                    continue
            else:
                xsec = float(getTTDMXSec(tp.replace('pseudo','pseudoscalar'), int(mChi), int(mPhi))['xsec']) # replacement needed for compatibilty with yaml file
                print 'NLO', xsec, mPhi, mChi
        else:
            if args.LO:
                try:
                    xsec_LO = float(getTTDMXSec(tp.replace('pseudo','pseudoscalar'), int(mChi), int(mPhi), order='LO')['xsec'])
                except TypeError:
                    continue
                xsec_NLO = float(getTTDMXSec(tp.replace('pseudo','pseudoscalar'), int(mChi), int(mPhi))['xsec'])
                xsec = xsec_NLO/xsec_LO
            else:
                xsec = 1
        #xsec = 1

        # x-sec line
        if args.LO and not args.xsec:
            xsecs.append(1)
        else:
            xsecs.append(xsec)
        print s
        mass.append(s)

        # expected line and bands
        exp.append(xsec*float(tmp['combined_0.500']))
        print (xsec*float(tmp['combined_0.500']))
        try:
            expDL.append(xsec*float(tmp['2l_0.500']))
            expSL.append(xsec*float(tmp['1l_0.500']))
            expZL.append(xsec*float(tmp['0l_0.500']))
        except:
            pass
        exp1Up.append(xsec*(float(tmp['combined_0.840']) - float(tmp['combined_0.500'])))
        exp2Up.append(xsec*(float(tmp['combined_0.975']) - float(tmp['combined_0.500'])))
        exp1Down.append(xsec*(float(tmp['combined_0.500']) - float(tmp['combined_0.160'])))
        exp2Down.append(xsec*(float(tmp['combined_0.500']) - float(tmp['combined_0.025'])))

        # observed line and theory uncertainty band
        obs.append(xsec*(float(tmp['combined_-1.000'])))
        obsUp.append(xsec*(float(tmp['combined_-1.000']))*0.3)
        obsDown.append(xsec*(float(tmp['combined_-1.000']))*0.3)

        #obsUp.append(xsec*res[(s[0],s[1],s[2])]['-1.000']*math.sqrt(0.3**2 + (xSecDM_.getXSec(tp,s[1],s[0],sigma=1)/xSecDM_.getXSec(tp,s[1],s[0]) - 1)**2))
        #obsDown.append(xsec*res[(s[0],s[1],s[2])]['-1.000']*math.sqrt(0.3**2 + (1 - xSecDM_.getXSec(tp,s[1],s[0],sigma=-1)/xSecDM_.getXSec(tp,s[1],s[0]))**2))

        # technicality
        zeros.append(0)


    except KeyError:
        print "Result not found for"

#raise NotImplementedError

a_mass      = array('d',mass)
a_obs       = array('d',obs)
a_obsUp     = array('d',obsUp)
a_obsDown   = array('d',obsDown)
a_exp       = array('d',exp) 
a_expDL     = array('d',expDL) 
a_expSL     = array('d',expSL) 
a_expZL     = array('d',expZL) 
a_exp1Up    = array('d',exp1Up) 
a_exp2Up    = array('d',exp2Up) 
a_exp1Down  = array('d',exp1Down) 
a_exp2Down  = array('d',exp2Down) 
a_zeros     = array('d',zeros)
a_xsecs     = array('d',xsecs)

exp2Sigma   = ROOT.TGraphAsymmErrors(len(zeros), a_mass, a_exp, a_zeros, a_zeros, a_exp2Down, a_exp2Up)
exp1Sigma   = ROOT.TGraphAsymmErrors(len(zeros), a_mass, a_exp, a_zeros, a_zeros, a_exp1Down, a_exp1Up)
exp         = ROOT.TGraphAsymmErrors(len(zeros), a_mass, a_exp, a_zeros, a_zeros, a_zeros, a_zeros)
expDL       = ROOT.TGraphAsymmErrors(len(zeros), a_mass, a_expDL, a_zeros, a_zeros, a_zeros, a_zeros)
expSL       = ROOT.TGraphAsymmErrors(len(zeros), a_mass, a_expSL, a_zeros, a_zeros, a_zeros, a_zeros)
expZL       = ROOT.TGraphAsymmErrors(len(zeros), a_mass, a_expZL, a_zeros, a_zeros, a_zeros, a_zeros)
obs         = ROOT.TGraphAsymmErrors(len(zeros), a_mass, a_obs, a_zeros, a_zeros, a_zeros, a_zeros)
obs1Sigma   = ROOT.TGraphAsymmErrors(len(zeros), a_mass, a_obs, a_zeros, a_zeros, a_obsDown, a_obsUp)
xsecs       = ROOT.TGraphAsymmErrors(len(zeros), a_mass, a_xsecs, a_zeros, a_zeros, a_zeros, a_zeros)

exp2Sigma.SetFillColor(ROOT.kOrange)
exp1Sigma.SetFillColor(ROOT.kGreen+1)
obs1Sigma.SetFillStyle(3444)
obs1Sigma.SetFillColor(ROOT.kGray+2)
obs1Sigma.SetLineWidth(2)
obs1Sigma.SetMarkerSize(0)
#obs1Sigma.SetFillColorAlpha(ROOT.kGray, 0.5)

exp.SetLineWidth(4)
exp.SetLineStyle(2)
exp.SetLineColor(ROOT.kRed)

expDL.SetLineWidth(4)
expDL.SetLineStyle(4)
expDL.SetLineColor(ROOT.kOrange+1)

expSL.SetLineWidth(4)
expSL.SetLineStyle(3)
expSL.SetLineColor(ROOT.kBlue+1)

expZL.SetLineWidth(4)
expZL.SetLineStyle(6)
expZL.SetLineColor(ROOT.kMagenta+1)

obs.SetLineWidth(4)
xsecs.SetLineWidth(2)
xsecs.SetLineColor(ROOT.kGray+1)
#xsecs.SetLineStyle(3)

can = ROOT.TCanvas("can","",700,700)
can.SetRightMargin(0.05)
if args.logy:
    can.SetLogy()
if args.scan == 'mPhi' and False:
    can.SetLogx()

#h2 = ROOT.TH1F('h2','h2',10,10,1000)

#limits = Plot.fromHisto(name = "brazil_limits", histos = [[h]], texX = "m_{1} (GeV)", texY = "95% ..." )
#
#plotting.draw( limits, \
#        plot_directory = os.path.join(plot_directory, 'DMLimits'),
#        logX = True, logY = True,
#        sorting = False,
#        #ratio = ratio,
#        extensions = ["pdf", "png", "root"],
#        yRange = (0.01,100),
#        widths = {'x_width':700, 'y_width':700}
#        #drawObjects = drawObjects,
#        #legend = legend,
#        #canvasModifications = canvasModifications
#    )

mg = ROOT.TMultiGraph()
mg.SetTitle("Exclusion graphs")
mg.Add(exp2Sigma)
mg.Add(exp1Sigma)
#mg.Add(obs1Sigma)
y_max = 500
y_min = 0.05
if args.xsec:
    y_max = 500 if args.logy else 2
    y_min = 0.005
else:
    y_max = 500 if args.logy else 10
#if mChi == 10:
#    y_max = 5000
#    y_min = 0.2
#elif mChi == 50:
#    y_max = 50000
#    y_min = 0.2
mg.SetMaximum(y_max)
mg.SetMinimum(y_min)
mg.Draw("a3 same")
if args.scan == 'mPhi':
    if tp == 'scalar': tp_ = 'm_{#phi}'
    elif tp == 'pseudo': tp_ = 'm_{a}'
else:
    tp_ = 'm_{#chi}'
mg.GetXaxis().SetTitle(tp_+" (GeV)")
if args.xsec:
    mg.GetYaxis().SetTitle("95% CL upper limit #sigma")
else:
    mg.GetYaxis().SetTitle("95% CL upper limit #sigma/#sigma_{theory}")
min_x = min(filteredResults[scanVar].tolist()) if not args.scan == 'mPhi' else 35
mg.GetXaxis().SetRangeUser(min_x,max(filteredResults[scanVar].tolist()))

xsecs.Draw("l same")
exp.Draw("l same")
expDL.Draw("l same")
expSL.Draw("l same")
expZL.Draw("l same")
if not args.blinded: obs.Draw("l same")
leg_size = 0.04 * 8


#leg = ROOT.TLegend(0.285,0.79-leg_size,0.6,0.79)
leg = ROOT.TLegend(0.315,0.79-leg_size,0.6,0.79)
leg.SetBorderSize(1)
leg.SetFillColor(0)
leg.SetLineColor(0)
leg.SetTextSize(0.03)

leg.AddEntry(obs,"#bf{Observed}",'l')
#leg.AddEntry(obs1Sigma,"#bf{Observed #pm theory uncertainty}")
#leg.AddEntry(xsecs,"#bf{#sigma_{theory}}",'l')
leg.AddEntry(exp,"#bf{Median expected}",'l')
leg.AddEntry(expDL,"#bf{Median expected 2l}",'l')
leg.AddEntry(expSL,"#bf{Median expected 1l}",'l')
leg.AddEntry(expZL,"#bf{Median expected 0l}",'l')
leg.AddEntry(exp1Sigma,"#bf{68% expected}",'f')
leg.AddEntry(exp2Sigma,"#bf{95% expected}",'f')
leg.Draw()

none = ROOT.TH1F()

if tp == 'scalar': tp_ = 'Scalar mediator'
elif tp == 'pseudo': tp_ = 'Pseudoscalar mediator'

extraText = ""
#extraText = "Preliminary"

latex2 = ROOT.TLatex()
latex2.SetNDC()
latex2.SetTextSize(0.03)
latex2.SetTextAlign(11) # align right
if args.scan == 'mChi' and args.spin == 'scalar':
    latex2.DrawLatex(0.33,0.89,'#bf{'+tp_+', Dirac DM, m_{#phi} = '+str(fixedMass)+' GeV}')
elif args.scan == 'mChi' and args.spin == 'pseudo':
    latex2.DrawLatex(0.33,0.89,'#bf{'+tp_+', Dirac DM, m_{a} = '+str(fixedMass)+' GeV}')
else:
    latex2.DrawLatex(0.33,0.89,'#bf{'+tp_+', Dirac DM, m_{#chi} = '+str(fixedMass)+' GeV}')

latex2.DrawLatex(0.33,0.85,'#bf{g_{q} = 1, g_{DM} = 1, %s}'%("LO" if args.LO else "NLO"))

latex2.DrawLatex(0.33,0.80,'#bf{95% CL upper limits}')
#latex2.DrawLatex(0.22,0.84,'#bf{m_{#chi} = '+str(mChi)+' GeV, g_{q} = 1, g_{#chi} = 1}')

latex1 = ROOT.TLatex()
latex1.SetNDC()
latex1.SetTextSize(0.04)
latex1.SetTextAlign(11) # align right
latex1.DrawLatex(0.16,0.96,'CMS #bf{#it{'+extraText+'}}')
latex1.DrawLatex(0.71,0.96,"#bf{137 fb^{-1} (13 TeV)}")

can.RedrawAxis()

plot_directory = '/home/users/dspitzba/public_html/Stop_Run2/TTDM/'

plot_dir = os.path.join(plot_directory,args.plot_directory)
if not os.path.isdir(plot_dir):
    os.makedirs(plot_dir)

postFix = '' if not args.xsec  else '_xsec'
if not args.logy:
    postFix += '_linear'
if args.LO:
    postFix += '_LO'

if not args.blinded:
    plot_dir += ('/brazil_%s_scan_%s'%(tp, args.scan) + postFix)
else:
    plot_dir += ('/brazil_%s_scan_%s_blinded'%(tp, scanVar) + postFix)

filetypes = [".pdf",".png",".root"]

for f in filetypes:
    can.Print(plot_dir+f)


