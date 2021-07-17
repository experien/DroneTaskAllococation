from abc import *
from parameters import *


class Solver(metaclass=ABCMeta):
    # main loops and operations to solve the JOAR problem

    def __init__(self, topology, allocator):
        self.topology = topology
        self.allocator = allocator

    @abstractmethod
    def solve(self):
        solution = self.allocator.allocate_workflows()
        return solution

    @abstractmethod
    def re_solve(self):
        # this method is called when Workload(Workflows & Tasks) changed
        pass


class StupidSolver(Solver):

    def solve(self):
        solutions = []
        size = 10
        for _ in range(size):
            solutions.append(self.allocator.allocate_workflows())

        best_solution = min(solutions, key=lambda s: s.evaluate())

        if DEBUG:
            print(f"[DBG] StupidSolver: {size} solutions: ")
            for solution in solutions:
                solution.print_allocation()

            print(f"[DBG] StupidSolver: {size} evaluations: ")
            for solution in solutions:
                print('      ', solution, '(BEST)' if solution == best_solution else '')

        return best_solution

    def re_solve(self):
        pass


