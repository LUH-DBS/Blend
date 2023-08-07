import numpy as np
import pandas as pd
from src.DBHandler import DBHandler
from src.Operators.OperatorBase import Operator
import time


class Plan(Operator):
    def __init__(self):
        self.input_data = None
        self.k = 10
        self.nodes = {} # Maps node names to their corresponding (operator, params)
        self.adj = {} # Maps node names to their corresponding input node names
        self.execution_plan = []
        self.DB = DBHandler()
        self.node_input_result = {}

    def readData(self, path):
        self.input_data = pd.read_csv(path)

    def add(self, name, operator, input_operator_names=[], params={}):
        self.nodes[name] = (operator, params)
        if name not in self.adj:
            self.adj[name] = []
        if len(input_operator_names) != 0:
            self.adj[name] += input_operator_names

    def delete_node(self, node_name):
        self.nodes.pop(node_name)
        previous_nodes = self.adj[node_name]
        next_nodes = []
        for k in self.adj:
            if node_name in self.adj[k]:
                next_nodes += [k]
        self.adj.pop(node_name)
        for n in next_nodes:
            self.adj[n] += previous_nodes
        for k in self.adj:
            if node_name in self.adj[k]:
                self.adj[k].remove(node_name)

    def update_node_sql_by_input_results(self, node_name):
        node_object = self.nodes[node_name][0]
        node_object.sql = node_object.sql.replace('$PREVIOUSSTEP_MUST$', self.create_sql_where_condition_from_numerical_value_list(self.node_input_result[node_name]))

    def optimize(self):
        # add terminal
        # nodes_without_target = set(self.nodes).difference(set([item for sublist in self.adj.values() for item in sublist if len(sublist) > 0]))
        # self.add('terminal', Terminal.Terminal(), nodes_without_target, {})

        nodes_to_optimize = []
        for node_name in self.nodes:
            if len(self.adj[node_name]) > 1:
                nodes_to_optimize += [node_name]

        for node_name in nodes_to_optimize:
            if self.nodes[node_name][0].type.startswith('set_'):
                optimized_name = self.optimize_nodes(self.nodes[node_name][0].type, self.adj[node_name])
                self.adj[node_name] = [optimized_name]
                self.delete_node(node_name)

                # dict_values = set([x[0] for x in self.adj.values() if len(x) > 0])
                dict_values = set([item for sublist in self.adj.values() for item in sublist if len(sublist) > 0])
                nodes_temp = self.nodes.copy()
                for node_name in self.nodes:
                    if node_name not in dict_values and self.nodes[node_name][0].type != 'terminal':
                        if node_name in self.nodes:
                            nodes_temp.pop(node_name)
                        if node_name in self.adj:
                            self.adj.pop(node_name)
                self.nodes = nodes_temp
        for element_name in self.nodes:
            if self.nodes[element_name][0].type in ['intersection', 'multicolumnintersection', 'quadrantapproximation'] and self.nodes[element_name][0].sql == '':
                self.nodes[element_name][0].create_sql_query()
        self.execution_plan = self.create_the_execution_plan()

    def optimize_nodes(self, destination_set_operator_type, input_operators):
        # the first loop is to run the linear nodes before optimizing for new ones
        for last_operator in input_operators:
            local_execution_plan = []
            pointer = self.adj[last_operator][0]
            while self.nodes[pointer][0].type != 'input': # we assume that it is linear (each node here has one input)
                local_execution_plan += [pointer]
                pointer = self.adj[pointer][0]
            local_execution_plan.reverse()
            local_execution_plan += [last_operator]
            for executable_node_name_index in np.arange(len(local_execution_plan)-1):
                result = self.independent_node_run(local_execution_plan[executable_node_name_index])
                self.delete_node(local_execution_plan[executable_node_name_index])
                self.node_input_result[local_execution_plan[executable_node_name_index + 1]] = result
                self.update_node_sql_by_input_results(local_execution_plan[executable_node_name_index + 1])
        optimized_node_name = input_operators[0]
        for input_index in np.arange(1, len(input_operators)):
            linear = self.nodes[optimized_node_name][0].optimize(self.nodes[input_operators[input_index]][0], destination_set_operator_type, True)
            if linear:
                self.adj[input_operators[input_index]] = self.adj[optimized_node_name]
                self.adj[optimized_node_name] = [input_operators[input_index]]
        return optimized_node_name

    def create_the_execution_plan(self):
        reversed_dictionary = {}
        for node_name in self.nodes:
            input_element_name_list = self.adj[node_name]
            if len(input_element_name_list) == 0:
                reversed_dictionary['starting_point'] = node_name
            else:
                reversed_dictionary[input_element_name_list[0]] = node_name
        plan = []
        plan += [reversed_dictionary['starting_point']]
        key = reversed_dictionary['starting_point']
        while key in reversed_dictionary:
            plan += [reversed_dictionary[key]]
            key = reversed_dictionary[key]
        return plan

    def run(self):
        optimization_time = time.time()
        self.optimize()
        optimization_time = time.time() - optimization_time

        execution_time = 0
        fetch_time = 0
        for element_name_index in np.arange(len(self.execution_plan)):
            element_name = self.execution_plan[element_name_index]
            element_object = self.nodes[element_name][0]
            if element_object.type in ['intersection', 'multicolumnintersection', 'quadrantapproximation']:
                if '$PREVIOUSSTEP_MUST$' in element_object.sql and len(self.node_input_result[element_name]) == 0:
                    continue
                next_element_name = self.execution_plan[element_name_index + 1]
                query = element_object.sql
                if element_name in self.node_input_result:
                    query = element_object.sql.replace('$PREVIOUSSTEP_MUST$', self.create_sql_where_condition_from_numerical_value_list(self.node_input_result[element_name]))
                execution_results, local_execution_time, local_fetch_time = self.DB.execute_and_fetchall(query)
                if hasattr(element_object, 'run'):
                    execution_results = element_object.run(execution_results, self.DB)
                self.node_input_result[next_element_name] = [x[0] for x in execution_results]
                execution_time += local_execution_time
                fetch_time += local_fetch_time
        if 'terminal' in self.node_input_result:
            return self.node_input_result['terminal'], optimization_time, execution_time, fetch_time
        else:
            return [], optimization_time, execution_time, fetch_time

    def independent_node_run(self, node_name):
        node = self.nodes[node_name][0]
        query = node.sql
        if node_name in self.node_input_result:
            query = query.replace('$PREVIOUSSTEP_MUST$',
                                  self.create_sql_where_condition_from_numerical_value_list(self.node_input_result[node_name]))
        execution_results, _, _ = self.DB.execute_and_fetchall(query)
        if hasattr(node, 'run'):
                    execution_results = node.run(execution_results, self.DB)
        return [x[0] for x in execution_results]
    
    def execute_seeker(self, seeker):
        pass


    def discover_terminal_set_op(self):
        return 'terminal'
