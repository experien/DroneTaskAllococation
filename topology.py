from abc import ABCMeta
from random import randint, randrange
from itertools import product, chain

from parameters import *


# in this file, all the classes contain STATIC information

class StaticTopology:
    # a topology contains node deploy, node connection, workflow and tasks
    # and not contains dynamic info. i.e. assignments from a task to a node

    def __init__(self):
        # generate & deploy nodes
        self.drones = self._deploy(Drone, global_params.NumOfDrones, global_params.DroneXRange)
        self.edge_servers = self._deploy(EdgeServer, global_params.NumOfEdgeServer, global_params.EdgeServerXRange)
        self.cloud_servers = self._deploy(CloudServer, global_params.NumOfCloudServer, global_params.CloudServerXRange)
        self.all_nodes = self.drones + self.edge_servers + self.cloud_servers
        self.n_all_node = len(self.all_nodes)

        # investigate distance between all pairs of nodes
        self.distance = {}
        for node1, node2 in product(self.all_nodes, self.all_nodes):
            dist_x = node1.pos_x - node2.pos_x
            dist_y = node1.pos_y - node2.pos_y
            d = pow(dist_x ** 2 + dist_y ** 2, 0.5)
            self.distance[(node1, node2)] = self.distance[(node2, node1)] = d

        # build connection info.
        # self.links = self._connect(self.drones, self.drones, dist_constrained=True)
        # self.links |= self._connect(self.drones, self.edge_servers)
        # self.links |= self._connect(self.edge_servers, self.cloud_servers)

        # build connection info.
        # investigate 'neighbors' of each node
        self._connect(self.drones, self.drones, dist_constrained=True)
        self._connect(self.drones, self.edge_servers)
        self._connect(self.edge_servers, self.cloud_servers)

        # generate workflows & tasks
        self.workflows = [WorkFlow() for _ in range(global_params.NumOfWorkflows)]
        self.all_tasks = list(chain(*[wf.tasks for wf in self.workflows]))
        self.n_all_task = len(self.all_tasks)

        if DEBUG:
            self._print_nodes()
            self._print_workflow_n_tasks()

    @staticmethod
    def _deploy(constructor, n, x_range):
        nodes = []
        for _ in range(n):
            x = randrange(*x_range)
            y = randrange(*global_params.AreaYRange)
            nodes.append(constructor(x, y))

        return nodes

    def get_distance(self, node1, node2):
        return self.distance[(node1, node2)]

    def _connect(self, nodes1, nodes2, dist_constrained=False):

        #links = {}
        for node1, node2 in product(nodes1, nodes2):
            if node1 == node2:
                continue

            d = self.distance[(node1, node2)]
            if not dist_constrained or \
                    d <= node1.trans_range and \
                    d <= node2.trans_range:
                #links[(node1, node2)] = links[(node2, node1)] = True
                node1.neighbors.append(node2)
                node2.neighbors.append(node1)

        #return links

    def _print_nodes(self):
        print(f"[DBG] {self.n_all_node} nodes generated")
        print("      Node#id [processing power, bandwidth, delay factor]")
        print()
        for node in self.all_nodes:
            print(node.info())
        print()
        input("Press <ENTER> to continue...... >>>")
        print()

    def _print_workflow_n_tasks(self):
        print(f"[DBG] {global_params.NumOfWorkflows} workflows generated")
        print("      WorkFlow#id [Task#id [processing power req., bandwidth req.], ...]")
        print()
        for wf in self.workflows:
            print('      ' + wf.info())
        print()
        input("Press <ENTER> to continue...... >>>")
        print()


class Resources(dict):
    # a Resource instance is an addable, substractable, comparable dictionary
    # for example,
    #   {'processing_power':100, 'bandwidth': 200} - {'processing_power':50, 'bandwidth': 100}
    #   => {'processing_power':50, 'bandwidth': 100}
    #
    # assume that Resources instances contain identical resource names(keys)

    def __le__(self, other):
        return all([self[key] <= other[key] for key in self])

    def __add__(self, other):
        return Resources({key: self[key] + other[key] for key in self})

    def __sub__(self, other):
        return Resources({key: self[key] - other[key] for key in self})

    def __repr__(self):
        # return str(dict(self))
        return str(list(self.values()))


class Node(metaclass=ABCMeta):
    id_base = 0
    resources = Resources()
    delay_factor = 0

    def __init__(self, pos_x=0, pos_y=0):
        Node.id_base += 1
        self.id = Node.id_base
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.neighbors = []

    def __repr__(self):
        return f'Node#{self.id}'

    def info(self):
        stat = list(self.resources.values()) + [self.delay_factor]
        return self.__repr__() + ' ' + str(stat)


class Drone(Node):
    trans_range = global_params.DroneTransRange
    resources = Resources(
        processing_power=global_params.MaxProcessingRateOfDrone,
        bandwidth=global_params.BandwidthOfDrone
    )
    delay_factor=global_params.MaxDelayFactorOfDrone

    def __repr__(self):
        return f'Drone#{self.id}'


class EdgeServer(Node):
    trans_range = global_params.EdgeServerTransRange
    resources = Resources(
        processing_power=global_params.MaxProcessingRateOfEdgeServer,
        bandwidth=global_params.BandwidthOfEdgeServer
    )
    delay_factor = global_params.MaxDelayFactorOfEdgeServer

    def __repr__(self):
        return f'Edge#{self.id}'


class CloudServer(Node):
    trans_range = global_params.CloudServerTransRange
    resources = Resources(
        processing_power=global_params.MaxProcessingRateOfCloudServer,
        bandwidth=global_params.BandwidthOfCloudServer
    )
    delay_factor = global_params.MaxDelayFactorOfCloudServer

    def __repr__(self):
        return f'Cloud#{self.id}'


class WorkFlow:
    id_base = 0

    def __init__(self):
        WorkFlow.id_base += 1
        self.id = WorkFlow.id_base

        self.n_task = randint(global_params.MinTasksPerWorkFlow, global_params.MaxTasksPerWorkflow)
        self.tasks = []
        for _ in range(self.n_task):
            res = Resources(
                processing_power=randint(global_params.MinRequiredProcessingPower, global_params.MaxRequiredProcessingPower),
                bandwidth=randint(global_params.MinRequiredBandwidth, global_params.MaxRequiredBandwidth)
            )
            self.tasks.append(Task(self, res))

    def __repr__(self):
        return f'WorkFlow#{self.id}'

    # __repr__ + details
    def info(self):
        s = f'WorkFlow#{self.id} [' + self.tasks[0].info()
        for task in self.tasks[1:]:
            s += ', ' + task.info()
        return s + ']'


class Task:
    id_base = 0

    def __init__(self, workflow, required_resources):
        Task.id_base += 1
        self.id = Task.id_base
        self.workflow = workflow    # 'self' belongs to 'workflow'
        self.required_resources = required_resources

    def __repr__(self):
        return f'Task#{self.id}'

    def info(self):
        return f'Task#{self.id} {self.required_resources}'
