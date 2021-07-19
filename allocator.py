from abc import *
from solution import *
from random import shuffle
from itertools import permutations
from collections import deque


class Allocator(metaclass=ABCMeta):
    # initially allocates workflows & their tasks to the given topology
    # returns 'a' solution

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


class RandomAllocator(Allocator):
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

        neighbors = list(cur_node.neighbors)
        shuffle(neighbors)
        for next_node in neighbors:
            if self.solution.mappable(cur_node, tasks[1], next_node) and \
                    self._alloc_wf_tasks(tasks[1:], cur_node, next_node):
                return True

        self.solution.unmap(tasks[0])
        return False


class OptimalAllocator(Allocator):
    # completely searches the problem space in the given topology
    # returns the best solution among the all possible assignments
    # BFS

    def __init__(self, topology, solution, include_incomplete_cases=False):
        super().__init__(topology, solution)
        self.include_incomplete_cases = include_incomplete_cases

    def allocate_workflows(self):
        optimum = None
        n_cases = 0
        for workflows in permutations(self.topology.workflows):
            que = deque([Solution(self.topology, self.evaluator)])
            for wf in workflows:

                old_que = que
                que = deque()
                for start_node in self.topology.all_nodes:
                    self._allocate_workflow(start_node, wf, old_que, que)

            n_cases += len(que)
            sub_optimum = self.evaluator.get_best(que)
            if not optimum:
                optimum = sub_optimum
            elif sub_optimum:
                optimum = self.evaluator.get_best([optimum, sub_optimum])

        if DEBUG:
            if DEBUG_ALL_CASES:
                input("Press <ENTER> to continue...... >>>")
                print()

            print("[DBG] OptimalAllocator:")
            print(f"      found {n_cases} cases")
            print()

        return optimum

    def _allocate_workflow(self, start_node, wf, old_que, que):
        for temp_solution in old_que:
            tasks = wf.tasks[:]
            # _alloc_wf_tasks 호출 후 temp_solution은 상태 변화가 없어야 함
            self._alloc_wf_tasks(temp_solution, tasks, None, start_node, que)

    def _alloc_wf_tasks(self, temp_solution, tasks, prev_node, cur_node, que):
        # temp_solution 상태에서 wf룰 start_node에서 할당 시작하는 모든 경우를 que에 추가
        # temp_solution을 일일이 복사하면 메모리 너무 먹을 거 같아서, 백트래킹 사용하고 큐에 넣을 때만 복사해서 넣음

        if not temp_solution.map(prev_node, tasks[0], cur_node):
            return False

        if len(tasks) == 1:
            if DEBUG_ALL_CASES:
                temp_solution.print_allocation()

            que.append(temp_solution.clone())
            temp_solution.unmap(tasks[0])
            return True

        for next_node in cur_node.neighbors:
            if temp_solution.mappable(cur_node, tasks[1], next_node) and \
                    self._alloc_wf_tasks(temp_solution, tasks[1:], cur_node, next_node, que):
                temp_solution.unmap(tasks[0])
                return True

        if self.include_incomplete_cases:
            que.append(temp_solution.clone())

        temp_solution.unmap(tasks[0])
        return False
