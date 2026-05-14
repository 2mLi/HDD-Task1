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


np.random.seed(666)

noise_modes = ['random', ]

def generate_params_from_recovery_group(recovery_group, randomised = True):
    if recovery_group == 0: 
        if randomised:
            return {
                'ymax': np.random.randint(8000, 12000),
                't0': np.random.randint(75, 125),
                'k': np.random.uniform(0.05, 0.075),
                'noise': np.random.randint(100, 500),
                't1': 365,
                'burn_in_time': 6*7, 
                'optimum_time': 365,
                'stagnated_level': 1.0,
            }
        else:
            return {
                'ymax': 10000,
                't0': 100,
                'k': 0.1,
                'noise': 400,
                't1': 365,
                'burn_in_time': 6*7, 
                'optimum_time': 365,
                'stagnated_level': 1.0,
            }
        
    elif recovery_group == 1: 
        if randomised:
            return {
                'ymax': np.random.randint(6000, 8000),
                't0': np.random.randint(100, 180),
                'k': np.random.uniform(0.03, 0.05),
                'noise': np.random.randint(200, 250),
                't1': 999,
                'burn_in_time': 6*7, 
                'optimum_time': 999,
                'stagnated_level': 1.0,
            }
        else:
            return {
                'ymax': 8000,
                't0': 140,
                'k': 0.1,
                'noise': 400,
                't1': 999,
                'burn_in_time': 6*7,
                'optimum_time': 999,
                'stagnated_level': 1.0,
            }
        
    elif recovery_group == 2: 
        if randomised:
            return {
                'ymax': np.random.randint(4000, 5000),
                't0': np.random.randint(100, 300),
                'k': np.random.uniform(0.02, 0.03),
                'noise': np.random.randint(200, 250),
                't1': 999,
                'burn_in_time': 6*7, 
                'optimum_time': 999,
                'stagnated_level': 1.0,
            }
        else: 
            return {
                'ymax': 6000,
                't0': 300,
                'k': 0.025,
                'noise': 500,
                't1': 999,
                'burn_in_time': 42,
                'optimum_time': 999,
                'stagnated_level': 1.0,
            }
    else: 
        raise ValueError(f"Invalid recovery group: {recovery_group}")

def generate_one_doubly_logistic_growth(
    pre_treatment_days = None, 
    ymax = 15000, 
    t0 = 60, 
    k = 0.1, 
    t1 = 200, 
    burn_in_time = 10, 
    optimum_time = 20, 
    stagnated_level = 0.7, 
): 
    y = np.zeros(365)
    
    # init
    y[0] = 0

    # burn-in
    for t in range(1, burn_in_time): 
        # print(f'burn-in: {t}')
        y[t] = y[t-1] + np.random.normal(0, 50)
        y[t] = max(0, y[t])
    
    # growth
    for t in range(burn_in_time, min(burn_in_time + 2*t0 + optimum_time, 365)): 
        y[t] = ymax / (1 + np.exp(-k * (t - burn_in_time - t0)))
        if y[t] > ymax: 
            y[t] = ymax
    
    # stagnation
    for t in range(min(burn_in_time + 2*t0 + optimum_time, 365), 365): 
        y[t] = stagnated_level * ymax + (1 - stagnated_level) * ymax / (1 + np.exp(k * (t - burn_in_time - 2*t0 - optimum_time - t1)))
        if y[t] < stagnated_level * ymax: 
            y[t] = stagnated_level * ymax
    


    return y

def generate_noise(sigma, length = 365,mode = 'random'):
    assert mode in noise_modes, f"mode must be one of {noise_modes}; got {mode}"

    if mode == 'random':
        return np.random.normal(0, sigma, length)
    
    else:
        raise NotImplementedError






if __name__ == "__main__": 

    # simple demo - generate 9 trajectories, 3 per group
    df = pd.DataFrame()

    # generating 9 synthetic patients, 3 per recovery group
    patient_id = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    recovery_group = [item for item in [0, 1, 2] for _ in range(3)]

    for patient_id, recovery_group in zip(patient_id, recovery_group):
        print(f'generating recovery group {recovery_group}')
        params = generate_params_from_recovery_group(recovery_group, randomised = True)
        ymax = params['ymax']
        t0 = params['t0']
        k = params['k']
        noise = params['noise']
        t1 = params['t1']
        burn_in_time = params['burn_in_time']
        optimum_time = params['optimum_time']
        stagnated_level = params['stagnated_level']
        print(f'ymax: {ymax}, t0: {t0}, k: {k}, noise: {noise}, t1: {t1}, burn_in_time: {burn_in_time}, optimum_time: {optimum_time}, stagnated_level: {stagnated_level}')

        y = generate_one_doubly_logistic_growth(
            ymax=ymax, t0=t0, k=k, t1=t1,
            burn_in_time=burn_in_time, optimum_time=optimum_time,
            stagnated_level=stagnated_level,
        )
        y = y + generate_noise(noise, len(y))
        df_sub = pd.DataFrame({"day": np.arange(len(y)), "steps": y})
        df_sub['id'] = patient_id
        df_sub['recovery_group'] = recovery_group
        df = pd.concat([df, df_sub])

    os.makedirs("outputs", exist_ok=True)
    df.to_csv("outputs/df.csv", index=False)
    fig, ax = plt.subplots(figsize=(12, 8))
    # Plot all 9 patients; patients in the same recovery group share a similar colour
    group_colors = [
        ['#99ccff', '#66b2ff', '#0066cc'],   # group 0: light → dark blue
        ['#a8d5b0', '#66bb6a', '#1b5e20'],   # group 1: light → dark green
        ['#ffe08a', '#ffa726', '#e65100'],   # group 2: light → dark orange
    ]
    group_labels = ['Group blue: Typical Recovery', 'Group green: Stagnated w/ Recovery', 'Group orange: Very Stagnated']
    added_group_label = [False, False, False]
    for patient_id in range(9):
        group = patient_id // 3
        shade = patient_id % 3
        df_sub = df[df['id'] == patient_id]
        label = group_labels[group] if not added_group_label[group] else None
        added_group_label[group] = True
        ax.plot(
            df_sub['day'].values,
            df_sub['steps'].values,
            linewidth=1.5,
            color=group_colors[group][shade],
            label=label
        )
    # ax.axhline(15000, color="red", linestyle="--", linewidth=1.0, label="ymax = 15 000")
    ax.set_xlabel("Day")
    ax.set_ylabel("Daily Steps")
    ax.set_title("Synthetic Baseline Daily Step Count - All Recovery Groups")
    ax.legend()
    sns.despine()
    plt.tight_layout()
    fig.savefig("outputs/baseline_plot.png", dpi=150)
    print("Saved baseline_plot.png to outputs/")
  

### deprecated
'''
def generate_one_baseline(
    recovery_group, 
    # pre_treatment_days = None, 
    # ymax = 15000, 
    # scale = 1.0, 
    **kwargs, 

): 


    # generate the baseline daily step for a single patient over 365 days


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

    
    y = np.ceil(y)
    t = np.arange(len(y))
    df = pd.DataFrame({"day": t, "steps": y})
    df['recovery_group'] = recovery_group

    return df

'''