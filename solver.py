from abc import *

from evaluator import Evaluator
from parameters import *


class Solver(metaclass=ABCMeta):
    # main loops and operations to solve the JOAR problem

    def __init__(self, topology, allocator, evaluator):
        self.topology = topology
        self.allocator = allocator
        self.evaluator = evaluator

    @abstractmethod
    def solve(self):
        solution = self.allocator.allocate_workflows()
        return solution

    @abstractmethod
    def re_solve(self):
        # this method is called when Workload(Workflows & Tasks) changed
        pass

    @staticmethod
    def _normalize(evaluations):
        if not evaluations:
            return []

        max_val = max(evaluations)
        min_val = min(evaluations)
        diff = max_val - min_val
        if diff == 0:
            return [1]

        base_0 = map(lambda x: x - min_val, evaluations)
        le_1 = map(lambda x: x / diff, base_0)
        return list(le_1)

    def print_summary(self, solutions):
        sovler_name = self.__class__.__name__

        best_solution = self.evaluator.get_best(solutions)
        if not best_solution:
            print(f"[DBG] {sovler_name}: No feasible solution found")
            return

        if DEBUG_ALL_CASES:
            for solution in solutions:
                solution.print_allocation()

        evaluations = list(map(lambda s: s.evaluate(), solutions))
        eval_norm = self._normalize(evaluations)

        print(f"[DBG] {sovler_name} summary: {len(solutions)} solutions: ")
        print("       solution, no. of allocated workflows, value, normalized: ")
        for solution, evaluation in zip(solutions, eval_norm):
            if solution is best_solution:
                solution.print_allocation()

                print('      solution#{}\t{:6}\t{:10.3f}\t{:.3f}'.format(
                    solution.id, solution.workflow_alloc_cnt, solution.evaluate(), evaluation),
                      '(BEST)' if solution is best_solution else '')

        # for solution, evaluation in zip(solutions, eval_norm):
        #     print('      solution#{}\t{:6}\t{:10.3f}\t{:.3f}'.format(
        #         solution.id, solution.workflow_alloc_cnt, solution.evaluate(), evaluation),
        #           '(BEST)' if solution is best_solution else '')


class StupidSolver(Solver):
    def __init__(self, topology, allocator, evaluator, size=200):
        super().__init__(topology, allocator, evaluator)
        self.size=size

    def solve(self):
        solutions = []
        for _ in range(self.size):
            solution = self.allocator.allocate_workflows()
            if solution:
                solutions.append(solution)

        if DEBUG:
            self.print_summary(solutions)

        best_solution = self.evaluator.get_best(solutions)
        return best_solution

    def re_solve(self):
        pass


class OptimalSolver(StupidSolver):
    def __init__(self, topology, allocator, evaluator):
        super().__init__(topology, allocator, evaluator, size=1)
