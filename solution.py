from topology import *


class Solution:
    # mapping information for all the workflows, tasks <--> nodes
    # I used both terms, 'assign' and 'map' to represent task-to-node assignment
    #
    # Assumption: it n tasks exist in a workflow, these tasks should be allocated to n nodes
    #             i.e. multiple tasks can be assigned to a single node, however,
    #             2 tasks cannot be assigned to a node if they belong to a workflow together

    id_base = 0
    topology = None
    evaluator = None

    def __init__(self, topology=None, evaluator=None, base_solution=None):
        Solution.id_base += 1
        self.id = Solution.id_base

        if not base_solution:
            # remember previous arguments for parameters 'topology' and 'evaluator'
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
            self.wf_alloc = {wf: False for wf in topology.workflows}
            self.wf_to_node = {wf: {} for wf in topology.workflows}
            self.task_to_node = {}  # n to 1
            self.node_to_task = {node: {} for node in topology.all_nodes} # 1 to n
            self.available_resources = {node: Resources(node.resources)
                                        for node in topology.all_nodes}

            # value, cost, fitness, or anything comparable scalar value.
            # NOTE: lazy evaluation. not up-to-date
            self.value = 0

            # if this variable is False, self.evaluate() will return previously calculated value
            self.require_evaluation = True

        else:
            pass

    def mappable(self, prev_node, task, target_node):
        first_task = not prev_node
        resource_ok = task.required_resources <= self.available_resources[target_node]
        visited = target_node in self.wf_to_node[task.workflow]

        return first_task and resource_ok or \
                not first_task and not visited and resource_ok

    def map(self, prev_node, task, target_node):
        # 'task' should be a not-assigned-task
        if task in self.task_to_node:
            return False

        if not self.mappable(prev_node, task, target_node):
            return False

        wf = task.workflow
        self.wf_to_node[wf][target_node] = True
        if len(self.wf_to_node[wf]) == wf.n_task:
            self.wf_alloc[wf] = True

        self.task_to_node[task] = target_node
        self.node_to_task[target_node][task] = True
        self.available_resources[target_node] -= task.required_resources
        self.require_evaluation = True
        return True

    def unmap(self, task):
        # 'task' should be an assigned-task
        if task not in self.task_to_node:
            return False

        target_node = self.task_to_node[task]
        wf = task.workflow
        del self.wf_to_node[wf][target_node]
        self.wf_alloc[wf] = False
        del self.task_to_node[task]
        del self.node_to_task[target_node][task]
        self.available_resources[target_node] -= task.required_resources
        self.require_evaluation = True
        return True

    @property
    def workflow_alloc_cnt(self):
        return sum(self.wf_alloc.values())

    def assigned_nodes(self, workflow):
        return list(self.wf_to_node[workflow].keys())

    def evaluate(self):
        if self.require_evaluation:
            self.value = self.evaluator.evaluate(self)

        return self.value

    def __repr__(self):
        return str(self.evaluate())

    def print_allocation(self):
        print(f"[DBG] Solution#{self.id}: {self.workflow_alloc_cnt} of {NumOfWorkflows} workflows are fully allocated")
        print("      WorkFlow#id(# of tasks) : [target node1, target node2, ...]")
        print()
        for wf in self.topology.workflows:
            target_drones = list(self.wf_to_node[wf].keys())
            print(f"      {wf}({wf.n_task} tasks) : {target_drones}")
        print()


# an alias of 'Solution'
class Chromosome(Solution):
    pass
