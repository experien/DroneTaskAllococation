from evaluator import *
from allocator import *
from solver_ga import *
from visualizer import *
import pickle
from solver_ma import *


test_mode_settings = {
    'random' : {
        'allocator' : RandomAllocator,
        'evaluator' : SingleHopEvaluator,
        'solver'    : SimpleSolver
    },
    'optimal': {
        'allocator' : OptimalAllocator,
        'evaluator' : SingleHopEvaluator,
        'solver'    : OptimalSolver
    },
    'genetic': {
        'allocator' : RandomAllocator,
        'evaluator' : SingleHopEvaluator,
        'solver'    : GeneticSolver,
        'params'    : GeneticSolverParameters(
                        population_size=10000,
                        n_generation=1000000,
                        mutation_ratio=1.0
                        # selection_ratio=0.2, // not used
                    )
    },
    'markov': {
        'allocator' : RandomAllocator,
        'evaluator' : MultiHopMarkovEvaluator,
        'solver'    : MarkovSolver,
        'params'    : MarkovSolverParameters(
                        n_iteration=350,     # up to 1600 in the ref' paper.
                        beta=2000   # 1, 10, 100, 1000, 2000 in the ref' paper.
                    )
    }
}


class TestSet:
    def __init__(self, toppology_gen, dump_filename, topology_print=False, topology_savefile=""):
        assert toppology_gen in ["new", "load_small", "load_large", "load_Xlarge"]  # 논문에는 small, medium, large
        self.topology_gen = toppology_gen
        self.dump_filename = dump_filename

        if self.topology_gen == "load_small":
            with open('dump/topology_small1.bin', 'rb') as fin:
                self.topology = pickle.load(fin)
        elif self.topology_gen == "load_large":
            with open('dump/topology_large1.bin', 'rb') as fin:
                self.topology = pickle.load(fin)
        elif self.topology_gen == "load_large":
            with open('dump/topology_Xlarge1.bin', 'rb') as fin:
                self.topology = pickle.load(fin)
        else:
            self.topology = StaticTopology()

        if topology_print:
            self.topology.print_nodes()
            self.topology.print_workflow_n_tasks()
            self.topology.print_distances()

        if topology_savefile != "":
            with open('dump/' + topology_savefile, 'wb') as fout:
                pickle.dump(self.topology, fout)

    def run(self, title, mode, n_iter=1):
        with open('dump/' + self.dump_filename, "w") as f_out:
            f_out.write('total_consumption(J), fairness_index, total_routing_path_len, average_link_distance(m)\n')
            for i in range(n_iter):
                print()
                print(f'===============TestSet {title}: {i+1} th===============')
                try:
                    evaluation = self.test(mode, draw=False)
                    print(evaluation)
                    f_out.write(str(evaluation.total_energy_consumption / 1000) + " " + \
                                str(evaluation.fairness_index) + " " + \
                                str(evaluation.total_distance) + \
                                str(evaluation.average_link_distance) + "\n")
                except KeyError as e:
                    print("Exception in", i+1, "th trial:", e)
            f_out.close()

    def test(self, test_setting_name, draw=True):
        assert test_setting_name in test_mode_settings, "Invalid test name: " + test_setting_name

        if DEBUG:
            print(f"\n====================Test [{test_setting_name}] ====================")
            print()

        setting = test_mode_settings[test_setting_name]
        evaluator = setting['evaluator'](self.topology)
        allocator = setting['allocator'](self.topology, evaluator)

        if 'params' in setting:
            solver = setting['solver'](self.topology, allocator, evaluator, setting['params'])
        else:
            solver = setting['solver'](self.topology, allocator, evaluator)

        best_solution = solver.solve()

        if not best_solution:
            title = 'No feasible solution found'
            return None

        if test_setting_name == 'markov':
            final_evaluator = MultiHopEvaluator(self.topology)
        elif test_setting_name == 'genetic':
            final_evaluator = SingleHopEvaluator(self.topology)
        else:
            final_evaluator = SingleHopEvaluator(self.topology)

        if draw:
            Visualizer.draw('Best Solution', self.topology, best_solution)

        return final_evaluator.evaluate(best_solution)


#TestSet('load_small', 'genetic_small').run(title='small-genetic', mode='genetic', n_iter=10)
#TestSet('load_small', 'markov_small').run(title='small-markov', mode='markov', n_iter=10)

#TestSet('load_large', 'genetic_large').run(title='large-genetic', mode='genetic', n_iter=10)
#TestSet('load_large', 'markov_large').run(title='large-markov', mode='markov', n_iter=10)

#TestSet('load_large', 'genetic_Xlarge').run(title='Xlarge-genetic', mode='genetic', n_iter=10)
#TestSet('load_large', 'markov_Xlarge').run(title='Xlarge-markov', mode='markov', n_iter=10)

#TestSet('load_Xlarge', 'genetic_Xlarge').run(title='Xlarge-genetic', mode='genetic', n_iter=3)
TestSet('load_Xlarge', 'markov_Xlarge').run(title='Xlarge-markov', mode='markov', n_iter=5)


# with open('dump/wf_large_markov.txt', 'w') as f:
#     for n_wf in range(5, 55, 5):
#         print()
#         print(f'===============[No. of Workflows] large_genetic: {n_wf} workflows===============')
#         global_params.NumOfWorkflows = n_wf
#         topology = StaticTopology()
#         fairness_index = test('markov', draw=False)
#         f.write(str(fairness_index) + "\n")
#     f.close()
