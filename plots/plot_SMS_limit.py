'''
Create 2D limit plots.
'''

#!/usr/bin/env python
import ROOT
import sys, ctypes, os
from limitHelpers   import getContours, cleanContour, getPoints, extendContour, getProjection

ROOT.gROOT.LoadMacro("niceColorPalette.C")

def niceColorPalette(n=255):
    ROOT.niceColorPalette(n)

#ROOT.gROOT.SetBatch(True)

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--signal",           action='store',     default='T2tt',  choices=["T2tt","T2bW"], help="which signal?")
parser.add_option("--smoothAlgo",       dest="smoothAlgo",  default='k5a', choices=["k5a", "k3a", "k5b"],  action="store",  help="Which smoothing algo?")
parser.add_option("--iterations",       dest="iterations", type="int",  default=1,  action="store",  help="How many smoothing iterations?")
parser.add_option("--smooth",           action="store_true",  help="Use real data?")
(options, args) = parser.parse_args()

def toGraph2D(name,title,length,x,y,z):
    result = ROOT.TGraph2D(length)
    result.SetName(name)
    result.SetTitle(title)
    for i in range(length):
        result.SetPoint(i,x[i],y[i],z[i])
    h = result.GetHistogram()
    h.SetMinimum(min(z))
    h.SetMaximum(max(z))
    c = ROOT.TCanvas()
    result.Draw()
    del c
    #res = ROOT.TGraphDelaunay(result)
    return result

def toGraph(name,title,length,x,y):
    result = ROOT.TGraph(length)
    result.SetName(name)
    result.SetTitle(title)
    for i in range(length):
        result.SetPoint(i,x[i],y[i])
    c = ROOT.TCanvas()
    result.Draw()
    del c
    return result

# input
analysis_results = '../workflow/results/'
defFile = os.path.join(analysis_results, "%s.pkl"%options.signal)

print defFile
lumi = 137

plot_directory = os.path.abspath('/home/users/dspitzba/public_html/Stop_Run2/%s/v4/'%options.signal)
plotDir = os.path.join(plot_directory,'limits')
if options.smooth:
    plotDir += "_smooth_it%s_%s"%(options.iterations, options.smoothAlgo)

import RootTools.plot.helpers as plot_helpers
plot_helpers.copyIndexPHP( plotDir )

if not os.path.exists(plotDir):
    os.makedirs(plotDir)

graphs  = {}
hists   = {}

#nbins = 50
#nbins = 210
nbins = 135 # bin size 10 GeV

import pickle
import pandas as pd
import numpy as np
results = pickle.load(file(defFile, 'r'))

results_df = pd.DataFrame(results)
#results_df = results_df[(results_df['stop']-results_df['lsp'])<=174]

## filter out the failed fits
results_df = results_df[results_df['0.500']>0]

## load corridor results
corridor_df = pd.DataFrame.from_csv("data/corridor_limits.txt", index_col=None, parse_dates=False)

exp_graph       = toGraph2D('exp',      'exp',      len(results_df['mStop'].tolist()),results_df['mStop'].tolist(),results_df['mLSP'].tolist(),results_df['0.500'].tolist())
exp_up_graph    = toGraph2D('exp_up',   'exp_up',   len(results_df['mStop'].tolist()),results_df['mStop'].tolist(),results_df['mLSP'].tolist(),results_df['0.840'].tolist())
exp_down_graph  = toGraph2D('exp_down', 'exp_down', len(results_df['mStop'].tolist()),results_df['mStop'].tolist(),results_df['mLSP'].tolist(),results_df['0.160'].tolist())
obs_graph       = toGraph2D('obs',      'obs',      len(results_df['mStop'].tolist()),results_df['mStop'].tolist(),results_df['mLSP'].tolist(),results_df['-1.000'].tolist())
#signif_graph    = toGraph2D('signif',   'signif',   len(results_df['stop'].tolist()),results_df['stop'].tolist(),results_df['lsp'].tolist(),results_df['significance'].tolist())

graphs["exp"]       = exp_graph
graphs["exp_up"]    = exp_up_graph
graphs["exp_down"]  = exp_down_graph
graphs["obs"]       = obs_graph

#for i in ["exp","exp_up","exp_down","obs", "obs_bulk", "obs_comp"]:
for i in ["exp","exp_up","exp_down", "obs"]:
    graphs[i].SetNpx(nbins)
    graphs[i].SetNpy(nbins)
    hists[i] = graphs[i].GetHistogram().Clone()

for i in ["obs_UL","obs_up","obs_down"]:
  hists[i] = hists["obs"].Clone(i)

for i in ["obs_up","obs_down"]:
  hists[i].Reset()


for i in ["exp","exp_up","exp_down","obs"]:
    c1 = ROOT.TCanvas()
    graphs[i].Draw()
    c1.SetLogz()
    c1.Print(os.path.join(plotDir, 'scatter_%s.png'%i))
    del c1

from xSecSusy import xSecSusy
xSecSusy_ = xSecSusy()
xSecKey = "obs" # exp or obs
for ix in range(hists[xSecKey].GetNbinsX()):
    #mStop   = hists[xSecKey].GetXaxis().GetBinUpEdge(ix)
    mStop   = (hists[xSecKey].GetXaxis().GetBinUpEdge(ix)+hists[xSecKey].GetXaxis().GetBinLowEdge(ix)) / 2.
    scaleup   = xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=1) /xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=0)
    scaledown = xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=-1)/xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=0)
    xSec = xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=0)

    print "mStop: %s, x-sec: %s"%(mStop, xSec)

    for iy in range(hists[xSecKey].GetNbinsY()):
        mNeu    = (hists[xSecKey].GetYaxis().GetBinUpEdge(iy)+hists[xSecKey].GetYaxis().GetBinLowEdge(iy)) / 2.
        v       = hists[xSecKey].GetBinContent(hists[xSecKey].FindBin(mStop, mNeu)) # get the value
        hists["obs_UL"].SetBinContent(hists[xSecKey].FindBin(mStop, mNeu), v * xSec)
        hists["obs_up"].SetBinContent(hists[xSecKey].FindBin(mStop, mNeu), v*scaleup)
        hists["obs_down"].SetBinContent(hists[xSecKey].FindBin(mStop, mNeu), v*scaledown)

# set bins for y=0
for ix in range(hists[xSecKey].GetNbinsX()):
    hists["obs_UL"].SetBinContent(ix, 0, hists["obs_UL"].GetBinContent(ix,1))
    hists["obs_up"].SetBinContent(ix, 0, hists["obs_up"].GetBinContent(ix,1))
    hists["obs_down"].SetBinContent(ix, 0, hists["obs_down"].GetBinContent(ix,1))

# to get a properly closed contour
for ix in range(hists[xSecKey].GetNbinsX()):
    for iy in range(hists[xSecKey].GetNbinsY()):
        if iy>ix:
            for i in ["exp", "exp_up", "exp_down", "obs", "obs_up", "obs_down"]:
                if hists[i].GetBinContent(ix,iy) == 0:
                    hists[i].SetBinContent(ix,iy,1e6)

for i in ["exp", "exp_up", "exp_down", "obs", "obs_up", "obs_down", "obs"]:
    hists[i + "_smooth"] = hists[i].Clone(i + "_smooth")
    if options.smooth:
        for x in range(int(options.iterations)):
            hists[i + "_smooth"].Smooth(1,options.smoothAlgo)

        if options.signal == 'T2bW':
            for ix in range(hists[i].GetNbinsX()):
                for iy in range(hists[i].GetNbinsY()):
                    if iy>(ix):#  or iy==ix-1 or iy==ix-2:
                        hists[i + "_smooth"].SetBinContent(ix, iy, hists[i].GetBinContent(ix,iy))

        



ROOT.gStyle.SetPadRightMargin(0.05)
c1 = ROOT.TCanvas()
niceColorPalette(255)

hists["obs_UL"].GetZaxis().SetRangeUser(0.002, 2999)
hists["obs_UL"].Draw('COLZ')
c1.SetLogz()

c1.Print(os.path.join(plotDir, 'limit.png'))

modelname = options.signal
temp = ROOT.TFile("tmp.root","recreate")

## we currently use non-smoothed color maps!
hists["obs_UL"].Clone("temperature").Write()

contourPoints = {}

for i in ["exp", "exp_up", "exp_down", "obs", "obs_up", "obs_down", "obs"]:
    c1 = ROOT.TCanvas()
    # get ALL the contours
    contours = getContours(hists[i + "_smooth"], plotDir)
    # cleaning
    contourPoints[i] = {}
    for j,g in enumerate(contours):
        contourPoints[i][j] = [{'x': p[0], 'y':p[1]} for p in getPoints(g)]
        #contourPoints[i][j] = getPoints(g)
        cleanContour(g, model=modelname)
        #g = extendContour(g)
    contours = max(contours , key=lambda x:x.GetN()).Clone("contour_" + i)
    contours.Draw()
    c1.Print(os.path.join(plotDir, 'contour_%s.png'%i))
    contours.Write()

temp.Close()

from python.inputFile import inputFile
from python.smsPlotXSEC import smsPlotXSEC
from python.smsPlotCONT import smsPlotCONT
from python.smsPlotBrazil import smsPlotBrazil


# read input arguments
analysisLabel = "SUS-17-001"
outputname = os.path.join(plotDir, 'limit')

# read the config file
fileIN = inputFile('SMS_limit.cfg')

# classic temperature histogra
xsecPlot = smsPlotXSEC(modelname, fileIN.HISTOGRAM, fileIN.OBSERVED, fileIN.EXPECTED, fileIN.ENERGY, fileIN.LUMI, "", "asdf")
xsecPlot.Draw( lumi = lumi, zAxis_range = (10**-4,10) )
#SINGLELEP t2tt_sus19_009.root gExpNew- kGreen kOrange
from Stop_Run2.tools.helpers import getObjFromFile
#self.model.Xmin+3*xRange/100, self.model.Ymax-2.45*yRange/100*10
if options.signal == 'T2tt':
    xRange=1350
    Xmin = 150
    Xmax = 1500
    yRange = 1500
    Ymin = 0
    Ymax = 1500
elif options.signal == 'T2bW':
    xRange=1300
    Xmin = 200
    Xmax = 1500
    yRange = 1500
    Ymin = 0
    Ymax = 1500

if options.signal == 'T2tt':

    exp_0l = getObjFromFile('t2tt_sus19_010.root', 'graph_smoothed_Exp')
    exp_0l.SetLineWidth(4)
    exp_0l.SetLineStyle(6)
    exp_0l.SetLineColor(ROOT.kGreen+1)
    exp_0l.Draw("same")
    
    lexp_0l = ROOT.TGraph(2)
    lexp_0l.SetName("LExp1l")
    lexp_0l.SetTitle("LExp1l")
    lexp_0l.SetLineColor(ROOT.kGreen+1)
    lexp_0l.SetLineStyle(6)
    lexp_0l.SetLineWidth(4)
    lexp_0l.SetPoint(0, Xmin+3*xRange/100, Ymax-2.80*yRange/100*10)
    lexp_0l.SetPoint(1, Xmin+10*xRange/100, Ymax-2.80*yRange/100*10)
    lexp_0l.Draw("same")
    textExp_0l = ROOT.TLatex(Xmin+11*xRange/100, Ymax-2.95*yRange/100*10, "Expected 0l analysis")
    textExp_0l.SetTextFont(42)
    textExp_0l.SetTextSize(0.035)
    textExp_0l.Draw()
    
    
    exp_1l = getObjFromFile('t2tt_sus19_009.root', 'gExpNew')
    exp_1l.SetLineWidth(4)
    exp_1l.SetLineStyle(3)
    exp_1l.SetLineColor(ROOT.kBlue+1)
    exp_1l.Draw("same")
    
    lexp_1l = ROOT.TGraph(2)
    lexp_1l.SetName("LExp1l")
    lexp_1l.SetTitle("LExp1l")
    lexp_1l.SetLineColor(ROOT.kBlue+1)
    lexp_1l.SetLineStyle(3)
    lexp_1l.SetLineWidth(4)
    lexp_1l.SetPoint(0, Xmin+3*xRange/100, Ymax-3.30*yRange/100*10)
    lexp_1l.SetPoint(1, Xmin+10*xRange/100, Ymax-3.30*yRange/100*10)
    lexp_1l.Draw("same")
    textExp_1l = ROOT.TLatex(Xmin+11*xRange/100, Ymax-3.45*yRange/100*10, "Expected 1l analysis")
    textExp_1l.SetTextFont(42)
    textExp_1l.SetTextSize(0.035)
    textExp_1l.Draw()
    
    
    exp_2l = getObjFromFile('t2tt_sus19_011.root', 'contour_exp')
    exp_2l.SetLineWidth(4)
    exp_2l.SetLineStyle(4)
    exp_2l.SetLineColor(ROOT.kOrange+1)
    exp_2l.Draw("same")
    
    lexp_2l = ROOT.TGraph(2)
    lexp_2l.SetName("LExp2l")
    lexp_2l.SetTitle("LExp2l")
    lexp_2l.SetLineColor(ROOT.kOrange+1)
    lexp_2l.SetLineStyle(4)
    lexp_2l.SetLineWidth(4)
    lexp_2l.SetPoint(0, Xmin+3*xRange/100, Ymax-3.85*yRange/100*10)
    lexp_2l.SetPoint(1, Xmin+10*xRange/100, Ymax-3.85*yRange/100*10)
    lexp_2l.Draw("same")
    textExp_2l = ROOT.TLatex(Xmin+11*xRange/100, Ymax-3.95*yRange/100*10, "Expected 2l analysis")
    textExp_2l.SetTextFont(42)
    textExp_2l.SetTextSize(0.035)
    textExp_2l.Draw()
    
    ### ATLAS result for comparison
    showATLAS = True
    
    if showATLAS:
        import json
        atlas_0l = json.load(file('data/ATLAS_stop0l_exp.json'))
        atlas_0l_exp = ROOT.TGraph()
        atlas_0l_exp.SetPoint(0,85,0)
        iPoint = 1
        for point in reversed(atlas_0l['values']):
            print point['x'][0]['value'], point['y'][0]['value']
            if float(point['x'][0]['value'])-float(point['y'][0]['value']) < 85: continue
            atlas_0l_exp.SetPoint(iPoint, float(point['x'][0]['value']), float(point['y'][0]['value']))
            iPoint += 1
            if float(point['y'][0]['value']) < 0.1: break
        atlas_0l_exp.SetPoint(iPoint+2,1000,0)
        atlas_0l_exp.SetLineColor(ROOT.kMagenta)
        atlas_0l_exp.SetLineStyle(4)
        atlas_0l_exp.SetLineWidth(2)
        atlas_0l_exp.Draw()
    
        atlas_1l = json.load(file('data/ATLAS_stop1l_exp.json'))
        atlas_1l_exp = ROOT.TGraph()
        atlas_1l_exp.SetPoint(0,85,0)
        iPoint = 1
        for point in atlas_1l['values']:
            print point['x'][0]['value'], point['y'][0]['value']
            if float(point['x'][0]['value'])-float(point['y'][0]['value']) < 85: continue
            atlas_1l_exp.SetPoint(iPoint, float(point['x'][0]['value']), float(point['y'][0]['value']))
            iPoint += 1
            #if float(point['y'][0]['value']) < 0.1: break
        atlas_1l_exp.SetPoint(iPoint+2,1000,0)
        atlas_1l_exp.SetLineColor(ROOT.kAzure+1)
        atlas_1l_exp.SetLineStyle(4)
        atlas_1l_exp.SetLineWidth(2)
        atlas_1l_exp.Draw()

xsecPlot.Save("%sXSEC" %outputname)

temp = ROOT.TFile("tmp.root","update")
xsecPlot.c.Write("cCONT_XSEC")
temp.Close()

# only lines
contPlot = smsPlotCONT(modelname, fileIN.HISTOGRAM, fileIN.OBSERVED, fileIN.EXPECTED, fileIN.ENERGY, fileIN.LUMI, fileIN.PRELIMINARY, "")
contPlot.Draw()
contPlot.Save("%sCONT" %outputname)

# brazilian flag (show only 1 sigma)
brazilPlot = smsPlotBrazil(modelname, fileIN.HISTOGRAM, fileIN.OBSERVED, fileIN.EXPECTED, fileIN.ENERGY, fileIN.LUMI, fileIN.PRELIMINARY, "")
brazilPlot.Draw()
brazilPlot.Save("%sBAND" %outputname)

