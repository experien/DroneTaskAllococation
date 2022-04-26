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
                        n_generation=10000,
                        #selection_ratio=0.2, // not used
                        mutation_ratio=1.0
                    )
    },
    'markov': {
        'allocator' : RandomAllocator,
        'evaluator' : MultihopEnergyEvaluator,
        'solver'    : MarkovSolver,
        'params'    : MarkovSolverParameters(
            n_iteration=2000,     # up to 1600 in the ref' paper.
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
    if best_solution:
        allocated_wf, best_score = best_solution.evaluate()
        allocated_wf = -allocated_wf
        title = f'best solution: {allocated_wf}/{len(topology.workflows)} workflows allocated, result={best_score:.3f}'
    else:
        title = 'No feasible solution found'

    if draw:
        Visualizer.draw(title, topology, best_solution)


# Save topology to file
# topology = StaticTopology()
# with open('dump/topology.bin', 'wb') as fout:
#     pickle.dump(topology, fout)

# Load topology from file
# with open('dump/topology_large1.bin', 'rb') as fin:
with open('dump/topology_small1.bin', 'rb') as fin:
    topology = pickle.load(fin)
    topology.print_nodes()
    topology.print_workflow_n_tasks()
    topology.print_distances()

#test('random')
test('genetic', draw=True)
#test('markov', draw=True)
#test('optimal')
