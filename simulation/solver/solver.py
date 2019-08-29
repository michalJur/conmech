"""
Created at 21.08.2019

@author: Michał Jureczka
@author: Piotr Bartman
"""

import numpy as np
import scipy.optimize
import numba


class Solver:

    def __init__(self, grid, F0, FN, alpha, regular_dphi, b, rho):

        self.grid = grid

        self.alpha = alpha
        self.regular_dphi = regular_dphi
        self.b = b
        self.rho = rho

        self.u = np.empty(self.grid.ind_num)

        self.B = None
        self.F = None

    def solve(self, verbose=True):
        u_vector = np.zeros(self.grid.ind_num)

        while True:
            u_vector = scipy.optimize.fsolve(self.f, u_vector)
            quality_inv = np.linalg.norm(self.f(u_vector))
            if quality_inv < 1:
                if verbose:
                    if quality_inv == 0:
                        print("Found exact solution.")
                    else:
                        print(f"Quality = {quality_inv ** -1} > 1.0 is acceptable.")
                break
            else:
                if verbose:
                    print(f"Quality = {quality_inv**-1} is too low, trying again...")

    # TODO cleanup
    @staticmethod
    @numba.jit()
    def numba_JZu(ind_num, Edges, Points, u, alpha, BorderEdgesD, BorderEdgesN, BorderEdgesC):
        result = np.zeros(ind_num)

        for i in range(ind_num):
            for e in range(-BorderEdgesD - BorderEdgesN - BorderEdgesC,
                           -BorderEdgesD - BorderEdgesN):
                e1 = Edges[e][0]
                e2 = Edges[e][1]
                if i == e1 or i == e2:
                    umL = _u_at_middle(e1, e2, ind_num, u)

                    p1 = Points[e1][:2]
                    p2 = Points[e2][:2]

                    L = _distance(p1, p2)
                    x1 = (p1[0] + p2[0]) * 0.5
                    # TODO
                    result[i] += L * 0.5 * (-x1) #self.regular_dphi(umL, b, rho)

        result *= alpha
        return result

    def JZu(self):
        JZu = Solver.numba_JZu(self.grid.ind_num, self.grid.Edges, self.grid.Points, self.u, self.alpha,
                               self.grid.BorderEdgesD, self.grid.BorderEdgesN, self.grid.BorderEdgesC)
        return JZu

    # TODO cleanup
    @staticmethod
    @numba.jit()
    def numba_Bu1(B, u):
        result = np.dot(B, u)
        return result

    def Bu1(self):
        result = Solver.numba_Bu1(self.B, self.u)
        return result

    def f(self, u_vector):
        self.u = u_vector

        X = self.Bu1() \
            + self.JZu() \
            - self.F.Zero

        return 1e8 * X


@numba.njit()
def _distance(p1, p2):
    return np.sqrt(np.sum((p1 - p2) ** 2))


@numba.njit()
def _u_at_middle(e1, e2, ind_num, u):
    result = 0
    if e1 < ind_num:
        result += u[e1] * 0.5
    if e2 < ind_num:
        result += u[e2] * 0.5
    return result