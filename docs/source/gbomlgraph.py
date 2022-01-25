from compiler import parse_file, semantic, check_program_linearity, matrix_generation_a_b, matrix_generation_c, \
    factorize_program, extend_factor
from compiler.classes import Parameter, Expression, Node, Hyperlink, Time, Program
from compiler.utils import error_, move_to_directory
from enum import Enum
import os
from solver_api import cplex_solver, gurobi_solver, clp_solver
from copy import deepcopy
import numpy as np


# TODO
# first check the whole thing
# Structure and problem print
# Solve the whole thing
# Hyperedge problem ?


def test_gboml_python_interface():
    timehorizon_considered = 10
    gboml_model = GbomlGraph(timehorizon_considered)
    if gboml_model.get_timehorizon() != timehorizon_considered:
        error_('Timehorizon SET : FAILED')
    print("Timehorizon SET : OK ")

    gboml_model.set_timehorizon(12)
    if gboml_model.get_timehorizon() != 12:
        error_('Timehorizon CHANGE : FAILED')
    print("Timehorizon CHANGE : OK ")

    node_pv = gboml_model.import_node("examples/microgrid/microgrid.txt", "SOLAR_PV", copy=True)
    if node_pv.get_name() != "SOLAR_PV" and type(node_pv) != Node:
        error_('Import Node without renaming : FAILED')
    print("Import Node without renaming : OK")

    node_b = gboml_model.import_node("examples/microgrid/microgrid.txt", "DEMAND", new_node_name="B", copy=True)
    if node_b.get_name() != "B" and type(node_b) != Node:
        error_('Import Node with renaming : FAILED')
    print("Import Node with renaming : OK")

    all_parameters_names = []
    all_parameters_values = []
    for i, parameter in enumerate(node_pv.get_parameters()):
        all_parameters_names.append(parameter.get_name())
        all_parameters_values.append(i)

    gboml_model.redefine_parameters_from_list(node_pv, all_parameters_names, all_parameters_values)
    for i, parameter in enumerate(node_pv.get_parameters_changes()):
        name = parameter.get_name()
        value = parameter.get_expression().get_name()

        if name != all_parameters_names[i] and value != all_parameters_values[i]:
            error_("Parameter change by list : FAILED")
    print("Parameter change by list : OK")
    node_pv_2 = gboml_model.import_node("examples/microgrid/microgrid.txt", "SOLAR_PV", copy=True)
    if len(node_pv_2.get_parameters_changes()) != 0:
        error_("Copying node : FAILED")
    print("Copying node : OK")

    gboml_model.remove_objective_in_node(node_pv_2, "hi")
    if len(node_pv_2.get_objectives()) != 0:
        error_("Removing objective : FAILED")
    print("Removing objective : OK")

    gboml_model.change_type_variable_in_node(node_pv_2, "investment", VariableType.EXTERNAL)
    if len(node_pv_2.get_variables_changes()) != 1:
        error_("Changing variables type : FAILED")

    var_name, var_type, line = node_pv_2.get_variables_changes()[0]
    if var_name != "investment" or var_type != VariableType.EXTERNAL.value:
        error_("Changing variables type : FAILED")
    print("Changing variables type : OK")
    nodes, edges = gboml_model.import_all_nodes_and_edges("examples/microgrid/microgrid.txt")

    gboml_model.add_nodes_in_model(*nodes)
    gboml_model.add_hyperedges_in_model(*edges)

    gboml_model.build_model()
    print(gboml_model.solve_cplex())
    exit()


class VariableType(Enum):
    EXTERNAL = "external"
    INTERNAL = "internal"


class GbomlGraph:
    """GbomlGraph makes it possible to define and solve a GBOML model.

    The GbomlGraph class enables the construction of GBOML models by importing nodes and hyperedges from a GBOML file.
    It also possesses a set of functions for updating the imported nodes and hyperedges (e.g., re-defining parameters
    or the type of variables). Nodes and hyperedges can be added to a GbomlGraph instance, from which the model can be
    solved and generated.

    Args:
        timehorizon (int) : length of optimization horizon considered

    :ivar list_nodes: nodes included in model
    :ivar list_hyperedges: hyperedges included in model
    :ivar timehorizon: optimization horizon object
    :ivar node_hyperedge_dict: dictionary of all nodes and hyperedges
    :ivar program: Program class of generated model (= None if model not generated)
    :ivar matrix_a: constraint matrix A in sparse COO format (= None if model not generated)
    :ivar matrix_b: upper bound on each row in constraint matrix (i.e., right-hand side coefficients, = None if model not generated)
    :ivar vector_c: vector of objective coefficients (= None if model not generated)
    :ivar indep_term_c: objective offset (i.e., constant term in the objective, = None if model not generated)

    """
    def __init__(self, timehorizon=1):
        """
        __init__ initializes GbomlGraph instance

        Args:
           timehorizon (int) : length of optimization horizon considered

        """
        self.list_nodes = []
        self.list_hyperedges = []
        self.timehorizon = Time("T", Expression('literal', timehorizon))
        self.node_hyperedge_dict = {}

        self.program = None
        self.matrix_a = None
        self.matrix_b = None
        self.vector_c = None
        self.indep_term_c = None

    def __add_node(self, to_add_node):
        """
        __add_node adds node to GbomlGraph instance

        Args:
           to_add_node (Node) : node that should be added

        :raises: re-use of identifier error

        """
        node_name = to_add_node.get_name()
        if node_name in self.node_hyperedge_dict:
            error_("Re-use of same identifier twice for nodes or hyperedges : " + str(node_name))
        self.node_hyperedge_dict[node_name] = to_add_node
        self.list_nodes.append(to_add_node)

    def __add_hyperedge(self, to_add_hyperedge):
        """
        __add_hyperedge adds hyperedge to GbomlGraph instance

        Args:
           to_add_hyperedge (Hyperlink) : hyperedge that should be added

        :raises: re-use of identifier error

        """

        hyperedge_name = to_add_hyperedge.get_name()
        if hyperedge_name in self.node_hyperedge_dict:
            error_("Reuse of same identifier twice for nodes or hyperedges : " + str(hyperedge_name))
        self.node_hyperedge_dict[hyperedge_name] = to_add_hyperedge
        self.list_hyperedges.append(to_add_hyperedge)

    def __get__(self, *node_or_hyperedge_name, error=False, wanted_type=None):
        """
        __get__ returns node(s) or hyperedge(s) identified by *node_or_hyperedge_name

        Args:
           *node_or_hyperedge_name (list <str>) : name of node(s) or hyperedge(s) to retrieve

           error (bool) : if identifier not found, an error is raised

           wanted_type (Node or Hyperlink) : returned type expected

        :raises: not found error

        """

        retrieved_object = None
        current_layer = self.node_hyperedge_dict
        depth_search = len(node_or_hyperedge_name)
        for i, name in enumerate(node_or_hyperedge_name):
            if name in current_layer:
                retrieved_object = current_layer[node_or_hyperedge_name]
                if i < depth_search-1 and isinstance(retrieved_object, Hyperlink):
                    error_("Hyperlinks do not possess subnodes or subhyperedges")
                elif i < depth_search-1:
                    current_layer = retrieved_object.get_internal_dict()

            elif error:
                error_("Unknown node or hyperedge named " + str(node_or_hyperedge_name))

        if wanted_type and not isinstance(retrieved_object, wanted_type):
            error_("Error wanted type " + str(wanted_type) + " but that name references a " +
                   str(type(retrieved_object)))

        return retrieved_object

    def add_nodes_in_model(self, *nodes):
        """
        add_nodes_in_model adds nodes to GbomlGraph instance

        Args:
            nodes (list <Nodes>) : list of node objects to be added

        """
        for node in nodes:
            self.__add_node(node)

    def add_hyperedges_in_model(self, *hyperedges):
        """
        add_hyperedges_in_model adds hyperedges to GbomlGraph instance

        Args:
            hyperedges (list <Hyperlink>) : list of hyperedge objects to be added

        """
        for hyperedge in hyperedges:
            self.__add_hyperedge(hyperedge)

    def set_timehorizon(self, value):
        """
        set_timehorizon sets time horizon to specified value

        Args:
           value (int) : length of time horizon considered

        """
        self.timehorizon = Time("T", Expression('literal', value))

    def get_timehorizon(self):
        """
        get_timehorizon returns time horizon value

        Returns:
           value (int) : length of time horizon considered

        """

        return self.timehorizon.get_value()

    def build_model(self, nb_processes: int = 1):
        """
        build_model generates optimization model in matrix form

        Args:
           nb_processes (int) : number of processes used for model generation

        """

        program = Program(self.list_nodes, timescale=self.timehorizon, links=self.list_hyperedges)
        program, program_variables_dict, definitions = semantic(program)
        check_program_linearity(program, program_variables_dict, definitions)
        factorize_program(program, program_variables_dict, definitions)
        if nb_processes > 1:
            extend_factor_on_multiple_processes(program, definitions, nb_processes)
        else:
            extend_factor(program, definitions)

        matrix_a, vector_b = matrix_generation_a_b(program)
        vector_c, indep_terms_c = matrix_generation_c(program)
        program.free_factors_objectives()

        self.program = program
        self.matrix_a = matrix_a
        self.matrix_b = vector_b
        self.vector_c = vector_c
        self.indep_term_c = indep_terms_c

    def __solve(self, solver_function):
        """
        __solve solves the optimization model

        Args:
           solver_function (function) : function calling solver

        Returns:
            solution (numpy.ndarray) -> flattened solution

            objective (float) -> objective value

            status -> solution status

            solver_info (dict) -> dictionary storing solver information

        """
        vector_c = np.asarray(self.vector_c.sum(axis=0), dtype=float)
        objective_offset = float(self.indep_term_c.sum())
        return solver_function(self.matrix_a, self.matrix_b, vector_c, objective_offset, self.program.get_tuple_name())

    def solve_cplex(self):
        """
        solve_cplex solves the flattened optimization model with CPLEX

        Returns:
            solution (numpy.ndarray) -> flattened solution

            objective (float) -> objective value

            status -> solution status

            solver_info (dict) -> dictionary storing solver information

        """

        return self.__solve(cplex_solver)

    def solve_gurobi(self):
        """
        solve_gurobi solves the flattened optimization problem with Gurobi

        Returns:
            solution (numpy.ndarray) -> flattened solution

            objective (float) -> objective value

            status -> solution status

            solver_info (dict) -> dictionary storing solver information

        """
        return self.__solve(gurobi_solver)

    def solve_clp(self):
        """
        solve_clp solves the flattened optimization problem with Clp/Cbc

        Returns:
            solution (numpy.ndarray) -> flattened solution

            objective (flat) -> float of the objective value

            status -> solution status

            solver_info -> dictionary of solver information

        """
        return self.__solve(clp_solver)

    @staticmethod
    def import_all_nodes_and_edges(filename):
        """
        import_all_nodes_and_edges is a static method that imports all nodes and hyperedges
        contained in a file

        Args:
           filename (str) : path to GBOML input file

        Returns:
            all_nodes (list) -> list of nodes contained in file

            all_hyperedges (list) -> list of hyperedges contained in file

        """
        old_dir, cut_filename = move_to_directory(filename)
        filename_graph = parse_file(cut_filename)
        all_nodes = filename_graph.get_nodes()
        to_return_nodes = []
        for node in all_nodes:
            to_return_nodes.append(deepcopy(node))

        all_hyperedges = filename_graph.get_links()
        to_return_edges = []
        for edge in all_hyperedges:
            to_return_edges.append(deepcopy(edge))
        os.chdir(old_dir)
        return to_return_nodes, to_return_edges

    @staticmethod
    def import_node(filename: str, *imported_node_identifier: str, new_node_name: str = "", copy=False):
        """
        import_node is a static method that imports a node from a GBOML input file

        Args:
           filename (str) : path to GBOML input file

           imported_node_identifier (list <str>) : identifier of imported node (specified layer by layer)

           new_node_name (str) : new identifier of node (for re-naming purposes, optional)

           copy (bool) : predicate of whether to copy the node or not

        Returns:
            imported_node (Node) : imported node

        """
        old_dir, cut_filename = move_to_directory(filename)
        filename_graph = parse_file(cut_filename)
        imported_node = filename_graph.get(imported_node_identifier)

        if imported_node is None:
            error_("ERROR: In file " + str(filename) + " there is no node named " + str(imported_node_identifier))

        if type(imported_node) != Node:
            error_("ERROR: A node named " + str(imported_node_identifier) + " is imported as type hyperedge ")

        if new_node_name == "":
            new_node_name = imported_node_identifier[-1]

        if copy:
            imported_node = deepcopy(imported_node)

        imported_node.rename(new_node_name)
        os.chdir(old_dir)
        return imported_node

    @staticmethod
    def import_hyperedge(filename: str, *imported_hyperedge_identifier: str,
                         new_hyperedge_name: str = "", copy=False):
        """
        import_hyperedge is a static method that imports a hyperedge from a GBOML input file

        Args:
           filename (str) : path to GBOML input file

           imported_hyperedge_identifier (list <str>) : identifier of imported hyperedge (specified layer by layer)

           new_hyperedge_name (str) : new hyperedge identifier (for re-naming purposes, optional)

           copy (bool) : predicate of whether to copy the hyperedge or not

        Returns:
            imported_hyperedge (Hyperlink) : imported hyperedge

        """
        old_dir, cut_filename = move_to_directory(filename)
        filename_graph = parse_file(filename)
        imported_hyperedge = filename_graph.get(imported_hyperedge_identifier)

        if imported_hyperedge is None:
            error_("ERROR: In file " + str(filename) + " there is no node named " + str(imported_hyperedge_identifier))

        if type(imported_hyperedge) == Hyperlink:
            error_("ERROR: A hyperedge named " + imported_node_identifier + " is imported as type node ")

        if new_hyperedge_name == "":
            new_hyperedge_name = imported_hyperedge_identifier[-1]

        if copy:
            imported_hyperedge = deepcopy(imported_hyperedge)

        imported_hyperedge.rename(new_hyperedge_name)
        os.chdir(old_dir)
        return imported_hyperedge

    @staticmethod
    def rename(node_or_hyperedge, new_name):
        """
        rename is a static method that renames a node or hyperedge

        Args:
           node_or_hyperedge (Node/Hyperlink) : node or nyperedge to be re-named

           new_name (str) : new name

        """
        node_or_hyperedge.rename(new_name)

    @staticmethod
    def get_inside_node(in_node, *searched_node: str, wanted_type=None):
        """
        get_inside_node is a static method that returns a sub-node or sub-hyperedge of a given node

        Args:
           in_node (Node) : node to which the sub-node is expected to belong

           searched_node (list <str>) : The name of the sub-node searched (layer by layer)

           wanted_type (Class Type) : Either Node or Hyperlink depending on the type of the object considered

        Returns:
            retrieved_object (Node/Hyperlink) : The node/hyperedge searched

        """
        current_layer = in_node.get_internal_dict()
        depth_search = len(searched_node)
        retrieved_object = None
        for i, name in enumerate(searched_node):
            if name in current_layer:
                retrieved_object = current_layer[name]
                if i < depth_search - 1 and isinstance(retrieved_object, Hyperlink):
                    error_("Hyperlink objects do not possess subnodes or subhyperedges")
                elif i < depth_search - 1:
                    current_layer = retrieved_object.get_internal_dict()

            elif error:
                error_("Unknown node or hyperedge named " + str(node_or_hyperedge_name))

        if wanted_type and not isinstance(retrieved_object, wanted_type):
            error_("Error wanted type " + str(wanted_type) + " but that name references a " +
                   str(type(retrieved_object)))

        return retrieved_object

    @staticmethod
    def add_sub_node(node_to_add, in_node):
        """
        add_sub_node is a static method that adds a sub-node to a node

        Args:
           node_to_add (Node) : sub-node to add

           in_node (Node) : node to which sub-node should be added

        """
        in_node.add_sub_node(node_to_add)
        in_node.update_internal_dict()

    @staticmethod
    def add_sub_hyperedge(hyperedge_to_add, in_node):
        """
        add_sub_hyperedge is a static method that adds a sub-hyperedge to a node

        Args:
           hyperedge_to_add (Hyperlink) : sub-hyperedge to add

           in_node (Node) : node to which sub-hyperedge should be added

        """
        in_node.add_link(hyperedge_to_add)
        in_node.update_internal_dict()

    @staticmethod
    def redefine_parameter_from_value(node_or_hyperedge, parameter_name: str, value: float):
        """
        redefine_parameter_with_value is a static method that redefines a parameter with a scalar value

        Args:
           node_or_hyperedge (Node/Hyperlink) : Node/Hyperedge where the parameter will be redefined

           parameter_name (str) : parameter name

           value (float) : new value of parameter

        """
        expr = Expression('literal', value)
        parameter = Parameter(parameter_name, expr)
        node_or_hyperedge.add_parameter_change(parameter)

    @staticmethod
    def redefine_parameter_from_values(node_or_hyperedge, parameter_name: str, values: list):
        """
        redefine_parameter_from_value is a static method that re-defines a vector parameter from a list of values

        Args:
           node_or_hyperedge (Node/Hyperlink) : Node/Hyperedge where the parameter will be redefined

           parameter_name (str) : Name of the parameter considered

           values (list<float>) : list of values for redefinition

        """

        expression_values = []
        for value in values:
            expr = Expression('literal', value)
            expression_values.append(expr)
        parameter = Parameter(parameter_name, None)
        parameter.set_vector(expression_values)
        node_or_hyperedge.add_parameter_change(parameter)

    @staticmethod
    def redefine_parameter_from_file(node_or_hyperedge, parameter_name: str, filename):
        """
        redefine_parameter_from_file is a static method that redefines parameter values from a CSV file

        Args:
           node_or_hyperedge (Node/Hyperlink) : Node/Hyperedge in which the parameter should be re-defined

           parameter_name (str) : parameter name

           filename (str) : name of CSV file

        """

        parameter = Parameter(parameter_name, filename)
        node_or_hyperedge.add_parameter_change(parameter)

    @staticmethod
    def redefine_parameters_from_list(node_or_hyperedge, list_parameters: list = [], list_values: list = []):
        """
        redefine_parameters_from_list is a static method that re-defines the values of scalar parameters from a list.
        This functions generates tuples of re-defined parameters : [(list_parameters[i], list_values[i]) for every i in len(list_parameters)

        Args:
           node_or_hyperedge (Node/Hyperlink) : Node/Hyperedge in which parameters should be re-defined

           list_parameters (list <str>) : list of parameter names

           list_values (list <float/list<float>/str>) : list of parameter values

        """
        assert len(list_parameters) == len(list_values), "Unmatching size between list or parameters and list of values"
        for i in range(len(list_parameters)):
            parameter_name = list_parameters[i]
            value = list_values[i]
            if isinstance(value, str):
                GbomlGraph.redefine_parameter_from_file(node_or_hyperedge, parameter_name, value)
            elif isinstance(value, float) or isinstance(value, int):
                GbomlGraph.redefine_parameter_from_value(node_or_hyperedge, parameter_name, value)
            elif isinstance(value, list):
                GbomlGraph.redefine_parameter_from_values(node_or_hyperedge, parameter_name, value)
            else:
                error_("Unaccepted type value for parameter redefiniton "+str(type(value)))

    @staticmethod
    def redefine_parameters_from_keywords(node_or_hyperedge, **kwargs):
        """
        redefine_parameters is a static method that re-defines parameter values from keyword arguments.

        Args:
           node_or_hyperedge (Node/Hyperlink) : Node/Hyperedge in which parameters should be re-defined

           kwargs (tuple <str, value>): tuple of parameters name, value
        """
        for parameter_name, value in kwargs.items():
            if isinstance(value, str):
                GbomlGraph.redefine_parameter_from_file(node_or_hyperedge, parameter_name, value)
            elif isinstance(value, float) or isinstance(value, int):
                GbomlGraph.redefine_parameter_from_value(node_or_hyperedge, parameter_name, value)
            elif isinstance(value, list):
                GbomlGraph.redefine_parameter_from_values(node_or_hyperedge, parameter_name, value)
            else:
                error_("Unaccepted type value for parameter redefiniton " + str(type(value)))

    @staticmethod
    def change_type_variable_in_node(node, variable_name: str, variable_type):
        """
        change_type_variable_in_node is a static method that changes the type of a variable

        Args:
           node (Node) : node to which variable that should be modified belongs

           variable_name (str) : variable name

           variable_name (VariableType) : new variable type (either External or Internal)
        """
        variable_tuple = [variable_name, variable_type.value, 0]
        node.add_variable_change(variable_tuple)

    @staticmethod
    def remove_constraint(node_or_hyperedge, *to_delete_constraints_names):
        """
        remove_constraint is a static method that removes named constraints from a node/hyperedge

        Args:
           node_or_hyperedge (Node/Hyperlink) : Node/Hyperlink from which constraints should be removed

           to_delete_constraints_names (list <str>) : names of constraints to remove
        """
        constraints = node_or_hyperedge.get_constraints()
        to_delete_constraints_names = list(to_delete_constraints_names)
        for constraint in constraints:
            constraint_name = constraint.get_name()
            if constraint_name in to_delete_constraints_names:
                node_or_hyperedge.remove_constraint(constraint)
                to_delete_constraints_names.remove(constraint_name)

        if to_delete_constraints_names:
            error_("Could not delete "+str(to_delete_constraints_names)+" as they were not found in "
                   + str(node_or_hyperedge.get_name()))

    @staticmethod
    def remove_objective_in_node(node, *to_delete_objectives_names):
        """
        remove_objective_in_node is a static method that removes named objectives from a node

        Args:
           node_or_hyperedge (Node/Hyperlink) : node from which objectives should be removed

           to_delete_objectives_names (list <str>) : names of objectives to remove
        """
        objectives = node.get_objectives()
        to_delete_objectives_names = list(to_delete_objectives_names)
        for objective in objectives:
            objective_name = objective.get_name()
            if objective_name in to_delete_objectives_names:
                node.remove_objective(objective)
                to_delete_objectives_names.remove(objective_name)

        if to_delete_objectives_names:
            error_("Could not delete " + str(to_delete_objectives_names) + " as they were not found in hyperedge "
                   + str(node.get_name()))

    @staticmethod
    def change_node_name_in_hyperedge(hyperedge, old_node_name, new_node_name):
        """
        change_node_name_in_hyperedge is a static method that changes name of node in hyperedge

        Args:
           hyperedge (Hyperlink) : Hyperlink in which node names should be changed

           old_node_name (str) : previous node name

           new_node_name (str) : new node name
        """
        change_tuple = [old_node_name, new_node_name, None]
        hyperedge.add_name_change(change_tuple)
