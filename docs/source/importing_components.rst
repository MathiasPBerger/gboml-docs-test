Importing Nodes and Hyperedges
------------------------------

Importing Nodes
~~~~~~~~~~~~~~~

A node can be defined by importing an existing node from a GBOML input file. The imported node can be used as such or some of its attributes may be re-defined (e.g., parameter values may be changed), leading to the following syntax rules:

.. code-block:: c

 #NODE <new node identifier> = import <imported node identifier> from <filename>
 #NODE <new node identifier> = import <imported node identifier> from <filename> with <redefinitions>

If the imported node sits at the top of the node hierarchy in the GBOML input file, its identifier should be used. However, if the imported node happens to be deeper in the hierarchy, a sequence of dot-separated identifiers corresponding to its ancestors should be prefixed to its own identifier.
For example, for a GBOML file with a 2-level hierarchy, a child node could be imported by using the following identifier:

.. math::

    \texttt{<parent node identifier>.<child node identifier>}

When importing a node, two types of re-definitions are possible:

 * Re-defining parameter values (i.e., changing the value of an existing parameter).

 * Re-defining variable type (i.e., changing the variable from external to internal or the opposite).

To re-define the values of parameters originally defined in the imported node, their identifiers must be followed by equality signs and new values:

.. code-block:: c

	#NODE <new node identifier> = import <imported node identifier> from <filename> with <parameter identifier> = <parameter value>;

Note that the re-definition of a parameter may not change its type (i.e., vectors must remain vectors and likewise for scalars).
In addition, several parameters can be re-defined in such fashion, provided that each assignment is followed by a semi-colon.

Variable type can be re-defined with the following rules:

.. code-block:: c

 <variable identifier> external;
 <variable identifier> internal;

To illustrate these features, let *file1.txt* be a GBOML input file from which a node should be imported:

.. code-block:: c

  //file1.txt
  #NODE Consumers
  #PARAMETERS
  total_number = 10;

    #NODE consumer_1
    #PARAMETERS
    price_per_unit = 5;
    avg_number_of_units = 100;
    #VARIABLES
    internal : delivery[T];

  #VARIABLES
  internal : consumer_1_delivery[T] <- consumer_1.delivery[T];

Let *consumer_1* be the identifier of the node that should be imported. This node can be imported in another file *file2.txt* as follows:

.. code-block:: c

  //file2.txt
  #NODE average_consumer = import Consumers.consumer_1 from "file1.txt" with
    price_per_unit = 6;
    delivery external;

This code defines the node *average_consumer* by importing the node *consumer_1* from *file1.txt*. It redefines its parameter *price_per_unit* with a different value and changes the type of the variable *delivery* from *internal* to *external*.

Importing Hyperedges
~~~~~~~~~~~~~~~~~~~~

Hyperedges can also be imported from one file to another by using the following rules,

.. code-block:: c

 #HYPEREDGE <hyperedge identifier> = import <identifiers> FROM <filename>
 #HYPEREDGE <hyperedge identifier> = import <identifiers> FROM <filename> with <redefinitions>

The first rule works as the one described for nodes in the previous section. The second rule, however, differs in its possible redefinitions. The parameters redefinition defined for nodes also exists for hyperedges but the variable's coupling redefinition does not as hyperedges do not own a variable set. As node names may differ from one file to another, replacing node names in hyperedges is possible by applying the following rule,

.. code-block:: c

	<old node identifier> <- <new node identifier>;

This rule changes all encountered occurrences of the old node identifier by the new identifier in the hyperedge.
