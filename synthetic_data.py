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
    pre_treatment_days = None, 
    ymax = 15000, 
    scale = 1.0, 
): 

    # generate the baseline daily step for a single patient over 365 days

    '''args: 
    recovery_group: 0, 1 or 2; representing three different recovery groups. recovery group is assumed to be not associated with flare behaviour or missingness behaviour. 
    pre_treatment_days: if given, will be appended to the start of the baseline daily step. 

    ymax: max daily step, default to 15000

    scale: global scale, default to 1.0


    '''

    # weekly periodic variation

    if not recovery_group == 0: 
        raise NotImplementedError
    else: 
        y = np.zeros(365)

        # we now naively assume that the first day t = 0, patient has zero step
        y[0] = 0

        k_step = 100
        flare_time = np.random.binomial(1, 0.05, size=365)
        burn_in = np.arange(0, 6*7 + 1)
   
   
        for t in range(1, 365): 
            # impose recovery pattern
            if y[t-1] <= ymax: 
                step = min(ymax - y[t-1], np.random.normal(k_step, 50))

                if t in burn_in: 
                    step = step * 0.01
                y[t] = y[t-1] + step
            else: 
                y[t] = y[t-1] + np.random.normal(0, 50)

            # impose flare
            if flare_time[t] == 1: 
                y[t] = y[t] - np.random.normal(500, 50)
            
        # impose random variation

    

        # impose periodic pattern
        '''
        for t in range(1, 365): 

            # impose weekly pattern
            if t % 7 == 0 or t % 7 == 1:
                y[t] = y[t] + np.random.normal(500, 50)
        '''
        

        

        
    y = y * scale

    return y



if __name__ == "__main__": 
    y = generate_one_baseline(0)

    os.makedirs("outputs", exist_ok=True)

    np.save("outputs/y_baseline.npy", y)
    pd.DataFrame({"day": np.arange(len(y)), "steps": y}).to_csv("outputs/y_baseline.csv", index=False)

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(np.arange(len(y)), y, linewidth=1.2, color="steelblue")
    ax.set_xlabel("Day")
    ax.set_ylabel("Daily Steps")
    ax.set_title("Synthetic Baseline Daily Step Count (Recovery Group 0)")
    ax.axhline(15000, color="red", linestyle="--", linewidth=0.8, label="ymax = 15 000")
    ax.legend()
    sns.despine()
    plt.tight_layout()
    fig.savefig("outputs/baseline_plot.png", dpi=150)
    print("Saved y_baseline.npy, y_baseline.csv, and baseline_plot.png to outputs/")





        




