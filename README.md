
# pyCIAP

![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/jhelgert/pyCIAP)

This a very simple package to solve the Combinatorial Integral Approximation Problem (CIAP)
including dwell-time constraints by a dwell-time sum-up rounding algorithm, see [1]
for the theoretical results. 

## Install

Clone this repo and then run
```
python3 setup.py install
```
inside the repo directory.

## Example:

``` python
from pyCIAP import DSUR, solveCIAPMDT
import numpy as np

# Relaxed control fulfilling SOS1-constraint
b_rel = np.array([[
    0.47131227, 0.78736104, 0.97325193, 0.53496864, 
    0.73187786, 0.07838749, 0.48948843, 0.64580892],
    [0.52868773, 0.21263896, 0.02674807, 0.46503136, 
    0.26812214, 0.92161251, 0.51051157, 0.35419108]])

# time grid
dt = 1.0
time = np.arange(0, b_rel.shape[1], dt)

# Computes a binary control fulfilling the minimum dwell times
# The dwell times are always in number of time steps, i.e. multiples of dt
b_bin = DSUR(b_rel, 1.0, time, min_up_time=3, min_down_time=3)
```
gives

``` python
array([[1, 1, 1, 0, 0, 0, 1, 1],
       [0, 0, 0, 1, 1, 1, 0, 0]])
```

In order to compare the DSUR solution to the global optimum, one can
solve the CIAP by Gurobi and use the solution as MIP start:

``` python
runtime, eps_opt, eps_dsur = solveCIAPMDT(b_rel, dt, 3, 3, start_sol=b_bin)
```

Here `eps_opt` and `eps_dsur` denote the objective values of the corresponding
CIAP, i.e. the *integrality gap*.

[1]: https://link.springer.com/article/10.1007/s10107-020-01533-x
