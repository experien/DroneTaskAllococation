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
        self.temp_solution = Solution(self.topology, self.evaluator)

    @abstractmethod
    def allocate_workflows(self):
        return self.temp_solution


class GreedyAllocator(Allocator):
    # Greedy+DFS

    def allocate_workflows(self):
        self.temp_solution = Solution(self.topology, self.evaluator)

        for wf in self.topology.workflows:
            for start_node in self.topology.all_nodes:
                if self._alloc_wf_tasks(wf.tasks[:], None, start_node):
                    break

        return self.temp_solution

    # recursive. constraints are managed in 'self.solution'
    def _alloc_wf_tasks(self, tasks, prev_node, cur_node):
        if not self.temp_solution.map(prev_node, tasks[0], cur_node):
            return False

        if len(tasks) == 1:
            return True

        for next_node in cur_node.neighbors:
            if self.temp_solution.mappable(cur_node, tasks[1], next_node) and \
                    self._alloc_wf_tasks(tasks[1:], cur_node, next_node):
                return True

        self.temp_solution.unmap(tasks[0])
        return False


class RandomAllocator(Allocator):
    def allocate_workflows(self):
        self.temp_solution = Solution(self.topology, self.evaluator)

        for wf in self.topology.workflows:
            start_nodes = self.topology.all_nodes[:]
            shuffle(start_nodes)

            for start_node in start_nodes:
                if self._alloc_wf_tasks(wf.tasks[:], None, start_node):
                    break

        return self.temp_solution

    # recursive. constraints are managed in 'self.solution'
    def _alloc_wf_tasks(self, tasks, prev_node, cur_node):
        if not self.temp_solution.map(prev_node, tasks[0], cur_node):
            return False

        if len(tasks) == 1:
            return True

        neighbors = list(cur_node.neighbors)
        shuffle(neighbors)
        for next_node in neighbors:
            if self.temp_solution.mappable(cur_node, tasks[1], next_node) and \
                    self._alloc_wf_tasks(tasks[1:], cur_node, next_node):
                return True

        self.temp_solution.unmap(tasks[0])
        return False


# class OptimalAllocator(Allocator):
#     # completely searches the problem space in the given topology
#     # returns the best solution among the all possible assignments
#     # BFS
#
#     def __init__(self, topology, solution, include_incomplete_cases=False):
#         super().__init__(topology, solution)
#         self.include_incomplete_cases = include_incomplete_cases
#
#     def allocate_workflows(self):
#         optimum = None
#         n_cases = 0
#         for workflows in permutations(self.topology.workflows):
#             que = deque([Solution(self.topology, self.evaluator)])
#             for wf in workflows:
#
#                 old_que = que
#                 que = deque()
#                 for start_node in self.topology.all_nodes:
#                     self._allocate_workflow(start_node, wf, old_que, que)
#
#             n_cases += len(que)
#             sub_optimum = self.evaluator.get_best(que)
#             if not optimum:
#                 optimum = sub_optimum
#             elif sub_optimum:
#                 optimum = self.evaluator.get_best([optimum, sub_optimum])
#
#         if DEBUG:
#             print("[DBG] OptimalAllocator:")
#             print(f"      found {n_cases} cases")
#             print()
#
#         return optimum
#
#     def _allocate_workflow(self, start_node, wf, old_que, que):
#         for temp_solution in old_que:
#             tasks = wf.tasks[:]
#             # _alloc_wf_tasks 호출 후 temp_solution은 상태 변화가 없어야 함
#             self._alloc_wf_tasks(temp_solution, tasks, None, start_node, que)
#
#     def _alloc_wf_tasks(self, temp_solution, tasks, prev_node, cur_node, que):
#         # temp_solution 상태에서 wf룰 start_node에서 할당 시작하는 모든 경우를 que에 추가
#         # temp_solution을 일일이 복사하면 메모리 너무 먹을 거 같아서, 백트래킹 사용하고 큐에 넣을 때만 복사해서 넣음
#
#         if not temp_solution.map(prev_node, tasks[0], cur_node):
#             return False
#
#         if len(tasks) == 1:
#             if DEBUG_ALL_CASES:
#                 temp_solution.print_allocation()
#
#             que.append(temp_solution.clone())
#             temp_solution.unmap(tasks[0])
#             return True
#
#         for next_node in cur_node.neighbors:
#             if temp_solution.mappable(cur_node, tasks[1], next_node) and \
#                     self._alloc_wf_tasks(temp_solution, tasks[1:], cur_node, next_node, que):
#                 temp_solution.unmap(tasks[0])
#                 return True
#
#         if self.include_incomplete_cases:
#             que.append(temp_solution.clone())
#
#         temp_solution.unmap(tasks[0])
#         return False


class OptimalAllocator(Allocator):
    # completely searches the problem space in the given topology
    # returns the best solution among the all possible assignments
    def __init__(self, topology, evaluator):
        super().__init__(topology, evaluator)
        # 각각의 워크플로우에 대해,
        #   (아무것도 할당되지 않은) 초기 상태의 솔루션에서
        #   해당 워크플로우의 태스크를 전부 할당 가능한 경우들을 저장
        self.partial_solutions = {wf: [] for wf in self.topology.workflows}
        self.optimal_solution = None
        self.n_case = 0

    def allocate_workflows(self):
        self.temp_solution = Solution(self.topology, self.evaluator)

        for wf in self.topology.workflows:
            for start_node in self.topology.all_nodes:
                # 아래 호출에서 temp_solution 은 비어 있는 상태로 리턴함
                # 탐색 결과는 partial_sulitions[wf]에 저장됨(result 매개변수)
                self._alloc_wf_tasks(self.partial_solutions[wf],
                                     wf.tasks[:], None, start_node)

        self.temp_solution = Solution(self.topology, self.evaluator)
        self._merge_partial_solutions(self.topology.workflows[:])

        if DEBUG:
            print("[DBG] OptimalAllocator:")
            print()
            print(f"      found {self.n_case} cases")
            print()

        return self.optimal_solution

    def _alloc_wf_tasks(self, result, tasks, prev_node, cur_node):
        if not self.temp_solution.map(prev_node, tasks[0], cur_node):
            return False

        if len(tasks) == 1:
            result.append(self.temp_solution.clone())
            self.temp_solution.unmap(tasks[0])
            return True

        for next_node in cur_node.neighbors:
            if self.temp_solution.mappable(cur_node, tasks[1], next_node):
                self._alloc_wf_tasks(result, tasks[1:], cur_node, next_node)

        self.temp_solution.unmap(tasks[0])
        return False

    def _merge_partial_solutions(self, workflows):
        if not workflows:
            if not self.optimal_solution:
                self.optimal_solution = self.temp_solution.clone()
            self.optimal_solution = self.evaluator.get_best(
                [self.optimal_solution, self.temp_solution.clone()])
            self.n_case += 1
            return

        cur_wf = workflows[0]
        for partial_solution in self.partial_solutions[cur_wf]:
            if self._mergeable(cur_wf, partial_solution):
                self._merge(cur_wf, partial_solution)
                self._merge_partial_solutions(workflows[1:])
                self._unmerge(cur_wf, partial_solution)

    def _mergeable(self, wf, partial_solution):
        prev_node = None
        for task, target_node in zip(wf.tasks, partial_solution.wf_to_nodes[wf]):
            if not self.temp_solution.mappable(prev_node, task, target_node):
                return False
            prev_node = target_node

        return True

    def _merge(self, wf, partial_solution):
        prev_node = None
        for task, target_node in zip(wf.tasks, partial_solution.wf_to_nodes[wf]):
            self.temp_solution.map(prev_node, task, target_node)
            prev_node = target_node

    def _unmerge(self, wf, partial_solution):
        prev_node = None
        for task in wf.tasks:
            self.temp_solution.unmap(task)
