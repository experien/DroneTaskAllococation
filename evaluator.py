from abc import *
from solution import *
from parameters import *


class Evaluator(metaclass=ABCMeta):
    # evaluates a solution using specific metrics and models

    def __init__(self, topology):
        self.topology = topology

    @abstractmethod
    def evaluate(self, solution):
        return 0

    @abstractmethod
    def get_best(self, solutions):
        return solutions[0] if solutions else None


class StupidEvaluator(Evaluator):
    # sum of node-to-node distances
    def evaluate(self, solution):
        sum_dist = 0
        for wf in self.topology.workflows:
            if solution.is_allocated(wf):
                for prev_task, cur_task in zip(wf.tasks, wf.tasks[1:]):
                    prev_node = solution.task_to_node[prev_task]
                    cur_node = solution.task_to_node[cur_task]
                    sum_dist += self.topology.get_distance(prev_node, cur_node)

        #dist_upper_bound = self.topology.n_all_node ** 2 * (AreaXRange[1] + AreaYRange[1])
        return sum_dist

    def get_best(self, solutions):
        if solutions:
            return min(solutions, key=lambda solution:
            (-solution.workflow_alloc_cnt, solution.evaluate()))
        else:
            return None
