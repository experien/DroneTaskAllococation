from solver import *
from random import choice, random
import math


@dataclass
class MarkovSolverParameters:
    n_iteration: int
    beta: int


# solving JOAR Problem
class MarkovSolver(Solver):
    def __init__(self, topology, allocator, evaluator, params):
        super().__init__(topology, allocator, evaluator)
        self.params = params
        self.n_iter_iter = 10

    def solve(self):
        solutions = [self._solve() for _ in range(self.n_iter_iter)]
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
        cost_base = 1 - base.evaluate()[1]
        cost_target = 1 - target.evaluate()[1]
        param = (-0.5) * self.params.beta * (cost_target - cost_base)
        return math.exp(param)

    def re_solve(self):
        pass


# MAX_MATRIX_INDEX = NumOfDrones + NumOfEdgeServer + NumOfCloudServer  # 네트워크 연결 정보 저장 테이블의 최대 인덱스
# WorkflowInfo = [0, ]  # sequential 워크플로우 정보 저장 [(태스크 번호, 프로세싱 요구량, 대역폭요구량), ...]
# ConnectionInfo
# ProcessingRateOfDEC = [0, ]  # 각 드론, 에지서버, 클라우드 서버의 프로세싱 rate 저장
# DelayFactorOfDEC = [0, ]  # 각 드론, 에지서버, 클라우드 서버의 딜레이 factor 저장
# BandwidthOfDEC = [0, ]

# chromosome == wf 배치 정보 == solution
# chromosome 예시
#   processing_rate_of_dec =
#   bandwidth_of_dec =
#   delay_factor_of_dec =
#   workflow_status = [0, (1, True, [14, 17, 11, 19]), (2, True, [16, 12, 2, 6]), (3, True, [11, 17, 14, 21]), ..., (20, False, [0])]

#
# import matplotlib.pyplot as plt
# import copy
# import random
# from parameters import *
#
#
# # 일단 그냥 복사해왔음. 나중에 수정
# def cost_func(solution):
#     total_allocated_processing_power = 0.0
#     total_allocated_bandwidth = 0.0
#     total_allocated_delay_factor = 0.0
#
#     for i in range(1, len(solution.workflow_status)):
#         (workflow_id, workflow_status, allocated_node) = solution.workflow_status[i]
#         if workflow_status is True:
#             for (task_id, required_processing_power, required_bandwidth) in WorkflowInfo[workflow_id]:
#                 if task_id >= 0:
#                     total_allocated_processing_power += required_processing_power
#                     total_allocated_bandwidth += required_bandwidth
#             for node_id in allocated_node:
#                 total_allocated_delay_factor += DelayFactorOfDEC[node_id]
#
#     # print(total_allocated_processing_power, total_allocated_bandwidth, total_allocated_delay_factor)
#
#     return (total_allocated_processing_power, total_allocated_bandwidth, total_allocated_delay_factor)
#
#
# def iterate(n_iteration, chromosome, cost_func=cost_func):
#     cost_record = [cost_func(chromosome)]
#     temp_chromosome = copy.deepcopy(chromosome)
#     for _ in range(n_iteration):
#         markov_chain = build_markov_chain(temp_chromosome, cost_func)
#         temp_chromosome = transit(markov_chain)
#         cost_record.append(cost_func(temp_chromosome))
#
#     return cost_record
#
#
# def build_markov_chain(current_chromosome, cost_func):
#     current_chromosome_cost = cost_func(current_chromosome)
#     markov_chain = []
#
#     for i in range(1, len(current_chromosome.workflow_status)):
#         if not current_chromosome.workflow_status[i]:
#             continue
#
#         wf_no, is_allocated, task_assignments = current_chromosome.workflow_status[i]
#         if not is_allocated:
#             continue
#
#         # for each Edge, mutate
#         for j in range(1, len(task_assignments)):
#             new_chromosome = copy.deepcopy(current_chromosome)
#             if migrate(new_chromosome, i, j):
#                 new_chromosome_cost = cost_func(new_chromosome)
#                 prob = calc_prob(current_chromosome_cost, new_chromosome_cost)
#                 markov_chain.append((new_chromosome, prob))
#
#     print(f"[DBG] {len(markov_chain)} adoptable solutions")
#     return markov_chain
#
#
# def transit(markov_chain):
#     prob_upper_bound = random.random()
#     assert markov_chain, "transition failed"
#
#     acc = markov_chain[0][1]
#     for i in range(1, len(markov_chain)):
#         acc += markov_chain[i][1]
#         if acc >= prob_upper_bound:
#             return markov_chain[i-1][0]
#
#     return markov_chain[-1][0]
#
#
# def calc_prob(cur_cost, new_cost):
#     if (cur_cost < new_cost):
#         return 0
#     else:
#         return 1 / NumOfWorkflows + (sum(cur_cost) - sum(new_cost)) / 2000
#
#
# # migration == mutation?
# def migrate(chromosome, wf_no, end_node_idx):
#     def assignable(node_no, proc, bw):
#         return True
#
#     task_assignments = chromosome.workflow_status[wf_no][2]
#     start_node = task_assignments[end_node_idx-1]
#     end_node = task_assignments[end_node_idx]
#     if end_node_idx < len(task_assignments) - 1:
#         next_node = task_assignments[end_node_idx + 1]
#     else:
#         next_node = None
#
#     _, required_proc, required_bw = WorkflowInfo[wf_no][end_node_idx]
#     candidates = []
#     for k in range(len(ConnectionInfo)):
#         if ConnectionInfo[start_node][k] and \
#             (not next_node or ConnectionInfo[end_node][next_node]) and \
#             assignable(k, required_proc, required_bw):
#             candidates.append(k)
#
#     print(f"[DBG] {len(candidates)} migration candidates for current state")
#
#     if not candidates:
#         return False
#     else:
#         migrate_to = random.choice(candidates)
#         task_assignments[end_node_idx] = migrate_to
#         return True
#
#
# def display(record):
#     plt.ylabel('cost')
#     plt.xlabel('no. of iterations')
#     plt.plot(range(MA_MAX_ITERATION + 1), [sum(x) for x in record])
#     plt.show()
#
