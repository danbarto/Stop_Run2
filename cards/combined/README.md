# Combination

## Commands

```
combineCards.py dc_0l=../0l/T2tt_1052_100.txt dc_1l=datacard_std_T2tt_1050_100.txt dc_2l=T2tt_1052_100_combination_shapeCard.txt > datacard_combined_T2tt_1050_100.txt
combine --saveWorkspace -M AsymptoticLimits --rMin -10 --rMax 10 --cminDefaultMinimizerStrategy 0 datacard_combined_T2tt_1050_100.txt
```

First attempt correlations as described below:
```
 -- AsymptoticLimits ( CLs ) --
Observed Limit: r < 0.2078
Expected  2.5%: r < 0.1133
Expected 16.0%: r < 0.1558
Expected 50.0%: r < 0.2266
Expected 84.0%: r < 0.3376
Expected 97.5%: r < 0.4858
```
More than 20% better than stop-0l alone.

## Correlations

### Nuisance names and correlations

:white_check_mark: correlation implemented in latest result
:recycle: needs some more dicussion
:x: not correlated / not considered

For the time being we use stop-0l nuisance names in the combination.

| Stop-0l               | Stop-1l               | Stop-2l       | comment       | Correlation implemented |
| -------               | -------               | -------       | -----------   | -------                 |
| ISR_Weight            | ISRSystsignal         | isr           | ISR, signal   | :white_check_mark: | 
| ISR_Weight_background | ISR16SystBG           | n/a           | ISR, background | :white_check_mark: |
| LHEScale              | q2Syst                | n/a           | stop-2l has ttZ and ttbar scale uncertainty decorrelated | :recycle: |
| LHESigScale           | n/a                   | scale         | stop-1l has all scale variations correlated | :recycle: |
| PDF_Weight            | pdfSyst(BG)           | PDF           | PDF (Bkg and tt+DM only) | :white_check_mark: |
| JES                   | jesSyst               | JEC           | JES | :white_check_mark: |
| PU_Weight             | pileupSyst            | PU            | pileup modeling | :white_check_mark: |
| Prefire_Weight        | L1prefireSyst         | L1prefire     | L1 prefire | :white_check_mark: |
| b_heavy               | bTagEffHFSyst         | SFb           | b-tag | :white_check_mark: |
| b_light               | bTagEffLFSyst         | SFl           | mistag | :white_check_mark: |
| b_fast                | bTagFSEffSystsignal   | btagFS        | b-tag FastSim | :white_check_mark: |
| ivfunc                | softbSFSyst           | n/a           | soft b-tagging | :white_check_mark: |
| eff_restoptag         | resttagSFSyst         | n/a           | resolved top tag | :white_check_mark: |
| eff_toptag            | merttagSFSyst         | n/a           | merged top tag | :white_check_mark: |
| lumi                  | LumiSyst              | Lumi          | integrated luminosity | :white_check_mark: |
| toppt                 | n/a                   | topPt         | top pT reweighting | :white_check_mark: |
| TTZ_SF                | ttZxsecSystZ          | TTZ_SF        | ttZ x-sec uncertainty | :white_check_mark: |
| trigger_err           | TrigSyst              | trigger2l     | correlate 0l & 1l (same triggers) | :white_check_mark: |
| metres                | n/a                   | unclEn        | unclustered energy modeling | :white_check_mark: |
| MET_Unc               | SigGenMETunc          | FSmet         | gen/reco averaging for FastSim | :white_check_mark: |
| eff_e/err_mu/eff_tau  | lepSFSyst/tauSFSyst2l | leptonSF      | lepton ID/isolation SFs. Not correlated. | :x: |

### Processes

Correlated processes (except signal, which is of course correlated)

| Stop-0l               | Stop-1l               | Stop-2l       | comment |
| -------               | -------               | -------       | ----------- |
| TTZ                   | znunu                 | TTZ.          | all ttZ processes scaled to same x-sec value |
| znunu                 | n/a.                  | n/a           | |
| Rare                  | n/a                   | TTXNoZ        | not yet correlated. should it be? |
| ttbarplusw            | n/a                   | n/a           | lost lepton. correlate with 1lW or 1ltop from stop-1l? |
| qcd                   | n/a                   | n/a           | |
| n/a                   | 1lW                   | n/a           | see above |
| n/a                   | 2l                    | n/a           | lost lepton. correlate with TTJets from stop-2l? |
| n/a                   | 1ltop                 | n/a           | see above |
| n/a                   | n/a                   | TTJets        | ttbar/single t, 2l |
| n/a                   | n/a                   | DY            | Z->ll |
| n/a                   | n/a                   | multiboson    | VV/VVV |

### Open uncertainties
- b-tagging: LF and HF seperate or combined? -> combined :white_check_mark:
- lepton SFs. Not correlated for now
- LHEscale. Split?
- correlate signal and bkg JES (1l) :white_check_mark:
