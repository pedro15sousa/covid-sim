import os
import pandas as pd
import numpy as np

cur_path = "./report9/GB_suppress/output/"
f = True
stats_names = ["R0", "Trig", "Dur", "Scenario", "variable", "Total incidence", "Maximum incidence", "Mean time", "Max time", "Median time"]
variables = ["PropSocDist", "Mild", "ILI", "SARI", "Critical", "incMild", "incILI", "incSARI", "incCritical", "incDeath", "cumDeath"]
outd=None

i = "PC_CI_HQ_SD"
R = "2.6"
v = 0.75
tr = 400
y = int(tr * v)

stats = pd.DataFrame(columns=stats_names)

for j in variables:
    data1 = pd.read_csv(f"{cur_path}{i}_{tr}_{y}_R0={R}.avNE.severity.xls", delimiter='\t')
    print(data1.columns)
    data1 = data1[data1['t'] <= 800]
    cnm = f"{i}:{v}"
    tmp = data1[j].astype(float)

    if j == "PropSocDist":
        tmax = tmp.max() + 1e-10
        tmp /= tmax
        tmed = tmp.mean()
        tmp = np.where(tmp == 0, 0, 1)
        tmp2 = np.diff(tmp, prepend=0)
        mi = np.sum(tmp2 == 1)
        ton = data1['t'][tmp2 == 1]
        toff = data1['t'][tmp2 == -1]
        if not ton.empty and not toff.empty:
            mt = toff.iloc[0] - ton.iloc[0]
            tm = ton.iloc[1] - toff.iloc[0] if len(ton) > 1 else np.nan
        else:
            mt = np.nan
            tm = np.nan
        
        si = tmed * 730 / (730 - 80)
    else:
        si = tmp.sum()
        mi = tmp.max()
        t2 = tmp * data1['t']
        ct = tmp.cumsum()
        medi = si / 2
        tmed = (ct > medi).idxmax() - 1
        mt = t2.sum() / si
        tm = tmp.idxmax() - 1

    stats_row = pd.DataFrame([[R, tr, v, i, j, si, mi, mt, tm, tmed]], columns=stats_names)
    stats = pd.concat([stats, stats_row], ignore_index=True)

# Save the stats dataframe to a CSV file
stats.to_csv(f"{cur_path}stats_contain_specific.csv", index=False)