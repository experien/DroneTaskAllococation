# JOAR Problem solving


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


import matplotlib.pyplot as plt
import copy
import random
from parameters import *


# 일단 그냥 복사해왔음. 나중에 수정
def cost_func(solution):
    total_allocated_processing_power = 0.0
    total_allocated_bandwidth = 0.0
    total_allocated_delay_factor = 0.0

    for i in range(1, len(solution.workflow_status)):
        (workflow_id, workflow_status, allocated_node) = solution.workflow_status[i]
        if workflow_status is True:
            for (task_id, required_processing_power, required_bandwidth) in WorkflowInfo[workflow_id]:
                if task_id >= 0:
                    total_allocated_processing_power += required_processing_power
                    total_allocated_bandwidth += required_bandwidth
            for node_id in allocated_node:
                total_allocated_delay_factor += DelayFactorOfDEC[node_id]

    # print(total_allocated_processing_power, total_allocated_bandwidth, total_allocated_delay_factor)

    return (total_allocated_processing_power, total_allocated_bandwidth, total_allocated_delay_factor)


def iterate(n_iteration, chromosome, cost_func=cost_func):
    cost_record = [cost_func(chromosome)]
    temp_chromosome = copy.deepcopy(chromosome)
    for _ in range(n_iteration):
        markov_chain = build_markov_chain(temp_chromosome, cost_func)
        temp_chromosome = transit(markov_chain)
        cost_record.append(cost_func(temp_chromosome))

    return cost_record


def build_markov_chain(current_chromosome, cost_func):
    current_chromosome_cost = cost_func(current_chromosome)
    markov_chain = []

    for i in range(1, len(current_chromosome.workflow_status)):
        if not current_chromosome.workflow_status[i]:
            continue

        wf_no, is_allocated, task_assignments = current_chromosome.workflow_status[i]
        if not is_allocated:
            continue

        # for each Edge, mutate
        for j in range(1, len(task_assignments)):
            new_chromosome = copy.deepcopy(current_chromosome)
            if migrate(new_chromosome, i, j):
                new_chromosome_cost = cost_func(new_chromosome)
                prob = calc_prob(current_chromosome_cost, new_chromosome_cost)
                markov_chain.append((new_chromosome, prob))

    print(f"[DBG] {len(markov_chain)} adoptable solutions")
    return markov_chain


def transit(markov_chain):
    prob_upper_bound = random.random()
    assert markov_chain, "transition failed"

    acc = markov_chain[0][1]
    for i in range(1, len(markov_chain)):
        acc += markov_chain[i][1]
        if acc >= prob_upper_bound:
            return markov_chain[i-1][0]

    return markov_chain[-1][0]


def calc_prob(cur_cost, new_cost):
    if (cur_cost < new_cost):
        return 0
    else:
        return 1 / NumOfWorkflows + (sum(cur_cost) - sum(new_cost)) / 2000


# migration == mutation?
def migrate(chromosome, wf_no, end_node_idx):
    def assignable(node_no, proc, bw):
        return True

    task_assignments = chromosome.workflow_status[wf_no][2]
    start_node = task_assignments[end_node_idx-1]
    end_node = task_assignments[end_node_idx]
    if end_node_idx < len(task_assignments) - 1:
        next_node = task_assignments[end_node_idx + 1]
    else:
        next_node = None

    _, required_proc, required_bw = WorkflowInfo[wf_no][end_node_idx]
    candidates = []
    for k in range(len(ConnectionInfo)):
        if ConnectionInfo[start_node][k] and \
            (not next_node or ConnectionInfo[end_node][next_node]) and \
            assignable(k, required_proc, required_bw):
            candidates.append(k)

    print(f"[DBG] {len(candidates)} migration candidates for current state")

    if not candidates:
        return False
    else:
        migrate_to = random.choice(candidates)
        task_assignments[end_node_idx] = migrate_to
        return True


def display(record):
    plt.ylabel('cost')
    plt.xlabel('no. of iterations')
    plt.plot(range(MA_MAX_ITERATION + 1), [sum(x) for x in record])
    plt.show()

