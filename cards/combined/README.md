# Combination

## Commands

```
combineCards.py dc_0l=../0l/T2tt_1052_100.txt dc_1l=datacard_std_T2tt_1050_100.txt dc_2l=T2tt_1052_100_combination_shapeCard.txt > datacard_combined_T2tt_1050_100.txt
combine --saveWorkspace -M AsymptoticLimits --rMin -10 --rMax 10 --cminDefaultMinimizerStrategy 0 datacard_combined_T2tt_1050_100.txt
```

First attempt correlations as described below:
```
 -- AsymptoticLimits ( CLs ) --
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

### Latest correlation table

:white_check_mark: in latest result
:grey_exclamation: in next iteration

| Nuisance      | Correlated         |
| --------      | ----------         |
| Pileup        | :white_check_mark: |
| soft b-tagger | :grey_exclamation: |

### Nuisance names

For the time being we use stop-0l nuisance names in the combination.

| Stop-0l               | Stop-1l               | Stop-2l       | comment |
| -------               | -------               | -------       | ----------- |
| ISR_Weight            | ISRSystsignal         | isr           | ISR, signal |
| ISR_Weight_background | ISR16SystBG           | n/a           | ISR, background |
| JES                   | jesSystBG             | JEC           | JES for signal in 1l missing |
| LHEScale              | q2Syst                | n/a           | stop-2l has ttZ and ttbar scale uncertainty decorrelated |
| LHESigScale           | n/a                   | scale         | stop-1l has all scale variations correlated |
| MET_Unc               | SigGenMETunc          | FSmet         | gen/reco averaging for FastSim |
| PDF_Weight            | pdfSystBG             | PDF           | PDF (Bkg only) |
| PU_Weight             | pileupSyst            | PU            | |
| Prefire_Weight        | L1prefireSyst         | L1prefire     | L1 prefire |
| b                     | bTagEffHFSyst         | SFb           | b-tag, just one nuisance in stop-0l (no separate mistag) |
| b_fast                | bTagFSEffSystsignal   | btagFS        | b-tag FastSim |
| eff_restoptag         | resttagSFSyst         | n/a           | resolved top tag |
| eff_toptag            | merttagSFSyst         | n/a           | merged top tag |
| lumi                  | LumiSyst              | Lumi          | integrated luminosity |
| toppt                 | n/a                   | topPt         | top pT reweighting |

### Processes

Correlated processes (except signal, which is of course correlated)

| Stop-0l               | Stop-1l               | Stop-2l       | comment |
| -------               | -------               | -------       | ----------- |
| TTZ                   | n/a                   | TTZDL         | deliberately decorrelated because ttZ CR included in stop-2l fit |
| znunu                 | znunu                 | n/a           | |
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
- b-tagging: LF and HF seperate or combined?
- lepton SFs
- LHEscale
- correlate signal and bkg JES (1l)
