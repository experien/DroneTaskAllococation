from abc import *
from solution import *
from random import shuffle


class Allocator(metaclass=ABCMeta):
    # initially allocates workflows & their tasks to the given topology

    def __init__(self, topology, evaluator):
        self.topology = topology
        self.evaluator = evaluator
        self.solution = None

    @abstractmethod
    def allocate_workflows(self):
        self.solution = Solution(self.topology, self.evaluator)
        return self.solution


class GreedyAllocator(Allocator):
    # Greedy+DFS

    def allocate_workflows(self):
        self.solution = Solution(self.topology, self.evaluator)

        for wf in self.topology.workflows:
            for start_node in self.topology.all_nodes:
                if self._alloc_wf_tasks(wf.tasks[:], None, start_node):
                    break

        return self.solution

    # recursive. constraints are managed in 'self.solution'
    def _alloc_wf_tasks(self, tasks, prev_node, cur_node):
        if not self.solution.map(prev_node, tasks[0], cur_node):
            return False

        if len(tasks) == 1:
            return True

        for next_node in cur_node.neighbors:
            if self.solution.mappable(cur_node, tasks[1], next_node) and \
                    self._alloc_wf_tasks(tasks[1:], cur_node, next_node):
                return True

        self.solution.unmap(tasks[0])
        return False


class RandomAllocator(GreedyAllocator):
    def allocate_workflows(self):
        self.solution = Solution(self.topology, self.evaluator)

        for wf in self.topology.workflows:
            start_nodes = self.topology.all_nodes[:]
            shuffle(start_nodes)

            for start_node in start_nodes:
                if self._alloc_wf_tasks(wf.tasks[:], None, start_node):
                    break

        return self.solution

    # recursive. constraints are managed in 'self.solution'
    def _alloc_wf_tasks(self, tasks, prev_node, cur_node):
        if not self.solution.map(prev_node, tasks[0], cur_node):
            return False

        if len(tasks) == 1:
            return True

        neighbors = cur_node.neighbors[:]
        shuffle(neighbors)
        for next_node in neighbors:
            if self.solution.mappable(cur_node, tasks[1], next_node) and \
                    self._alloc_wf_tasks(tasks[1:], cur_node, next_node):
                return True

        self.solution.unmap(tasks[0])
        return False
