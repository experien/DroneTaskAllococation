from abc import *
from solution import *
from parameters import *


class Evaluator(metaclass=ABCMeta):
    # evaluates a solution using specific metrics and models

    def __init__(self, topology):
        self.topology = topology
        self.metric = 'None'

    @abstractmethod
    def evaluate(self, solution):
        return 0

    @abstractmethod
    def get_best(self, solutions):
        return solutions[0] if solutions else None


class DistanceEvaluator(Evaluator):
    def __init__(self, topology):
        super().__init__(topology)
        self.metric = 'Distance'

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


class EnergyEvaluator(Evaluator):
    def __init__(self, topology):
        super().__init__(topology)
        self.metric = 'Energy'

    def evaluate(self, solution):
        consumption = {node:0 for node in self.topology.all_nodes}

        allocated_nodes = set()
        for wf in self.topology.workflows:
            if solution.is_allocated(wf):

                for task in wf.tasks:
                    allocated_nodes.add(solution.task_to_node[task])

                for prev_task, cur_task in zip(wf.tasks, wf.tasks[1:]):
                    prev_node = solution.task_to_node[prev_task]
                    cur_node = solution.task_to_node[cur_task]
                    consumption[prev_node] += self.topology.get_distance(prev_node, cur_node) ** 2 + prev_task.required_resources['processing_power']

        e_sum = sum(consumption.values())
        e_sqr_sum = sum(map(lambda x: x * x, consumption.values()))
        e_fairness = e_sum ** 2 / (self.topology.n_all_node * e_sqr_sum)
        #e_fairness = e_sum ** 2 / (len(allocated_nodes) * e_sqr_sum)
        return e_fairness

    def get_best(self, solutions):
        if solutions:
            return max(solutions, key=lambda solution:
            (-solution.workflow_alloc_cnt, solution.evaluate()))
        else:
            return None


class MultihopEnergyEvaluator(EnergyEvaluator):
    def __init__(self, topology):
        super().__init__(topology)
        self.metric = 'Energy'

    def evaluate(self, solution):
        consumption = {node:0 for node in self.topology.all_nodes}

        allocated_nodes = set()
        for wf in self.topology.workflows:
            if solution.is_allocated(wf):

                for task in wf.tasks:
                    allocated_nodes.add(solution.task_to_node[task])

                for prev_task, cur_task in zip(wf.tasks, wf.tasks[1:]):
                    prev_node = solution.task_to_node[prev_task]
                    cur_node = solution.task_to_node[cur_task]

                    sum_distance_sqr = 0
                    try:
                        p = solution.routing_paths[(prev_node, cur_node)]
                        for src, dst in zip(p, p[1:]):
                            sum_distance_sqr += self.topology.get_distance(src, dst) ** 2
                    except KeyError:
                        pass

                    consumption[prev_node] += sum_distance_sqr + prev_task.required_resources['processing_power']

        try:
            e_sum = sum(consumption.values())
            e_sqr_sum = sum(map(lambda x: x * x, consumption.values()))
            e_fairness = e_sum ** 2 / (len(allocated_nodes) * e_sqr_sum)
            return e_fairness
        except ZeroDivisionError:
            return 0


class MultihopMarkovEvaluator(Evaluator):
    def __init__(self, topology):
        super().__init__(topology)
        self.metric = '(BW + proc.power)'

    def evaluate(self, solution):
        cost_proc = {node: 0 for node in self.topology.all_nodes}
        cost_bw = {node: 0 for node in self.topology.all_nodes}
        cost = {node: 0 for node in self.topology.all_nodes}

        for wf in filter(lambda x: solution.is_allocated(x), self.topology.workflows):
            for task in wf.tasks:
                node = solution.task_to_node[task]
                cost_proc[node] += task.required_resources['processing_power']
                cost_bw[node] += task.required_resources['bandwidth']

            for node in self.topology.all_nodes:
                cost_proc[node] = cost_proc[node] / node.resources['processing_power']
                cost_proc[node] **= 2
                cost_bw[node] = cost_bw[node] / node.resources['bandwidth']
                cost_bw[node] **= 2
                cost[node] = cost_proc[node] + cost_bw[node]

        total_cost = sum(cost.values())
        return total_cost

    def get_best(self, solutions):
        if solutions:
            return min(solutions, key=lambda solution:
            (-solution.workflow_alloc_cnt, solution.evaluate()))
        else:
            return None
