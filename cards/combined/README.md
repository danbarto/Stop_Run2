# Combination

## Commands

```
combineCards.py dc_1l=datacard_std_T2tt_1050_100.txt dc_2l=T2tt_1052_100_combination_shapeCard.txt > datacard_combined_T2tt_1050_100.txt
combineCards.py dc_0l=T2tt_1052_100.txt dc_1l=datacard_std_T2tt_1050_100.txt dc_2l=T2tt_1052_100_combination_shapeCard.txt > datacard_combined_T2tt_1050_100.txt
combine --saveWorkspace -M AsymptoticLimits --rMin -2 --rMax 2 datacard_combined_T2tt_1050_100.txt
```

First attempt without correlating nuisances or background processes:
```
 -- AsymptoticLimits ( CLs ) --
Observed Limit: r < 3.1840
Expected  2.5%: r < 0.1165
Expected 16.0%: r < 0.1595
Expected 50.0%: r < 0.2313
Expected 84.0%: r < 0.3419
Expected 97.5%: r < 0.4901
```

The 0l analysis seems to be very sensitive to the value rMin/rMax => need to follow up.

