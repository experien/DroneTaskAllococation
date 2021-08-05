from solver import *
from solution import *
from random import shuffle, sample
from dataclasses import dataclass
from heapq import *

@dataclass
class GeneticSolverParameters:
    population_size: int
    n_generation: int
    selection_ratio: float
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

            if DEBUG:
                if n_iter % len(self.population) == 0:
                    print(n_iter, "th iteration:", self.evaluator.get_best(self.population))

            n_iter += 1

        if DEBUG:
            self.print_summary(self.population)

        return self.evaluator.get_best(self.population)

    def _crossover(self, mother, father):
        cut_point = global_params.NumOfWorkflows // 2
        child = Solution(self.topology, self.evaluator)
        for i, wf in enumerate(self.topology.workflows):
            base = mother if i < cut_point else father
            prev_node = None
            for task in wf.tasks:
                target_node = base.task_to_node[task]
                if not child.mappable(prev_node, task, target_node):
                    # fix
                    fixed = False
                    if not prev_node:
                        return None

                    neighbors = list(prev_node.neighbors)
                    shuffle(neighbors)
                    for neighbor in neighbors:
                        if child.mappable(prev_node, task, neighbor):
                            target_node = neighbor
                            fixed = True
                            break

                    if not fixed:
                        return None

                child.map(prev_node, task, target_node)
                prev_node = target_node

        return child

    def _fix(self, chromosome):
        return chromosome

    # main tasks for GA
    # not used currently
    def _make_next_generation(self):
        next_generation = []
        candidates = self._select_by_rank(self.params.selection_ratio)

        # crossover
        shuffle(next_generation)
        while candidates:
            mother = candidates.pop()
            if not candidates:
                break
            father = candidates.pop()

            child = self._crossover(mother, father)
            next_generation.append(child)

        # mutation
        mutation_size = int(self.params.population_size * self.params.mutation_ratio)
        for chromosome in self.population[:mutation_size]:
            next_generation.append(self._mutate(chromosome))

        # replacement
        survivors = self._select_by_rank(1 - self.params.selection_ratio - self.params.mutation_ratio)
        next_generation.extend(survivors)

        return next_generation

    def _select_by_rank(self, ratio):
        self.population.sort(key=lambda c: c.evaluate())
        selected = []
        selection_size = int(self.params.population_size * ratio)
        iterator = iter(self.population)
        for _ in range(selection_size):
            try:
                selected.append(next(iterator))
            except StopIteration:
                break

        return selected

    def _mutate(self, chromosome):
        return chromosome

    def re_solve(self):
        pass
