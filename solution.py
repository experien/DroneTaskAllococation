from topology import *
from collections import deque


class Solution:
    # mapping information for all the workflows, tasks <--> nodes
    # I used both terms, 'assign' and 'map' to represent task-to-node assignment
    #
    # Assumption: if n tasks exist in a workflow, these tasks should be allocated to n nodes
    #             i.e. multiple tasks can be assigned to a single node, however,
    #             2 tasks cannot be assigned to a node if they belong to a workflow together

    id_base = 0
    topology = None
    evaluator = None

    def __init__(self, topology=None, evaluator=None):
        Solution.id_base += 1
        self.id = Solution.id_base

        # remember previous arguments for parameters 'topology' and 'evaluator'
        # Sorry. this code doesn't work now
        if topology:
            Solution.topology = self.topology = topology
        else:
            self.topology = Solution.topology

        if evaluator:
            Solution.evaluator = self.evaluator = evaluator
        else:
            self.evaluator = Solution.evaluator

        # CAUTION: these data structures should be synchronized
        #          they are different views of a single logical state
        #          if you change them, apply the changes to clone() method.
        self.wf_alloc = {wf: False for wf in topology.workflows}
        self.wf_to_nodes = {wf: {} for wf in topology.workflows}  # ordered
        self.task_to_node = {}  # n to 1
        self.node_to_tasks = {node: set() for node in topology.all_nodes} # 1 to n
        self.routing_paths = {}
        self.available_resources = {node: Resources(node.resources)
                                    for node in topology.all_nodes}

        # value, cost, fitness, or anything comparable scalar value.
        # NOTE: lazy evaluation. not up-to-date
        self.value = 0

        # if this variable is False, self.evaluate() will return previously calculated value
        self._require_evaluation = True

    def mappable(self, prev_node, task, target_node, multihop=False):
        first_task = not prev_node
        resource_ok = task.required_resources <= self.available_resources[target_node]
        visited = target_node in self.wf_to_nodes[task.workflow]
        if not multihop:
            connected = target_node in prev_node.neighbors if not first_task else True
        else:
            connected = self._is_connected(prev_node, target_node) if not first_task else True

        return first_task and resource_ok or \
                not first_task and not visited and connected and resource_ok

    def _is_connected(self, src_node, dst_node):
        visited = {src_node}
        que = deque([src_node])
        while que:
            cur = que.popleft()
            for neighbor in cur.neighbors:
                if neighbor == dst_node:
                    return True
                if neighbor not in visited:
                    visited.add(neighbor)
                    que.append(neighbor)

        return False

    def map(self, prev_node, task, target_node, multihop=False):
        # 'task' should be a not-assigned-task
        if task in self.task_to_node:
            return False

        if not self.mappable(prev_node, task, target_node, multihop):
            return False

        if multihop and prev_node is not None:
            path = self._route(prev_node, target_node)
            if path:
                self.routing_paths[(prev_node, target_node)] = path
            else:
                return False

        wf = task.workflow
        self.wf_to_nodes[wf][target_node] = True
        if len(self.wf_to_nodes[wf]) == wf.n_task:
            self.wf_alloc[wf] = True

        self.task_to_node[task] = target_node
        self.node_to_tasks[target_node].add(task)
        self.available_resources[target_node] -= task.required_resources
        self._require_evaluation = True
        return True

    def unmap(self, task):
        # 'task' should be an assigned-task
        if task not in self.task_to_node:
            return False

        target_node = self.task_to_node[task]
        wf = task.workflow

        # unmap routing path
        mapped_nodes = list(self.wf_to_nodes[wf].keys())
        if mapped_nodes[0] == target_node:
            prev_node = None
        else:
            target_idx = mapped_nodes.index(target_node)
            prev_node = mapped_nodes[target_idx - 1]

        if prev_node and (prev_node, target_node) in self.routing_paths:
            del self.routing_paths[(prev_node, target_node)]

        del self.wf_to_nodes[wf][target_node]
        self.wf_alloc[wf] = False
        del self.task_to_node[task]
        self.node_to_tasks[target_node].remove(task)
        self.available_resources[target_node] += task.required_resources
        self._require_evaluation = True
        return True

    def _route(self, src_node, dst_node):
        # min-hop routing
        paths =deque([[src_node]])
        while paths:
            p = paths.popleft()
            if p[-1] == dst_node:
                return p
            for neighbor in p[-1].neighbors:
                if neighbor not in p:
                    paths.append(p[:] + [neighbor])

        return None

    @property
    def workflow_alloc_cnt(self):
        return sum(self.wf_alloc.values())

    def is_allocated(self, wf):
        return self.wf_alloc[wf]

    def assigned_nodes(self, workflow):
        return list(self.wf_to_nodes[workflow].keys())

    def evaluate(self):
        self.value = self.evaluator.evaluate(self)
        self._require_evaluation = False

        return self.value

    def clone(self):
        new_solution = Solution(self.topology, self.evaluator)
        new_solution.wf_alloc = dict(self.wf_alloc)
        new_solution.wf_to_nodes = {wf: dict(self.wf_to_nodes[wf])
                                    for wf in self.wf_to_nodes}
        new_solution.task_to_node = dict(self.task_to_node)
        new_solution.node_to_tasks = {node: set(self.node_to_tasks[node])
                                      for node in self.node_to_tasks}
        new_solution.available_resources = {node: Resources(self.available_resources[node])
                                            for node in self.available_resources}
        new_solution.value = self.value
        new_solution._require_evaluation = self._require_evaluation
        new_solution.routing_paths = {key:value[:] for key, value in self.routing_paths.items()}

        return new_solution

    def __lt__(self, other):
        return self.evaluator.get_best([self, other]) == other

    def __gt__(self, other):
        return self.evaluator.get_best([self, other]) == self

    def __repr__(self):
        answer = self.evaluate()
        if answer:
            return str(answer)
        else:
            return ""

    def print_allocation(self):
        print(f"[DBG] Solution#{self.id}:", end=' ')
        print(f"allocated {self.workflow_alloc_cnt} of {global_params.NumOfWorkflows} workflows.")
        print()
        for wf in self.topology.workflows:
            print(f"      {wf}({wf.n_task} tasks) : ",
                  list(self.wf_to_nodes[wf].keys()))
        print()


# an alias of 'Solution'
class Chromosome(Solution):
    pass
