import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
import random
import time
import datetime
import json


np.random.seed(42)


def generate_one_baseline(
    recovery_group, 
    # pre_treatment_days = None, 
    # ymax = 15000, 
    # scale = 1.0, 
    **kwargs, 

): 


    # generate the baseline daily step for a single patient over 365 days

    '''args: 
    - recovery_group: 0, 1 or 2; representing three different recovery groups. recovery group is assumed to be not associated with flare behaviour or missingness behaviour. 
        - both group 0 and 1 feature a s-shaped growth pattern realised via a logistic growth function: 
            - y(t) = ymax / (1 + exp(-k * (t - t0)))
        

    kwargs: 

    - pre_treatment_days: if given, will be appended to the start of the baseline daily step. 

    - ymax: max daily step, default to 15000

    - t0: midpoint of growth
    
    - k: "intrinsic growth rate"

    - scale: global scale, default to 1.0

    - noise: noise level, currently deprecated

    - t1: midpoint of stagnation


    '''

    # weekly periodic variation

    assert recovery_group in [0, 1, 2], f"recovery_group must be either 0, 1 or 2; got {recovery_group}"

    y = np.zeros(365)

    # we now naively assume that the first day t = 0, patient has zero step
    y[0] = 0

    if recovery_group == 0: 
        k = kwargs.get("k", 0.1)
        t0 = kwargs.get("t0", 120)
        ymax = kwargs.get("ymax", 15000)
        burn_in_time = kwargs.get("burn_in_time", 6*7 + 1)

        # burn-in: no growth
        for t in range(1, burn_in_time): 
            y[t] = y[t-1] + np.random.normal(0, 50)
            y[t] = max(0, y[t])

        
        # s-shaped recovery pattern
        for t in range(burn_in_time, 365): 
            # impose recovery pattern
            y[t] = ymax / (1 + np.exp(-k * (t - burn_in_time - t0)))
    
    elif recovery_group == 1: 
        # recovery but after a lagged "prime time", it goes down to a certain percentage of optimum
        k = kwargs.get("k", 0.1)
        t0 = kwargs.get("t0", 100)
        ymax = kwargs.get("ymax", 15000)
        burn_in_time = kwargs.get("burn_in_time", 6*7 + 1)
        optimum_time = kwargs.get("optimum_time", 20)
        stagnated_prop = kwargs.get("stagnated_level", 0.7)
        t1 = kwargs.get("t1", 300)

        assert t1 > 2*t0 + optimum_time, f"t1 must be greater than 2*t0 + optimum_time; got {t1} and {2*t0 + optimum_time}"
        
        for t in range(1, burn_in_time): 
            y[t] = y[t-1] + np.random.normal(0, 50)
            y[t] = max(0, y[t])

        for t in range(burn_in_time, 2 * t0 + optimum_time): 
            y[t] = ymax / (1 + np.exp(-k * (t - burn_in_time - t0)))
            if y[t] > ymax: 
                y[t] = ymax
        
        # stagnation period
        B = ymax + ymax / (1 + np.exp(-k * (2*t0 - t1)))
        for t in range(2 * t0 + optimum_time, 365): 
            y[t] = B - ymax / (1 + np.exp(-k * (t - optimum_time - t1)))
            if y[t] < stagnated_prop * ymax: 
                y[t] = stagnated_prop * ymax
        
    elif recovery_group == 2: 
        # very stagnated growth
        rate = kwargs.get("rate", 10)
        burn_in_time = kwargs.get("burn_in_time", 6*7 + 1)
        ymax = kwargs.get("ymax", 15000)

        for t in range(1, burn_in_time): 
            y[t] = y[t-1] + np.random.normal(0, 50)
            y[t] = max(0, y[t])

        for t in range(burn_in_time, 365): 
            y[t] = y[t-1] + rate
            if y[t] > ymax: 
                y[t] = ymax

    


    else: 
        raise NotImplementedError

    
    y = np.ceil(y)
    t = np.arange(len(y))
    df = pd.DataFrame({"day": t, "steps": y})
    df['recovery_group'] = recovery_group

    return df



if __name__ == "__main__": 
    df = pd.DataFrame()
    for recovery_group in [0, 1, 2]:
        df_sub = generate_one_baseline(recovery_group)
        df_sub['id'] = recovery_group
        df = pd.concat([df, df_sub])

    os.makedirs("outputs", exist_ok=True)
    df.to_csv("outputs/df.csv", index=False)
    fig, ax = plt.subplots(figsize=(12, 4))
    # Plot the three trajectories on the same figure, use a different color and label for each recovery group
    colors = ['steelblue', 'orange', 'green']
    labels = ['Group 0: Typical Recovery', 'Group 1: Stagnated w/ Recovery', 'Group 2: Very Stagnated']
    for idx, recovery_group in enumerate([0, 1, 2]):
        df_sub = df[df['recovery_group'] == recovery_group]
        ax.plot(
            df_sub['day'].values,
            df_sub['steps'].values,
            linewidth=1.5,
            color=colors[idx],
            label=labels[idx]
        )
    ax.axhline(15000, color="red", linestyle="--", linewidth=1.0, label="ymax = 15 000")
    ax.set_xlabel("Day")
    ax.set_ylabel("Daily Steps")
    ax.set_title("Synthetic Baseline Daily Step Count - All Recovery Groups")
    ax.legend()
    sns.despine()
    plt.tight_layout()
    fig.savefig("outputs/baseline_plot.png", dpi=150)
    print("Saved baseline_plot.png to outputs/")
  