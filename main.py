# TODO List:
#   - Evaluator 구현(에너지 모델? 거리?)
#   - OPT 구현
#   - MA 구현
#   - GeneticSolver GA 마저 만들기
#   - 환경설정 저장하고 불러오기

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


topology = StaticTopology()
evaluator = StupidEvaluator(topology)
# allocator = GreedyAllocator(topology, evaluator)
allocator = RandomAllocator(topology, evaluator)

genetic_params = GeneticSolverParameters(
    population_size=20,
    n_generation=100,
    selection_ratio=0.2,
    mutation_ratio=0.1
)
# solver = GeneticSolver(topology, allocator, genetic_params)
solver = StupidSolver(topology, allocator)

best_solution = solver.solve()
best_score = best_solution.evaluate()
title = 'best solution({:.3f})'.format(best_score)
Visualizer.draw(title, topology, best_solution)
