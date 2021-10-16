from pyCIAP import DSUR, solveCIAPMDT
import numpy as np


def test_dsur():
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

    expected_result = np.array([[1, 1, 1, 0, 0, 0, 1, 1],
                                [0, 0, 0, 1, 1, 1, 0, 0]], dtype=np.int32)

    np.testing.assert_array_equal(b_bin, expected_result)
