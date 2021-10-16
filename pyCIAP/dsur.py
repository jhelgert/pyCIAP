
import numpy as np


def accumulated_control_deviation(c, j, alpha, beta, dt):
    return 0.0 if j == 0 else sum(dt*(alpha[c, l] - beta[c, l]) for l in range(0, j+1))


# Assumption: C is multiple of dt, i.e. c_e = C / dt
def J_SUR(k, time, C):
    return [r for r in range(k, k+C) if r <= len(time)-1]

# Determines the control with max. accumulated control deviation


def control_with_maximum_deviation(j, alpha, beta, dt, time, C, forbidden_configs):
    num_controls = beta.shape[0]
    c_max = -1
    maxdev = -1.0
    allowed_configs = [c for c in range(
        num_controls) if c not in forbidden_configs]
    # No calculation needed for only one allowed configuration
    if len(allowed_configs) == 1:
        return allowed_configs[0]
    # Otherwise, find the config with max. accum. control deviation
    for c in allowed_configs:
        theta = accumulated_control_deviation(c, j, alpha, beta, dt)
        theta += sum(alpha[c, l]*dt for l in J_SUR(j, time, C))
        if theta > maxdev:
            c_max = c
            maxdev = theta
    return c_max


# Determines all forbiden configurations for intervall j
def down_time_forbidden_configs(j, beta, dt, down_time):
    e_c = int(down_time / dt)
    return [c for c in range(beta.shape[0]) if np.sum(beta[c, j-e_c+1:j]) > 0.0]

# Dwell-time sum-up rounding algorithm


def DSUR(alpha, dt, time, min_up_time, min_down_time):
    """Dwell time sum-up rounding algorithm

    Args:
        alpha (np.array): relaxed control fulfilling SOS1-constraint.
        dt (float): discretization time step
        time (np.array): discretized time grid
        min_up_time (int): minimum up dwell times (in number of time steps dt)
        min_down_time (int): minimum down dwell times (in number of time steps dt)

    Returns:
        np.array: Binary control fulfilling dwell-time constraints and SOS1-constraint.
    """
    beta = np.zeros_like(alpha)
    ca = -1
    forbidden_configs = []
    j = 0
    while j < time.shape[0]:
        if j == 0:
            C = min_up_time
        else:
            C = np.max([min_up_time, min_down_time])
        c = control_with_maximum_deviation(
            j, alpha, beta, dt, time, C, forbidden_configs)
        if c == ca:
            beta[c, j] = 1.0
            j += 1
        else:
            Jsur = J_SUR(j, time, C)
            for l in Jsur:
                beta[c, l] = 1.0
            j = max(Jsur) + 1
        # Update the set of down time forbidden configurations
        forbidden_configs = down_time_forbidden_configs(j, beta, dt, C)
    return beta.astype(np.int32)
