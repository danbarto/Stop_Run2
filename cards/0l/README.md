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
 -- AsymptoticLimits ( CLs ) --
Observed Limit: r < 4.4361
Expected  2.5%: r < 0.1401
Expected 16.0%: r < 0.1966
Expected 50.0%: r < 0.2939
Expected 84.0%: r < 0.4592
Expected 97.5%: r < 0.7071

Done in 75.87 min (cpu), 75.89 min (real)
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
