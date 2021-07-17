from solver import *
from solution import *
from random import shuffle
from dataclasses import dataclass


@dataclass
class GeneticSolverParameters:
    population_size: int
    n_generation: int
    selection_ratio: float
    mutation_ratio: float


class GeneticSolver(Solver):
    def __init__(self, topology, allocator, params):
        super().__init__(topology, allocator)
        self.params = params
        self.population = []

    def solve(self):
        self.population = []
        for _ in range(self.params.population_size):
            chromosome = self.allocator.allocate_workflows()
            self.population.append(chromosome)

        if DEBUG:
            print(f"[DBG] Initial population (size {len(self.population)}): ")
            for chromosome in self.population:
                print('      ', chromosome)

        for _ in range(self.params.n_generation):
            self.population = self._make_next_generation()

        return max(self.population, key=lambda c: c.evaluate())

    # main tasks for GA
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

    def _crossover(self, mother, father):
        return mother

    def _fix(self, chromosome):
        return chromosome

    def _mutate(self, chromosome):
        return chromosome

    def re_solve(self):
        pass
