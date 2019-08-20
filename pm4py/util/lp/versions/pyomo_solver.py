import sys
import tempfile
import numpy as np

from pyomo.environ import *
from pyomo.core import *

import time

MIN_THRESHOLD = 10 ** -12


def apply(c, Aub, bub, Aeq, beq, parameters=None):
    """
    Gets the overall solution of the problem

    Parameters
    ------------
    c
        c parameter of the algorithm
    Aub
        A_ub parameter of the algorithm
    bub
        b_ub parameter of the algorithm
    Aeq
        A_eq parameter of the algorithm
    beq
        b_eq parameter of the algorithm
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    sol
        Solution of the LP problem by the given algorithm
    """
    if parameters is None:
        parameters = {}

    solver = parameters["solver"] if "solver" in parameters else "glpk"
    Aub = np.asmatrix(Aub)
    if type(bub) is list and len(bub) == 1:
        bub = bub[0]
    if Aeq is not None:
        Aeq = np.asmatrix(Aeq)
    if beq is not None and type(beq) is list and len(beq) == 1:
        beq = beq[0]

    model = ConcreteModel()

    # STEP 1: creates the variable of the model
    x_list = []
    for i in range(Aub.shape[1]):
        stru = "model.x%d = Var(within=PositiveReals)" % (i)
        exec(stru)
        stru = "model.x%d" % (i)
        x_list.append(eval(stru))

    # STEP 2: creates the objective function
    obj_fun = []
    obj_fun.append("model.obj = Objective(expr = 0 ")

    for j in range(len(c)):
        if abs(c[j]) > MIN_THRESHOLD:
            if c[j] > 0:
                obj_fun.append('+')
            obj_fun.append(str(c[j]))
            obj_fun.append("*")
            obj_fun.append("model.x%d" % (j))
    obj_fun.append(", sense=minimize)")
    exec("".join(obj_fun))

    # STEP 3: creates the linear inequalities
    for i in range(Aub.shape[0]):
        ok = False
        for j in range(Aub.shape[1]):
            if abs(Aub[i, j]) > MIN_THRESHOLD:
                ok = True
                break
        if ok:
            if type(bub[i]) is float:
                left = bub[i]
            elif type(bub[i]) is np.matrix:
                left = bub[i].reshape(-1, ).tolist()[0][0]
            elif type(bub[i]) is np.ndarray:
                left = bub[i].tolist()[0]
            else:
                left = bub[i]

            constraint = ["model.constraintdiseq%d = Constraint(expr = (" % (i)]
            constraint.append(str(left))
            constraint.append(" >= ")
            for j in range(Aub.shape[1]):
                if abs(Aub[i, j]) > MIN_THRESHOLD:
                    if Aub[i, j] > 0:
                        constraint.append('+')
                    constraint.append(str(Aub[i, j]))
                    constraint.append("*")
                    constraint.append("model.x%d" % (j))
            constraint.append("))")
            exec("".join(constraint))

    # STEP 4: creates the linear equalities
    if Aeq is not None and beq is not None:
        for i in range(Aeq.shape[0]):
            ok = False
            for j in range(Aeq.shape[1]):
                if abs(Aeq[i, j]) > MIN_THRESHOLD:
                    ok = True
                    break
            if ok:
                if type(beq[i]) is float:
                    left = beq[i]
                elif type(beq[i]) is np.matrix:
                    left = beq[i].reshape(-1,).tolist()[0][0]
                elif type(beq[i]) is np.ndarray:
                    left = beq[i].tolist()[0]
                else:
                    left = beq[i]

                constraint = ["model.constrainteq%d = Constraint(expr = (" % (i)]
                constraint.append(str(left))
                constraint.append(" == ")
                for j in range(Aeq.shape[1]):
                    if abs(Aeq[i, j]) > MIN_THRESHOLD:
                        if Aeq[i, j] > 0:
                            constraint.append('+')
                        constraint.append(str(Aeq[i, j]))
                        constraint.append("*")
                        constraint.append("model.x%d" % (j))
                constraint.append("))")
                exec("".join(constraint))

    solver = SolverFactory(solver)
    solver.solve(model)

    points = []
    for i in range(Aub.shape[1]):
        points.append(eval("model.x%d()" % (i)))

    objective = model.obj()

    return {"points": points, "objective": objective}

def get_prim_obj_from_sol(sol, parameters=None):
    """
    Gets the primal objective from the solution of the LP problem

    Parameters
    -------------
    sol
        Solution of the ILP problem by the given algorithm
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    prim_obj
        Primal objective
    """
    if parameters is None:
        parameters = {}

    return sol["objective"]


def get_points_from_sol(sol, parameters=None):
    """
    Gets the points from the solution

    Parameters
    -------------
    sol
        Solution of the LP problem by the given algorithm
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    points
        Point of the solution
    """
    if parameters is None:
        parameters = {}

    return sol["points"]
