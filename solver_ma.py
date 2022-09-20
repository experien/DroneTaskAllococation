from solver import *
from random import choice, random
import math


class MarkovSolverParameters:
    def __init__(self, n_iteration, beta):
        self.n_iteration = n_iteration
        self.beta = beta


# solving JOAR Problem
class MarkovSolver(Solver):
    def __init__(self, topology, allocator, evaluator, params):
        super().__init__(topology, allocator, evaluator)
        self.params = params
        self.n_iter = 1

    def solve(self):
        solutions = [self._solve() for _ in range(self.n_iter)]
        result = self.evaluator.get_best(solutions)
        self.print_summary([result])
        return result

    def _solve(self):
        current_solution = self.allocator.allocate_workflows()
        candidate_solutions = []
        for iter_cnt in range(self.params.n_iteration):
            for wf in self.topology.workflows:
                tmp = wf.tasks[:] + [None]
                for t1, t2, t3 in zip(tmp, tmp[1:], tmp[2:]):
                    node1 = current_solution.task_to_node[t1]
                    node2 = current_solution.task_to_node[t2]
                    node3 = current_solution.task_to_node[t3] if t3 else None

                    #candidate_node = node1.neighbors
                    candidate_node = set(self.topology.all_nodes) - set(current_solution.wf_to_nodes[wf].keys())
                    if node3: candidate_node = candidate_node & node3.neighbors
                    candidate_node -= {node2}
                    candidate_node = set(filter(
                        lambda target_node: current_solution.mappable(node1, t2, target_node, multihop=True),
                        candidate_node)
                    )

                    if candidate_node:
                        target_node = choice(list(candidate_node))
                        new_solution = current_solution.clone()
                        new_solution.unmap(t2)
                        new_solution.map(node1, t2, target_node, multihop=True)
                        candidate_solutions.append(new_solution)

            if candidate_solutions:
                current_solution = self._select(current_solution, candidate_solutions)

            if DEBUG_ALL_CASES or DEBUG and iter_cnt % (self.params.n_iteration // 10) == 0:
                if candidate_solutions:
                    print(f'[DBG] MA#{iter_cnt}: {current_solution.evaluate()}')
                else:
                    print(f'[DBG] MA#{iter_cnt}: transition failed')

        return current_solution

    # randomly select a solution among candidates according to transition_rates of them
    def _select(self, base, candidates):
        if not candidates:
            return None

        transition_rate = [self._get_transition_rate(base, solution) for solution in candidates]
        threshold = random() * sum(transition_rate)
        rate_sum = 0
        for i in range(len(candidates)):
            rate_sum += transition_rate[i]
            if threshold < rate_sum:
                return candidates[i]

        return candidates[-1]

    def _get_transition_rate(self, base, target):
        # energy fairness: the higher, the better. so change it to 'cost'
        cost_base = 1 - base.evaluate().total_cost
        cost_target = 1 - target.evaluate().total_cost
        param = (-0.5) * self.params.beta * (cost_target - cost_base)
        return math.exp(param)

    def re_solve(self):
        pass
