Python Interface
================

.. automodule:: pyGBOML
   :members:

Example
~~~~~~~

In the following example, we will toy around with the different functions of defined in the *GbomlGraph*.

First, we need to load the library to do so, one can do,

.. code-block:: python

   from gboml_script import GbomlGraph

Second, we initialize an instance of *GbomlGraph* with a timehorizon of 3,

.. code-block:: python

   timehorizon = 3
   gboml_model = GbomlGraph(timehorizon)

Third, we import all the nodes from the microgrid example,

.. code-block:: python

   nodes, edges = gboml_model.import_all_nodes_and_edges("examples/microgrid/microgrid.txt")

Then, let us rename all the nodes and hyperedges by adding "new\_" to all the nodes and hyperedges,

.. code-block:: python

   old_names = []
      for node in nodes:
         old_names.append(node.get_name())
         gboml_model_with_1.rename(node, "new_"+node.get_name())

      for hyperedge in edges:
         gboml_model_with_1.rename(hyperedge, "new_"+hyperedge.get_name())
         for i, node in enumerate(nodes):
            gboml_model_with_1.change_node_name_in_hyperedge(hyperedge, old_names[i], node.get_name())

We can now, for instance, load a toy node, named :math:`\texttt{H}`, present in the test as test6.txt which simply defines a variable :math:`\texttt{x[T]}`, a parameter :math:`\texttt{b=4}`, a constraint :math:`\texttt{x[t]>= b}` and an objective :math:`\texttt{min : x[t]}`. We will encapsulate all the microgrid problem inside this node.

.. code-block:: python

   parent = gboml_model.import_node("test/test6.txt", "H", copy=True)
   for node in nodes:
      gboml_model.add_sub_node(node, parent)

   for edge in edges:
      gboml_model.add_sub_hyperedge(edge, parent)

Let us now to tweak the value of the parent's parameter :math:`\texttt{b=6}`,

.. code-block:: python

   gboml_model.redefine_parameters_from_keywords(parent, b=6)

We will wrap everything now by adding the parent node to the model and solving it by using CPLEX,

.. code-block:: python

   gboml_model.add_nodes_in_model(parent)
   gboml_model.build_model()
   solution = gboml_model.solve_cplex()

The full code is written as follow,

.. code-block:: python

   from gboml_script import GbomlGraph

   timehorizon = 3
   gboml_model = GbomlGraph(timehorizon)
   nodes, edges = gboml_model.import_all_nodes_and_edges("examples/microgrid/microgrid.txt")
   old_names = []
      for node in nodes:
         old_names.append(node.get_name())
         gboml_model_with_1.rename(node, "new_"+node.get_name())

      for hyperedge in edges:
         gboml_model_with_1.rename(hyperedge, "new_"+hyperedge.get_name())
         for i, node in enumerate(nodes):
            gboml_model_with_1.change_node_name_in_hyperedge(hyperedge, old_names[i], node.get_name())

   parent = gboml_model.import_node("test/test6.txt", "H", copy=True)
   for node in nodes:
      gboml_model.add_sub_node(node, parent)

   for edge in edges:
      gboml_model.add_sub_hyperedge(edge, parent)

   gboml_model.redefine_parameters_from_keywords(parent, b=6)
   gboml_model.add_nodes_in_model(parent)
   gboml_model.build_model()
   solution = gboml_model.solve_cplex()
