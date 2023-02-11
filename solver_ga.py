from solver import *
from solution import *
from random import shuffle, sample, random, choice
from dataclasses import dataclass
from heapq import *

@dataclass
class GeneticSolverParameters:
    population_size: int
    n_generation: int
    #selection_ratio: float   # not used
    mutation_ratio: float


class GeneticSolver(Solver):
    def __init__(self, topology, allocator, evaluator, params):
        super().__init__(topology, allocator, evaluator)
        self.params = params
        self.population = []

    def solve(self):
        self.population = []
        for _ in range(self.params.population_size):
            chromosome = self.allocator.allocate_workflows()
            self.population.append(chromosome)

        heapify(self.population)

        n_iter = 0
        while n_iter < self.params.n_generation:
            # self.population = self._make_next_generation()
            mother, father = sample(self.population, 2)
            child = self._crossover(mother, father)
            if not child:
                continue

            if mother < child or father < child:
                heappop(self.population)
                heappush(self.population, child)

            if random() < self.params.mutation_ratio:
                self._mutate(choice(self.population))

            if DEBUG:
                if n_iter in [0, 10, 100, 1000] or n_iter % len(self.population) == 0:
                    answer = self.evaluator.get_best(self.population)
                    if answer:
                        print(n_iter, "th iteration:", self.evaluator.get_best(self.population))
                    else:
                        print(n_iter, "th iteration: no solution")

            n_iter += 1

        if DEBUG:
            self.print_summary(self.population)

        return self.evaluator.get_best(self.population)

    def _crossover(self, mother, father):
        # random cut point
        cut_point = randint(1, global_params.NumOfWorkflows - 1)
        child = Solution(self.topology, self.evaluator)
        for i, wf in enumerate(self.topology.workflows):
            base = mother if i < cut_point else father
            prev_node = None
            for task in wf.tasks:
                if task not in base.task_to_node:
                    return None

                target_node = base.task_to_node[task]
                if not child.mappable(prev_node, task, target_node):
                    if not prev_node:
                        return None

                    new_target = self._select_mappable_neighbor(child, prev_node, task)
                    if not new_target:
                        return None
                    else:
                        target_node = new_target

                child.map(prev_node, task, target_node)
                prev_node = target_node

        return child

    # fix(1-edge mutation)
    def _select_mappable_neighbor(self, chromosome, prev_node, task):
        assert prev_node is not None

        neighbors = list(prev_node.neighbors)
        shuffle(neighbors)
        candidates = []
        for neighbor in neighbors:
            if chromosome.mappable(prev_node, task, neighbor):
                candidates.append(neighbor)

        if not candidates:
            return None
        else:
            return choice(candidates)

    def _mutate(self, chromosome):
        for wf in self.topology.workflows:
            if wf.tasks[0] not in chromosome.task_to_node:
                return

            prev_node = chromosome.task_to_node[wf.tasks[0]]
            for task in wf.tasks[1:]:
                new_target = self._select_mappable_neighbor(chromosome, prev_node, task)
                if not new_target:
                    prev_node = chromosome.task_to_node[task]
                else:
                    chromosome.map(prev_node, task, new_target)
                    prev_node = new_target

    # main tasks for GA
    # not used currently
    # def _make_next_generation(self):
    #     next_generation = []
    #     candidates = self._select_by_rank(self.params.selection_ratio)
    #
    #     # crossover
    #     shuffle(next_generation)
    #     while candidates:
    #         mother = candidates.pop()
    #         if not candidates:
    #             break
    #         father = candidates.pop()
    #
    #         child = self._crossover(mother, father)
    #         next_generation.append(child)
    #
    #     # mutation
    #     mutation_size = int(self.params.population_size * self.params.mutation_ratio)
    #     for chromosome in self.population[:mutation_size]:
    #         next_generation.append(self._mutate(chromosome))
    #
    #     # replacement
    #     survivors = self._select_by_rank(1 - self.params.selection_ratio - self.params.mutation_ratio)
    #     next_generation.extend(survivors)
    #
    #     return next_generation
    #
    # def _select_by_rank(self, ratio):
    #     self.population.sort(key=lambda c: c.evaluate())
    #     selected = []
    #     selection_size = int(self.params.population_size * ratio)
    #     iterator = iter(self.population)
    #     for _ in range(selection_size):
    #         try:
    #             selected.append(next(iterator))
    #         except StopIteration:
    #             break
    #
    #     return selected

    def re_solve(self):
        pass
