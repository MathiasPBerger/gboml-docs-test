
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
        bound method initializing a GbomlGraph instance

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
        bound method adding a node to a GbomlGraph instance

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
        bound method adding a hyperedge to a GbomlGraph instance

        Args:
           to_add_hyperedge (Hyperedge) : hyperedge that should be added

        :raises: re-use of identifier error

        """

        hyperedge_name = to_add_hyperedge.get_name()
        if hyperedge_name in self.node_hyperedge_dict:
            error_("Reuse of same identifier twice for nodes or hyperedges : " + str(hyperedge_name))
        self.node_hyperedge_dict[hyperedge_name] = to_add_hyperedge
        self.list_hyperedges.append(to_add_hyperedge)

    def __get__(self, *node_or_hyperedge_name, wanted_type=None):
        """
        bound method returning a node or a hyperedge identified by its name and those of its ancestors

        Args:
           *node_or_hyperedge_name (list <str>) : list of ancestor node names and node or hyperedge name (used for depth-first traversal)
           wanted_type (Node or Hyperedge) : returned type (either Node or Hyperedge)

        :raises: not found error

        """

        retrieved_object = None
        current_layer = self.node_hyperedge_dict
        depth_search = len(node_or_hyperedge_name)
        for i, name in enumerate(node_or_hyperedge_name):
            if name in current_layer:
                retrieved_object = current_layer[node_or_hyperedge_name]
                if i < depth_search-1 and isinstance(retrieved_object, Hyperedge):
                    error_("Hyperedges do not possess subnodes or subhyperedges")
                elif i < depth_search-1:
                    current_layer = retrieved_object.get_internal_dict()

            else:
                error_("Unknown node or hyperedge named " + str(node_or_hyperedge_name))

        if wanted_type and not isinstance(retrieved_object, wanted_type):
            error_("Error wanted type " + str(wanted_type) + " but that name references a " +
                   str(type(retrieved_object)))

        return retrieved_object

    def add_nodes_in_model(self, *nodes):
        """
        bound method adding nodes to a GbomlGraph instance

        Args:
            nodes (list <Nodes>) : list of node objects to be added

        """
        for node in nodes:
            self.__add_node(node)

    def add_hyperedges_in_model(self, *hyperedges):
        """
        bound method adding hyperedges to a GbomlGraph instance

        Args:
            hyperedges (list <Hyperedge>) : list of hyperedge objects to be added

        """
        for hyperedge in hyperedges:
            self.__add_hyperedge(hyperedge)

    def set_timehorizon(self, value):
        """
        bound method setting the time horizon to a specified value

        Args:
           value (int) : length of time horizon considered

        """
        self.timehorizon = Time("T", Expression('literal', value))

    def get_timehorizon(self):
        """
        bound method returning the value of the time horizon

        Returns:
           value (int) : length of time horizon considered

        """

        return self.timehorizon.get_value()

    def build_model(self, nb_processes: int = 1):
        """
        bound method generating the matrices of the optimization model

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
        bound method solving the optimization model

        Args:
           solver_function (function) : function calling a solver

        Returns:
            solution (numpy.ndarray) : flattened solution
            objective (float) : objective value
            status (str) : solver exit status
            solver_info (dict) : dictionary storing solver information

        """
        vector_c = np.asarray(self.vector_c.sum(axis=0), dtype=float)
        objective_offset = float(self.indep_term_c.sum())
        return solver_function(self.matrix_a, self.matrix_b, vector_c, objective_offset, self.program.get_tuple_name())

    def solve_gurobi(self):
        """
        bound method solving the flattened optimization model with Gurobi

        Returns:
            solution (numpy.ndarray) : flattened solution
            objective (float) : objective value
            status (str) : solver exit status
            solver_info (dict) : dictionary storing solver information

        """
        return self.__solve(gurobi_solver)

    def solve_cplex(self):
        """
        bound method solving the flattened optimization model with CPLEX

        Returns:
            solution (numpy.ndarray) : flattened solution
            objective (float) : objective value
            status (str) : solver exit status
            solver_info (dict) : dictionary storing solver information

        """

        return self.__solve(cplex_solver)

    def solve_xpress(self):
        """
        bound method solving the flattened optimization model with Xpress

        Returns:
            solution (numpy.ndarray) : flattened solution
            objective (float) : objective value
            status (str) : solver exit status
            solver_info (dict) : dictionary storing solver information

        """
        return self.__solve(xpress_solver)

    def solve_clp(self):
        """
        bound method solving the flattened optimization problem with Clp/Cbc

        Returns:
            solution (numpy.ndarray) : flattened solution
            objective (flat) : float of the objective value
            status (str) : solver exit status
            solver_info (dict) : dictionary storing solver information

        """
        return self.__solve(clp_solver)

    def solve_dsp(self, algorithm="dw"):
        """
        bound method solving the optimization model with DSP

        Args:
            algorithm (str): algorithm selected ("dw" for Dantzig-Wolfe and "de" for extensive form solve)

        Returns:
            solution (numpy.ndarray) : flattened solution

            objective (float ) : objective value
            
            status (str) : solver exit status
            
            solver_info (dict) : dictionary of solver information

        """
        vector_c = np.asarray(self.vector_c.sum(axis=0), dtype=float)
        objective_offset = float(self.indep_term_c.sum())
        return dsp_solver(self.matrix_a, self.matrix_b, vector_c, objective_offset, self.program.get_tuple_name(),
                          program.get_first_level_constraints_decomposition(), algorithm=algorithm)

    @staticmethod
    def import_all_nodes_and_edges(filename):
        """
        static method importing all nodes and hyperedges contained in a file

        Args:
           filename (str) : path to GBOML input file

        Returns:
            all_nodes (list) : list of nodes contained in file
            all_hyperedges (list) : list of hyperedges contained in file

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
    def import_node(filename: str, *imported_node_identifier: str, new_node_name: str = "", copy=True):
        """
        static method importing a node from a GBOML input file

        Args:
           filename (str) : path to GBOML input file
           imported_node_identifier (list <str>) : list of ancestor node names and node name (used for depth-first traversal)
           new_node_name (str) : new identifier of node (for re-naming purposes, optional)
           copy (bool) : keyword argument defining whether a shallow or deep copy of the imported node is created
                         (defaults to True, which produces a deepcopy)

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
                         new_hyperedge_name: str = "", copy=True):
        """
        static method importing a hyperedge from a GBOML input file

        Args:
           filename (str) : path to GBOML input file
           imported_hyperedge_identifier (list <str>) : list of ancestor node names and hyperedge name (used for depth-first traversal)
           new_hyperedge_name (str) : new hyperedge identifier (for re-naming purposes, optional)
           copy (bool) : keyword argument defining whether a shallow or deep copy of the imported node is created (defaults to True, which produces a deepcopy)

        Returns:
            imported_hyperedge (Hyperedge) : imported hyperedge

        """
        old_dir, cut_filename = move_to_directory(filename)
        filename_graph = parse_file(filename)
        imported_hyperedge = filename_graph.get(imported_hyperedge_identifier)

        if imported_hyperedge is None:
            error_("ERROR: In file " + str(filename) + " there is no node named " + str(imported_hyperedge_identifier))

        if type(imported_hyperedge) == Hyperedge:
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
        static method re-naming a node or hyperedge

        Args:
           node_or_hyperedge (Node/Hyperedge) : node or nyperedge to be re-named
           new_name (str) : new name

        """
        node_or_hyperedge.rename(new_name)

    @staticmethod
    def get_object_in_node(in_node, *node_identifier: str, wanted_type=None):
        """
        static method returning a node or a hyperedge given an ancestor node

        Args:
           in_node (Node) : node to which the sub-node is expected to belong
           node_identifier (list <str>) : list of ancestor node names, with first name corresponding to first sub-node and last name corresponding to node to retrieve
           wanted_type (Class Type) : either Node or Hyperedge depending on the type of the object considered

        Returns:
            retrieved_object (Node/Hyperedge) : retrieved node or hyperedge

        """
        current_layer = in_node.get_internal_dict()
        depth_search = len(searched_node)
        retrieved_object = None
        for i, name in enumerate(searched_node):
            if name in current_layer:
                retrieved_object = current_layer[name]
                if i < depth_search - 1 and isinstance(retrieved_object, Hyperedge):
                    error_("Hyperedge objects do not possess subnodes or subhyperedges")
                elif i < depth_search - 1:
                    current_layer = retrieved_object.get_internal_dict()

            else:
                error_("Unknown node or hyperedge named " + str(node_or_hyperedge_name))

        if wanted_type and not isinstance(retrieved_object, wanted_type):
            error_("Error wanted type " + str(wanted_type) + " but that name references a " +
                   str(type(retrieved_object)))

        return retrieved_object

    @staticmethod
    def add_sub_node(node_to_add, in_node):
        """
        static method adding a child node to a given node

        Args:
           node_to_add (Node) : sub-node to add
           in_node (Node) : node to which sub-node should be added

        """
        in_node.add_sub_node(node_to_add)
        in_node.update_internal_dict()

    @staticmethod
    def add_sub_hyperedge(hyperedge_to_add, in_node):
        """
        static method adding a sub-hyperedge to a given node

        Args:
           hyperedge_to_add (Hyperedge) : sub-hyperedge to add
           in_node (Node) : node to which sub-hyperedge should be added

        """
        in_node.add_link(hyperedge_to_add)
        in_node.update_internal_dict()

    @staticmethod
    def redefine_parameter_from_value(node_or_hyperedge, parameter_name: str, value: float):
        """
        static method re-defining the value of a scalar parameter

        Args:
           node_or_hyperedge (Node/Hyperedge) : Node/Hyperedge where the parameter will be redefined
           parameter_name (str) : parameter name
           value (float) : new value of parameter

        """
        expr = Expression('literal', value)
        parameter = Parameter(parameter_name, expr)
        node_or_hyperedge.add_parameter_change(parameter)

    @staticmethod
    def redefine_parameter_from_values(node_or_hyperedge, parameter_name: str, values: list):
        """
        static method re-defining parameter values from a list of values

        Args:
           node_or_hyperedge (Node/Hyperedge) : Node/Hyperedge to which the parameter that should be re-defined belongs
           parameter_name (str) : name of the parameter considered
           values (list<float>) : list of updated parameter values

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
        static method re-defining parameter values from a CSV file

        Args:
           node_or_hyperedge (Node/Hyperedge) : Node/Hyperedge in which the parameter should be re-defined
           parameter_name (str) : parameter name
           filename (str) : name of CSV file

        """

        parameter = Parameter(parameter_name, filename)
        node_or_hyperedge.add_parameter_change(parameter)

    @staticmethod
    def redefine_parameters_from_list(node_or_hyperedge, list_parameters: list = [], list_values: list = []):
        """
        static method re-defining parameter values from a list

        Args:
           node_or_hyperedge (Node/Hyperedge) : Node/Hyperedge in which parameters should be re-defined
           list_parameters (list <str>) : list of parameter names
           list_values (list <float> | list <float> | <str>) : list of parameter values

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
        static method re-defining parameter values from keyword arguments

        Args:
           node_or_hyperedge (Node/Hyperedge) : Node/Hyperedge in which parameters should be re-defined
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
        static method changing the type of a variable

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
        static method removing constraints from a node/hyperedge

        Args:
           node_or_hyperedge (Node/Hyperedge) : Node/Hyperedge from which constraints should be removed
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
        static method removing objectives from a node

        Args:
           node_or_hyperedge (Node/Hyperedge) : node from which objectives should be removed
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
        static method changing the name of a node appearing in the constraints of a given hyperedge

        Args:
           hyperedge (Hyperedge) : Hyperedge in which node names should be changed
           old_node_name (str) : previous node name
           new_node_name (str) : new node name
        """
        change_tuple = [old_node_name, new_node_name, None]
        hyperedge.add_name_change(change_tuple)
