# TODO List:
#   - OPT (jhjang) - 검증 더 해보기, 가지치기
#   - GeneticSolver (bjkim)
#   - MA (jhjang)
#   - 엑셀/csv 파일에 저장하고 불러오기 (파라미터, 토폴로지, 배치)
#   - Evaluator - 에너지 모델? 거리?

# # ======================================================================================================
# import ma
# # 일단 random chromosome 1개(Population[0])으로 시작
# ma_record = ma.iterate(MA_MAX_ITERATION, Population[0])
# # ma.iterate(MA_MAX_ITERATION, Population, calculate_performance_chromosome)
#
# print("\n[GA Performance]")
# for x in Population:
#     calculate_performance_chromosome(x)
#
# print("\n[MA Performance]")
# for record in ma_record:
#     print(*record, 'SUM =', sum(record))
#
# ma.display(ma_record)
#


from evaluator import *
from allocator import *
from solver_ga import *
from visualizer import *
import pickle
from solver_ma import *


test_mode_settings = {
    'random' : {
        'allocator' : RandomAllocator,
        #'evaluator' : DistanceEvaluator,
        'evaluator' : EnergyEvaluator,
        'solver'    : SimpleSolver
    },
    'optimal': {
        'allocator' : OptimalAllocator,
        #'evaluator' : DistanceEvaluator,
        'evaluator' : EnergyEvaluator,
        'solver'    : OptimalSolver
    },
    'genetic': {
        'allocator' : RandomAllocator,
        'evaluator' : EnergyEvaluator,
        'solver'    : GeneticSolver,
        'params'    : GeneticSolverParameters(
                        population_size=10000,
                        n_generation=300000,
                        #selection_ratio=0.2, // not used
                        mutation_ratio=1.0
                    )
    },
    'markov': {
        'allocator' : RandomAllocator,
        'evaluator' : MultihopMarkovEvaluator,
        'solver'    : MarkovSolver,
        'params'    : MarkovSolverParameters(
            n_iteration=300,     # up to 1600 in the ref' paper.
            beta=2000   # 1, 10, 100, 1000, 2000 in the ref' paper.
        )
    }
}


def test(test_setting_name, draw=True):
    assert test_setting_name in test_mode_settings, "Invalid test name: " + test_setting_name

    if DEBUG:
        print(f"\n====================[{test_setting_name}] TEST ====================")
        print()

    setting = test_mode_settings[test_setting_name]
    evaluator = setting['evaluator'](topology)
    allocator = setting['allocator'](topology, evaluator)

    if 'params' in setting:
        solver = setting['solver'](topology, allocator, evaluator, setting['params'])
    else:
        solver = setting['solver'](topology, allocator, evaluator)

    best_solution = solver.solve()
    fairness_index = 0

    if best_solution:
        allocated_wf, best_score = best_solution.evaluate()
        allocated_wf = -allocated_wf
        title = f'best solution: {allocated_wf}/{global_params.NumOfWorkflows} workflows allocated, result={best_score:.3f}'

        if test_setting_name == 'markov':
            # energy fairnes index도 계산해서 출력
            energy_evaluator = MultihopEnergyEvaluator(topology)
            fairness_index = energy_evaluator.evaluate(best_solution)
            print(f"(energy) fairess index = {fairness_index:.3f}")
        else:
            _, fairness_index = best_solution.evaluate()
            print(f"(energy) fairess index = {fairness_index:.3f}")

        if draw:
            Visualizer.draw(title, topology, best_solution)

    else:
        title = 'No feasible solution found'

    return fairness_index


topology = StaticTopology()

# Save topology to file
# with open('dump/topology.bin', 'wb') as fout:
#     pickle.dump(topology, fout)

# Load topology from file
# with open('dump/topology_large1.bin', 'rb') as fin:
# # with open('dump/topology_small1.bin', 'rb') as fin:
#     topology = pickle.load(fin)
#     topology.print_nodes()
#     topology.print_workflow_n_tasks()
#     topology.print_distances()


#test('optimal')
#test('random')


with open('dump/density_large_genetic.txt', 'w') as f:
    for n_drone in range(10, 101, 10):
        print()
        print(f'===============[DENSITY] genetic: {n_drone} Drones===============')
        global_params = GlobalParameters()
        global_params.NumOfDrones = n_drone
        topology = StaticTopology()  # 토폴로지 재정의
        fairness_index = test('genetic', draw=False)
        f.write(str(fairness_index) + "\n")
    f.close()

with open('dump/density_large_markov.txt', 'w') as f:
    for n_drone in range(10, 101, 10):
        print()
        print(f'===============[DENSITY] markov: {n_drone} drones===============')
        global_params = GlobalParameters()
        global_params.NumOfDrones = n_drone
        topology = StaticTopology()  # 토폴로지 재정의
        fairness_index = test('markov', draw=False)
        f.write(str(fairness_index) + "\n")
    f.close()


global_params = vanilla_test_parameters

with open('dump/task_small_genetic.txt', 'w') as f:
    for n_task in range(1, 11):
        print()
        print(f'===============[Tasks per Workflow] small_genetic: {n_task} Tasks===============')
        global_params.MinTasksPerWorkFlow = 1
        global_params.MaxTasksPerWorkflow = n_task
        topology = StaticTopology()
        fairness_index = test('genetic', draw=False)
        f.write(str(fairness_index) + "\n")
    f.close()


with open('dump/task_small_markov.txt', 'w') as f:
    for n_task in range(1, 11):
        print()
        print(f'===============[Tasks per Workflow] small_markov: {n_task} Tasks===============')
        global_params.MinTasksPerWorkFlow = 1
        global_params.MaxTasksPerWorkflow = n_task
        topology = StaticTopology()
        fairness_index = test('markov', draw=False)
        f.write(str(fairness_index) + "\n")
    f.close()

# rollback
vanilla_test_parameters.MinTasksPerWorkflow = 4
vanilla_test_parameters.MaxTasksPerWorkflow = 4


global_params = GlobalParameters()

with open('dump/task_large_genetic.txt', 'w') as f:
    for n_task in range(1, 11):
        print()
        print(f'===============[Tasks per Workflow] large_genetic: {n_task} Tasks===============')
        global_params.MinTasksPerWorkFlow = 1
        global_params.MaxTasksPerWorkflow = n_task
        topology = StaticTopology()
        fairness_index = test('genetic', draw=False)
        f.write(str(fairness_index) + "\n")
    f.close()


with open('dump/task_large_markov.txt', 'w') as f:
    for n_task in range(1, 11):
        print()
        print(f'===============[Tasks per Workflow] large_markov: {n_task} Tasks===============')
        global_params.MinTasksPerWorkFlow = 1
        global_params.MaxTasksPerWorkflow = n_task
        topology = StaticTopology()
        fairness_index = test('markov', draw=False)
        f.write(str(fairness_index) + "\n")
    f.close()


global_params = vanilla_test_parameters

with open('dump/wf_small_genetic.txt', 'w') as f:
    for n_wf in range(1, 11):
        print()
        print(f'===============[No. of Workflows] small_genetic: {n_wf} workflows===============')
        global_params.NumOfWorkflows = n_wf
        topology = StaticTopology()
        fairness_index = test('genetic', draw=False)
        f.write(str(fairness_index) + "\n")
    f.close()

with open('dump/wf_small_markov.txt', 'w') as f:
    for n_wf in range(1, 11):
        print()
        print(f'===============[No. of Workflows] small_markov: {n_wf} workflows===============')
        global_params.NumOfWorkflows = n_wf
        topology = StaticTopology()
        fairness_index = test('markov', draw=False)
        f.write(str(fairness_index) + "\n")
    f.close()


global_params = GlobalParameters()

with open('dump/wf_large_genetic.txt', 'w') as f:
    for n_wf in range(5, 55, 5):
        print()
        print(f'===============[No. of Workflows] large_genetic: {n_wf} workflows===============')
        global_params.NumOfWorkflows = n_wf
        topology = StaticTopology()
        fairness_index = test('genetic', draw=False)
        f.write(str(fairness_index) + "\n")
    f.close()

with open('dump/wf_large_markov.txt', 'w') as f:
    for n_wf in range(5, 55, 5):
        print()
        print(f'===============[No. of Workflows] large_genetic: {n_wf} workflows===============')
        global_params.NumOfWorkflows = n_wf
        topology = StaticTopology()
        fairness_index = test('markov', draw=False)
        f.write(str(fairness_index) + "\n")
    f.close()
