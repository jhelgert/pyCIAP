#distutils: language = c++

import numpy as np
cimport numpy as np

from libcpp.vector cimport vector
from cython cimport cdivision, wraparound, boundscheck
from cython.operator cimport dereference as deref

cdef extern from "<algorithm>" namespace "std" nogil:
    Iter find[Iter, T](Iter first, Iter last, const T& value) except +
    Iter max_element[Iter](Iter first, Iter last) except +

@wraparound(False)
@boundscheck(False)
cdef double accumulated_control_deviation(int c, int j, double[:, ::1] alpha, double[:, ::1] beta, double dt):
    cdef int l
    cdef double ssum = 0.0
    if j == 0:
        return 0.0
    for l in range(j+1):
        ssum += dt * (alpha[c, l] - beta[c, l])
    return ssum



cdef vector[int] J_SUR(int k, double[::1] time, int C):
    # Assumption: C is multiple of dt, i.e. c_e = C / dt
    cdef vector[int] erg
    cdef int r
    cdef int Nt = time.shape[0]
    for r in range(k, k+C):
        if r <= Nt - 1:
            erg.push_back(r)
    return erg


@wraparound(False)
@boundscheck(False)
cdef int control_with_maximum_deviation(int j, double[:, ::1] alpha, double[:, ::1] beta, double dt, double[::1] time, int C, vector[int]& forbidden_configs):
    """ Determines the control with max. accumulated control deviation """ 
    cdef int num_controls = beta.shape[0]
    cdef int c
    cdef int c_max = -1
    cdef double theta = 0.0
    cdef double maxdev = -1.0
    cdef vector[int] allowed_configs
    cdef vector[int] j_sur_steps
    
    for c in range(num_controls):
        # if c not in forbidden_configs
        if find(forbidden_configs.begin(), forbidden_configs.end(), c) == forbidden_configs.end():
            allowed_configs.push_back(c)
    # no calculation needed for only one allowed configuration
    if allowed_configs.size() == 1:
        return allowed_configs[0]
    # otherwise, find the config with max. accum. control deviation
    for c in allowed_configs:
        theta = accumulated_control_deviation(c, j, alpha, beta, dt)
        j_sur_steps = J_SUR(j, time, C)
        for l in j_sur_steps:
            theta += dt*alpha[c, l]
        if theta > maxdev:
            c_max = c
            maxdev = theta
    return c_max



@cdivision(True)
@wraparound(False)
@boundscheck(False)
cdef vector[int] down_time_forbidden_configs(int j, double[:, ::1] beta, double dt, int down_time):
    """ Determines all forbiden configurations for intervall j """
    cdef int e_c = <int>(down_time / dt)
    cdef unsigned int i, c
    cdef double ssum = 0.0
    cdef vector[int] erg
    
    for c in range(beta.shape[0]):
        ssum = 0.0
        for i in range(j-e_c+1, j):
            ssum += beta[c, i]
        if ssum > 0.0:
            erg.push_back(c)
    return erg


@wraparound(False)
@boundscheck(False)
def DSUR(double[:, ::1] alpha, double dt, double[::1] time, int min_up_time, int min_down_time):
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
    cdef vector[int] Jsur
    cdef vector[int] forbidden_configs
    cdef double[:, ::1] beta = np.zeros_like(alpha)
    cdef int c
    cdef int ca = -1
    cdef int j = 0
    while j < time.shape[0]:
        if j == 0:
            C = min_up_time
        else:
            C = min_down_time
            if min_up_time > min_down_time:
                C = min_up_time
        c = control_with_maximum_deviation(j, alpha, beta, dt, time, C, forbidden_configs)
        if c == ca:
            beta[c, j] = 1.0
            j += 1
        else:
            Jsur = J_SUR(j, time, C)
            for l in Jsur:
                beta[c, l] = 1.0
            j = deref(max_element(Jsur.begin(), Jsur.end())) + 1
        # Update the set of down time forbidden configurations
        forbidden_configs = down_time_forbidden_configs(j, beta, dt, C)
    return np.array(beta, copy=False).astype(np.int32)