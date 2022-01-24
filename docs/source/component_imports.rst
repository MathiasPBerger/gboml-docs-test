Component Imports
-----------------

A node can also be declared by importing it from another GBOML file by using the following rules,

.. code-block:: c

 #NODE <node identifier> = import <identifiers> FROM <filename>
 #NODE <node identifier> = import <identifiers> FROM <filename> WITH <redefinitions>

The first node identifier is the one of the newly declared node. After the *IMPORT* keyword, a series of dot separated identifiers will name the node searched for in the file indicated by *filename*. These dot separated identifiers can name any node in *filename* by giving the full searched name layer by layer. In other words, any sub-node can be imported by identifying it as,

.. math::

    \texttt{<parent identifier>.<sub_node identifier>}

giving the full path from the top layer nodes to the sub-node searched for. Note that if a top layer node is wanted, only its identifier is sufficient.

When importing a given node, there exists two types of possible redefinitions:

 * Parameters'value: Redefining an already existing parameter by a different value.

 * Variables'coupling type: Changing the internal/external type of a variable.

To redefining a parameters'value, the usual parameter definition is needed as explained in the Parameters section with the identifier already existing in the node. Note that the redefinition of a parameter must not change its type (vector or scalar).

The following rule enables to change a variable's coupling type,

.. code-block:: c

 <variable identifier> external;
 <variable identifier> internal;

To illustrate, let us consider the file *file1.txt*,

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
      ...
    #VARIABLES
      internal : consumer_1_delivery[T] <- consumer_1.delivery[T];
      ...

The node *consumer_1* can be imported in another file *file2.txt* as,

.. code-block:: c

  //file2.txt
  #NODE average_consumer = import Consumers.consumer_1 from "file1.txt" with
    price_per_unit = 6;
    delivery external;

This code defines the node *average_consumer* by importing the node *consumer_1* from *file1.txt*. It redefines its parameter *price_per_unit* with a different value and changes the type of the variable *delivery* from *internal* to *external*.
