import math
import pandas as pd


import glob
import numpy as np
datacards = glob.glob('/home/users/dspitzba/WH/wh_draw/statistics/unblind_dataCRfix_newSF_allSystUpdate/datacards/*.txt')
datacards = ['datacard_std_ttbarDM_pseudo_200_1.txt']

import os
update_dir = './scaled36fb/'
if not os.path.isdir(update_dir):
    os.makedirs(update_dir)

nNuisanceString = 'kmax {}  number of nuisance parameters'

scaleFactor = 36./137

for datacard in datacards:
    cardfile = datacard.split('/')[-1]
    print "Datacard:", cardfile

    with open(datacard, 'r') as f:
        card = f.readlines()
    

    # Deal with the observation first
    obs_line = [ x for x in card if x.startswith('observation')][0]
    obs_index = card.index(obs_line)
    obs_list = obs_line.split()[1:]
    obs_np = np.array(obs_list)
    obs_np = np.round(obs_np.astype(float) * scaleFactor,0).astype(int)
    obs_scaled = ['observation'] + [str(x) for x in obs_np]

    obs_template = "{:13}"+"{:20}"*len(obs_np) + "\n"

    obs_string = obs_template.format(*obs_scaled)

    card[obs_index] = obs_string

    ## Now do the prediction. ##
    # This is more complicated because we have to rescale the control region stats (=gmN nuisances) and then the rate accordingly
    # Let's just get the rates first
    rate_line = [ x for x in card if x.startswith('rate')][0]
    rate_index = card.index(rate_line)
    rate_list = rate_line.split()[1:]
    rate_np = np.array(rate_list)
    rate_np = (rate_np.astype(float) * scaleFactor)

    # Get the Bg1lDataStat1 like nuisances
    bg1l = [ x for x in card if x.startswith('Bg1lDataStat')]
    bg1l_df = { int(x.split()[0][12:]): {'CR': int(round(int(x.split()[2])*scaleFactor,0)), 'R': float([ y for y in x.split()[3:] if y is not '-'][0])} for x in bg1l }
    # this is so fucking ugly
    for line in bg1l:
        iCR = int(line.split()[0][12:])
        index = card.index(line)
        card[index] = line.replace( ' %s '%line.split()[2], ' %s '%bg1l_df[iCR]['CR'] )
        

    for i in sorted(bg1l_df.keys()):
        rate_np[(i-1)*5+2] = bg1l_df[i]['CR']*bg1l_df[i]['R']

    # Get the Bg2lDataStat1 like nuisances
    bg2l = [ x for x in card if x.startswith('Bg2lDataStat')]
    bg2l_df = { int(x.split()[0][12:]): {'CR': int(round(int(x.split()[2])*scaleFactor,0)), 'R': float([ y for y in x.split()[3:] if y is not '-'][0])} for x in bg2l }
    for line in bg2l:
        iCR = int(line.split()[0][12:])
        index = card.index(line)
        #print
        #print iCR, bg2l_df[iCR]['CR'], bg2l_df[iCR]['R']
        #print "Line before:", line
        card[index] = line.replace( ' %s '%line.split()[2], ' %s '%bg2l_df[iCR]['CR'] )
        #print "Line after:", card[index]

    for i in sorted(bg2l_df.keys()):
        rate_np[(i-1)*5+1] = bg2l_df[i]['CR']*bg2l_df[i]['R']

    rate_scaled = ['rate'] + ['%.4f'%x for x in rate_np]

    rate_template = "{:40}"+"{:20}"*len(rate_np) + "\n"

    rate_string = rate_template.format(*rate_scaled)

    card[rate_index] = rate_string

    # Ok, so our limits are still way too good. Let's also rescale all the (MC) stat uncertainties.

    stat_template = '{:<24}{:<15}' + '{:<20}'*(len(card[-1].split())-2) + '\n'

    for line in card:
        if ('MCStat' in line) or ('ZnunuStat' in line) or ('SigStat' in line):
            # find value
            line_list = line.split()
            value = [ x for x in line_list[2:] if x is not '-'][0]
            rescaled_unc = (float(value)-1)/math.sqrt(scaleFactor)+1
            line_list[line_list.index(value)] = str(round(rescaled_unc,4) if rescaled_unc<2 else 2.)
            card[card.index(line)] = stat_template.format(*line_list)



    #obs_line = 

    #observation = [ l.split() for l in card[5:7] ]
    #prediction = [ l.split() for l in card[8:12] ]

    #new_card = card[0:2]
    #new_card.append('kmax {}  number of nuisance parameters\n'.format(len(lnNtable)+len(gmNtable)))
    #new_card += card[3:13]

    ## write the gmN nuisances
    #gmNtemplate = "{:13} {:3} {:5}" + "{:17}"*(len(gmNtable[0])-3) + '\n'
    #for gmN in gmNtable:
    #    new_card.append(gmNtemplate.format(*gmN))

    #lnNtemplate = "{:17} {:5}" + "{:17}"*(len(lnNtable[0])-2) + '\n'
    #for lnN in lnNtable:
    #    new_card.append(lnNtemplate.format(*lnN))

    with open(update_dir+cardfile, 'w') as f:
        f.writelines(card)
    

