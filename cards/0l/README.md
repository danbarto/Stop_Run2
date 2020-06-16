# All hadronic cards

To run those cards either check out:
```
git clone --single-branch --branch SUSYNano19 https://github.com/mkilpatr/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
```
or apply the corresponding [patch](../../longString.patch).
```
combineCards.py T2tt_1052_100/*txt > T2tt_1052_100.txt
combine --saveWorkspace -M AsymptoticLimits --rMin -10 --rMax 10 combinedCard.txt
```

Obtained standalone limits:
```


```

## Card details

Processes:
- TTZ: not correlated with TTZ in 2l
- znunu
- Rare
- ttbarplusw
- qcd

Systematics to (potentially) correlate:
- ISR_Weight, ISR_Weight_background
- JES
- LHEScale
- LHESigScale
- MET_Unc -> what's that?
- PDF_Weight
- PU_Weight
- Prefire_Weight
- b/b_fast
- lumi
- metres -> difference to MET_Unc?
- eff_restoptag, eff_toptag
