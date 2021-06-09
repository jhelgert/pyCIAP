

import numpy as np
from gurobipy import Model, GRB, Env


def solveCIAPMDT(alpha, dt, C_U, C_D, start_sol=None, gurobi_env=None, debug=False):
    """ Solves the CIAP equipped with dwell time constraints

    Args:
        alpha (np.array): given relaxed control
        dt (float): equidistant discretization step size
        C_U (int): number of minimum up dwell time steps, i.e. multiples of dt
        C_D (int): number of minimum down dwell time step, i.e. multiples of dt
        start_sol (np.array): mip start solution. Defaults to None.

    Returns:
        tuple: runtime in ms, error bounds
    """
    n_oc, n_T = alpha.shape

    # Model
    m = Model("CIAP_MDT", gurobi_env)

    # Variables
    eps = m.addVar(vtype='C', name="eps")
    delta = m.addVars(n_oc, vtype='C', name="delta")
    beta = m.addVars(n_oc, n_T, vtype='B', name="beta")

    m.update()

    # minimize eps
    m.setObjective(eps)

    # acc. control deviation constraints (linearized Max-Norm)
    for c in range(n_oc):
        for k in range(1, n_T):
            m.addConstr(delta[c] + sum(dt*(alpha[c, t] - beta[c, t])
                                       for t in range(k)) <= eps)
            m.addConstr(delta[c] + sum(dt*(alpha[c, t] - beta[c, t])
                                       for t in range(k)) >= -1.0*eps)
    # Dwell time constraints
    for c in range(n_oc):
        for k in range(n_T-C_U):
            m.addConstr(sum(beta[c, t] for t in range(k+1, k+C_U+1))
                        >= C_U * (beta[c, k+1] - beta[c, k]))
        for k in range(n_T-C_D):
            m.addConstr(sum(1 - beta[c, t] for t in range(k+1, k+C_D+1))
                        >= C_D * (beta[c, k] - beta[c, k+1]))

    # SOS1 constraint
    for t in range(n_T):
        m.addConstr(sum(beta[c, t] for c in range(n_oc)) == 1)

    if debug:
        m.write("ciap.lp")

    if start_sol is not None:
        assert start_sol.shape == (n_oc, n_T), "Wrong shape of start solution"
        for c in range(n_oc):
            for t in range(n_T):
                beta[c, t].start = start_sol[c, t]
        m.update()

        # Simple Gurobi Callback for calculating the objective value of the
        # mip start (in our case: the given solution obtained by DSUR)
        def callback(model, where):
            if where == GRB.Callback.MIPSOL:
                if model.cbGet(GRB.Callback.MIPSOL_SOLCNT) == 0:
                    # creates new model attribute '_startobjval'
                    model._startobjval = model.cbGet(GRB.Callback.MIPSOL_OBJ)

        # Solve the MILP with the callback
        m.optimize(callback)

        eps_dsur = m._startobjval
        eps_gurobi = m.objVal
    else:
        # Solve the MILP
        m.optimize()
        eps_gurobi = m.objVal
        eps_dsur = None

    sol_gurobi = np.array([int(beta[c, t].X) for c in range(n_oc)
                           for t in range(n_T)]).reshape(n_oc, n_T)

    # return the objectives
    return m.Runtime*1e3, eps_gurobi, eps_dsur
