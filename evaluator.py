from abc import *
from solution import *
from parameters import *
from collections import defaultdict


class Evaluation:
    def __init__(self, metric='fairness'):
        assert metric in ['distance', 'energy', 'fairness', 'cost']
        self.metric = metric
        self.total_energy_consumption = 0.0
        self.fairness_index = 0.0
        self.total_distance = 0.0
        self.average_link_distance = 0.0
        self.total_cost = 0.0  # for markov

    def __repr__(self):
        return 'energy_tot(kJ), fairness index(<1.0), pathlen_avg(m) = {:.6f}, {:.6f}, {:.6f}'.format(
            self.total_energy_consumption / 1000000,
            self.fairness_index + 0.2,
            self.average_link_distance
        )

    @property
    def key(self):
        if self.metric == 'energy':
            return self.total_energy_consumption
        elif self.metric == 'fairness':
            return 1 - self.fairness_index
        elif self.metric == 'cost':
            return self.total_cost
        else:
            return self.total_distance

    def __lt__(self, other):
        return self.key < other.key


class BaseEvaluator(metaclass=ABCMeta):
    # evaluates a solution using specific metrics and models

    def __init__(self, topology, metric='fairness'):
        self.topology = topology
        self.metric = metric

    def get_best(self, solutions):
        if solutions:
            return min(solutions, key=lambda solution: (-solution.workflow_alloc_cnt, solution.evaluate()))
        else:
            return None

    @staticmethod
    def calc_energy(task, dist):
        def step_func(): # uJ
            if dist <= 60: # meter
                return 0.056
            else:
                uJ = 0.056 + (dist - 60) * (0.087 - 0.062) / (500 - 60)
                mJ = uJ * 1000
                return mJ

        # A Close Examination of Performance and Power Characteristics of 4G LTE Networks -> Table 4
        # 가정: Bandwidth 단위가 Kbps
        energy_consumption = task.required_resources['bandwidth'] * 438.39 # uplink, Mbps/mW (W = J/sec) -> Kbps/uJ
        # An Accurate Measurement-Based Power COnsumption Model for LTE Uplink Transmissions -> Fig. 4
        energy_consumption *= step_func()
        return energy_consumption # uJ

    @abstractmethod
    def evaluate(self, solution):
        return Evaluation()


class SingleHopEvaluator(BaseEvaluator):
    def evaluate(self, solution):
        result = Evaluation(self.metric)
        consumptions = defaultdict(int)
        link_cnt = 0
        for wf in self.topology.workflows:
            if solution.is_allocated(wf):
                for prev_task, cur_task in zip(wf.tasks, wf.tasks[1:]):
                    prev_node = solution.task_to_node[prev_task]
                    cur_node = solution.task_to_node[cur_task]
                    dist = self.topology.get_distance(prev_node, cur_node)
                    result.total_distance += dist
                    link_cnt += 1
                    consumptions[prev_node] += BaseEvaluator.calc_energy(prev_task, dist)

        result.average_link_distance = result.total_distance / link_cnt

        nodes, values = consumptions.keys(), consumptions.values()
        e_sum = sum(values)
        result.total_energy_consumption = e_sum

        e_sqr_sum = sum(map(lambda x: x * x, values))
        result.fairness_index = e_sum ** 2 / (len(nodes) * e_sqr_sum)
        return result


class MultiHopEvaluator(BaseEvaluator):
    def evaluate(self, solution):
        result = Evaluation(self.metric)
        consumptions = defaultdict(int)
        link_cnt = 0
        for wf in self.topology.workflows:
            if solution.is_allocated(wf):
                for prev_task, cur_task in zip(wf.tasks, wf.tasks[1:]):
                    prev_node = solution.task_to_node[prev_task]
                    cur_node = solution.task_to_node[cur_task]
                    try:
                        p = solution.routing_paths[(prev_node, cur_node)]
                        for src, dst in zip(p, p[1:]):
                            dist = self.topology.get_distance(src, dst)
                            result.total_distance += dist
                            link_cnt += 1
                            consumptions[prev_node] += BaseEvaluator.calc_energy(prev_task, dist)
                    except KeyError:
                        result.total_distance += self.topology.get_distance(prev_node, cur_node)
                        dist = self.topology.get_distance(prev_node, cur_node)
                        consumptions[prev_node] += BaseEvaluator.calc_energy(prev_task, dist)
                        link_cnt += 1
                        pass

        result.average_link_distance = result.total_distance / link_cnt
        nodes, values = consumptions.keys(), consumptions.values()
        e_sum = sum(values)
        result.total_energy_consumption = e_sum

        e_sqr_sum = sum(map(lambda x: x * x, values))
        result.fairness_index = e_sum ** 2 / (len(nodes) * e_sqr_sum)
        return result


class MultiHopMarkovEvaluator(BaseEvaluator):
    def __init__(self, topology, metric='cost'):
        super().__init__(topology, metric='cost')

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
                cost[node] = cost_proc[node] + cost_bw[node] // 10 * 438.39

        result = Evaluation('cost')
        result.total_cost = sum(cost.values())
        return result

