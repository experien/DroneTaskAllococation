from topology import *


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
        self.available_resources = {node: Resources(node.resources)
                                    for node in topology.all_nodes}

        # value, cost, fitness, or anything comparable scalar value.
        # NOTE: lazy evaluation. not up-to-date
        self.value = 0

        # if this variable is False, self.evaluate() will return previously calculated value
        self._require_evaluation = True

    def mappable(self, prev_node, task, target_node):
        first_task = not prev_node
        resource_ok = task.required_resources <= self.available_resources[target_node]
        visited = target_node in self.wf_to_nodes[task.workflow]
        connected = target_node in prev_node.neighbors if not first_task else True

        return first_task and resource_ok or \
                not first_task and not visited and connected and resource_ok

    def map(self, prev_node, task, target_node):
        # 'task' should be a not-assigned-task
        if task in self.task_to_node:
            return False

        if not self.mappable(prev_node, task, target_node):
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
        del self.wf_to_nodes[wf][target_node]
        self.wf_alloc[wf] = False
        del self.task_to_node[task]
        self.node_to_tasks[target_node].remove(task)
        self.available_resources[target_node] += task.required_resources
        self._require_evaluation = True
        return True

    @property
    def workflow_alloc_cnt(self):
        return sum(self.wf_alloc.values())

    def is_allocated(self, wf):
        return self.wf_alloc[wf]

    def assigned_nodes(self, workflow):
        return list(self.wf_to_nodes[workflow].keys())

    def evaluate(self):
        #if self.require_evaluation:
        if True:
            self.value = self.evaluator.evaluate(self)
            self._require_evaluation = False

        return (-self.workflow_alloc_cnt, self.value)

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

        return new_solution

    def __lt__(self, other):
        return self.evaluator.get_best([self, other]) == other

    def __gt__(self, other):
        return self.evaluator.get_best([self, other]) == self

    def __repr__(self):
        n_wf_alloc, metric = self.evaluate()
        return str((-n_wf_alloc, "%.2f" % metric))

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
