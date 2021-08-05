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


test_mode_settings = {
    'random' : {
        'allocator' : RandomAllocator,
        'evaluator' : EnergyEvaluator,
        #'evaluator' : DistanceEvaluator,
        'solver'    : SimpleSolver
    },
    'optimal': {
        'allocator' : OptimalAllocator,
        'evaluator' : DistanceEvaluator,
        'solver'    : OptimalSolver
    },
    'genetic': {
        'allocator' : RandomAllocator,
        'evaluator' : EnergyEvaluator,
        'solver'    : GeneticSolver,
        'params'    : GeneticSolverParameters(
                        population_size=1000,
                        n_generation=10000,
                        selection_ratio=0.2,
                        mutation_ratio=0.1
                    )
    }
}


def test(test_setting_name):
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
        best_score = best_solution.evaluate()
        title = f'best solution {best_score}'
    else:
        title = 'No feasible solution found'

    Visualizer.draw(title, topology, best_solution)


topology = StaticTopology()
with open('dump/topology.bin', 'wb') as fout:
    pickle.dump(topology, fout)

# with open('dump/topology.bin', 'rb') as fin:
#     topology = pickle.load(fin)
#     topology.print_nodes()
#     topology.print_workflow_n_tasks()
#     topology.print_distances()

test('random')
#test('optimal')
test('genetic')
