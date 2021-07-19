import matplotlib.pyplot as plt
from random import random

from parameters import *


class Visualizer:
    topology = None
    solution = None

    @classmethod
    def draw(cls, title, topology, solution=None):
        cls.topology = topology
        cls.solution = solution

        plt.title(title)
        cls._draw_topology()
        if solution:
            cls._draw_solution()
        plt.show()

    @staticmethod
    def _draw_nodes(nodes, color, size):
        x_list = [node.pos_x for node in nodes]
        y_list = [node.pos_y for node in nodes]
        plt.scatter(x_list, y_list, edgecolors=color, s=size)

    @staticmethod
    def _draw_connection(node1, node2, color):
        plt.plot([node1.pos_x, node2.pos_x],
                 [node1.pos_y, node2.pos_y],
                 color=color)

    @classmethod
    def _draw_topology(cls):
        # nodes
        cls._draw_nodes(cls.topology.drones, 'blue', 30)
        cls._draw_nodes(cls.topology.edge_servers, 'black', 80)
        cls._draw_nodes(cls.topology.cloud_servers, 'red', 150)

        # area
        y = global_params.AreaYRange.stop
        plt.fill_between([*global_params.DroneXRange],[y, y], alpha=0.1)
        plt.fill_between([*global_params.EdgeServerXRange],[y, y], alpha=0.2)
        plt.fill_between([*global_params.CloudServerXRange],[y, y], alpha=0.1)

        # drone-to-drone connections
        for drone1 in cls.topology.drones:
            for drone2 in cls.topology.drones:
                if drone2 in drone1.neighbors:
                    cls._draw_connection(drone1, drone2, 'green')

        # edge-to-cloud connections
        for edge_server in cls.topology.edge_servers:
            for cloud_server in cls.topology.cloud_servers:
                cls._draw_connection(edge_server, cloud_server, 'black')

    @classmethod
    def _draw_solution(cls):
        for wf in cls.topology.workflows:
            target_nodes = cls.solution.assigned_nodes(wf)
            for node1, node2 in zip(target_nodes, target_nodes[1:]):
                color = (random(), random(), random())  # r, g, b
                cls._draw_connection(node1, node2, color)
