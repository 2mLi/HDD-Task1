# Task 1 Simulator - Health Data Detectives

## Overview
This project simulates daily step-count recovery trajectories for 365 days after knee surgery, including realistic individual variability and missingness.

## Files


## Requirements
- 
- 
- 
- 

## Setup
choose values of ymax that match behaviour of patient before surgery and t0 and t1

## Run 

## Trajectory parameters

The simulator uses three trajectory groups with different recovery dynamics.

| Trajectory | n | ymax | t0 | k | noise | t1 | burn_in_time | optimum_time | stagnated_level | Interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 20 | 10000 | 100 | 0.1 | 400 | 365 | 42 | 365 | 1.0 | Blue Group / high final step count |
| 1 | 50 | 8000 | 140 | 0.1 | 400 | 999 | 42 | 999 | 1.0 | Green Group / moderate final step count |
| 2 | 30 | 6000 | 300 | 0.025 | 500 | 999 | 42 | 999 | 1.0 | Orange Group / lower final step count |

## Trajectory parameter definitions

| Parameter | Meaning |
| --- | --- |
| `n` | Number of simulated patients in this trajectory group |
| `ymax` | Maximum or plateau step count |
| `t0` | Mid point of patient recovery |
| `k` | Growth rate / steepness of recovery |
| `noise` | Day-to-day random variation in steps |
| `t1` | End point or late-phase control parameter |
| `burn_in_time` | Early post-op low-activity period |
| `optimum_time` | Time by which best recovery is achieved |
| `stagnated_level` | Proportion of plateau retained after stagnation |

## Expected Outputs and File Locations

