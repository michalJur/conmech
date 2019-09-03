"""
Created at 21.08.2019

@author: Piotr Bartman
"""

import numpy as np
from simulation.simulation_runner import SimulationRunner
from simulation.mesh.mesh import Mesh
from simulation.mesh.mesh_factory import MeshFactory
from simulation.solver.solver_factory import SolverFactory
from simulation.solver.solver import Solver
from utils.drawer import Drawer
import numba


class Setup:
    gridHeight = 1
    cells_number = (20, 20)  # number of triangles per aside
    grid_left_border = Mesh.DIRICHLET
    grid_top_border = Mesh.DIRICHLET
    grid_right_border = Mesh.DIRICHLET
    grid_bottom_border = Mesh.DIRICHLET

    alpha = 0

    b = 3
    rho = 1e-3

    @staticmethod
    def F0(x1, x2):
        result = 0
        return result

    @staticmethod
    def FN(x1, x2):
        result = 0
        return result

    @staticmethod
    @numba.jit()
    def regular_dphi(r, b, rho):
        x = r - b
        result = x / np.sqrt(x**2 + rho**2)
        return result

    @staticmethod
    @numba.jit()
    def ub(x1, x2, b):
        if x2 == 0:
            result = b
        else:
            result = 0
        return result


if __name__ == '__main__':
    setup = Setup()
    mesh = MeshFactory.construct(setup.cells_number[0],
                                 setup.cells_number[1],
                                 setup.gridHeight,
                                 left=setup.grid_left_border,
                                 top=setup.grid_top_border,
                                 right=setup.grid_right_border,
                                 bottom=Mesh.CONTACT)  # !!!
    B = SolverFactory.construct_B(mesh)
    B = B[(1, 1)] + B[(2, 2)]
    ub = np.empty(mesh.ind_num)
    for i in range(mesh.ind_num):
        p = mesh.Points[i]
        ub[i] = setup.ub(p[0], p[1], setup.b)
    Bu = Solver.numba_Bu1(B, ub)

    mesh = MeshFactory.construct(setup.cells_number[0],
                                 setup.cells_number[1],
                                 setup.gridHeight,
                                 left=setup.grid_left_border,
                                 top=setup.grid_top_border,
                                 right=setup.grid_right_border,
                                 bottom=setup.grid_bottom_border)
    solver = SolverFactory.construct(mesh=mesh, setup=setup)
    solver.Bu = Bu[:mesh.ind_num]

    solver.solve(verbose=True)

    # TODO draw "Contact" border as b
    Drawer.draw(solver, setup)
