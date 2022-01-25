Hyperedges
----------

A hyperedge typically couples variables belonging to different nodes via equality or inequality constraints (or both). Each hyperedge is defined using a :math:`\texttt{#HYPEREDGE}` block. A hyperedge must have a unique :math:`\texttt{<identifier>}` and no two hyperedges or hyperedge and node may have the same identifier. In addition, a hyperedge may have its own parameters and constraints.
Hence, a :math:`\texttt{#HYPEREDGE}` block has the following structure:

.. code-block:: c

   #HYPEREDGE <identifier>
   #PARAMETERS
   // parameter definitions
   #CONSTRAINTS
   // constraint definitions

Parameters and constraints are further described below.

Parameters
==========

Parameters defined in a :math:`\texttt{#HYPEREDGE}` block follow the exact same rules as the ones defined in :math:`\texttt{#NODE}` blocks.

Constraints
===========

While affine constraints involving all variables declared in a :math:`\texttt{#NODE}` block can be defined in the same block, constraints defined in :math:`\texttt{#HYPEREDGE}` blocks couple :math:`\texttt{external}` variables associated with any subset of nodes.
The syntax for defining constraints is otherwise the same as the one used in :math:`\texttt{#NODE}` blocks:

.. code-block:: c

  #CONSTRAINTS
   <expression> == <expression> <expansion range>;
   <expression> <= <expression> <expansion range>;
   <expression> >= <expression> <expansion range>;

Similarly to the constraints defined in nodes, hyperedges can also be named by adding an identifier with colon defore the constraint, as follows,

.. math::

    \texttt{<constraint identifier>: <constraint>;}

Given these syntax rules, the following is an example including valid :math:`\texttt{#HYPEREDGE}` blocks (and associated :math:`\texttt{#NODE}` blocks):

.. code-block:: c

   #TIMEHORIZON
   // time horizon definition

   #NODE node1
   #VARIABLES
   external : x;
   external : inflow[T];
   // further node content

   #NODE node2
   #VARIABLES
   external : y;
   external : outflow[T];
   // further node content

   #HYPEREDGE hyperedge1
   #CONSTRAINTS
   node1.inflow[t] == node2.outflow[t];

   #NODE node3
   #VARIABLES
   external : z;
   // further node content

   #HYPEREDGE hyperedge2
   #PARAMETERS
   weight = {1/3,2/3};
   #CONSTRAINTS
   node1.x <= weight[0]*node2.y + weight[1]*node3.z;
   node2.y <= node3.z
