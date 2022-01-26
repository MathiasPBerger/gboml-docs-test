Hierarchical Models
===================

In the hierarchical hypergraph abstraction underpinning the GBOML language, each node can itself be viewed as a hierarchical hypergraph. Nodes may therefore be constructed in a bottom-up fashion, from *sub-nodes* linked by *sub-hyperedges*.

Sub-nodes and sub-hyperedges are defined between the :math:`\texttt{#PARAMETERS}` and :math:`\texttt{#VARIABLES}` blocks of a parent node. Thus, a typical hierarchical block :math:`\texttt{#NODE}` is structured as follows:

.. code-block:: c

   #NODE <parent node identifier>
      #PARAMETERS
      // parent parameter definitions

      #NODE <sub-node identifier 1>
         #PARAMETERS
         // sub-node 1 parameter definitions
         #VARIABLES
         // sub-node 1 variable definitions
         #CONSTRAINTS
         // sub-node 1 constraint definitions
         #OBJECTIVES
         // sub-node 1 objective definitions

      #NODE <sub-node identifier 2>
         #PARAMETERS
         // sub-node 2 parameter definitions
         #VARIABLES
         // sub-node 2 variable definitions
         #CONSTRAINTS
         // sub-node 2 constraint definitions
         #OBJECTIVES
         // sub-node 2 objective definitions

      #HYPEREDGE <sub-hyperedge identifier>
         #PARAMETERS
         // sub-hyperedge parameter definitions
         #CONSTRAINTS
         // sub-hyperedge constraint definitions

      #VARIABLES
      // parent variable definitions

      #CONSTRAINTS
      // parent constraint definitions

      #OBJECTIVES
      // parent objective definitions

Additional syntax rules must therefore be introduced to enable this feature, as discussed below.

Parameters
~~~~~~~~~~

Node parameters are local to a parent node, its child nodes and hyperedges. Therefore, parameters defined in a parent node can be accessed in any resulting sub-node or sub-hyperedge by referring to the parent node's identifier in the prefix. In other words, all parent node parameters can be referred to as:

 .. math::

    \texttt{<parent node identifier>.<parameter identifier>}

Given these syntax rules, the following is a valid example of hierarchical parameter use:

 .. code-block:: c

   #NODE A

      #PARAMETERS
         parameter_A = 1;

      #NODE B

         #PARAMETERS
            parameter_B = 2;

         #NODE C
            parameter_C = 3;
            sum_parameters = A.parameter_A + parameter_C + B.parameter_B; // = 6


Variables
~~~~~~~~~

A parent node can link one or several of its variables with a child node's variable by adding the following to the concerned variable definition before the semicolon,

 .. math::

    \texttt{<- <child node identifier>.<variable identifier>}

 .. math::

    \texttt{<- <child node identifier>.<variable identifier>[<expression>]}

Note that, the child's variable must be of same length and can only be linked with the one of its direct parent.

Given these syntax rules, the following is a valid example of hierarchical variable use:

 .. code-block:: c

   #NODE A

      #NODE B

         #VARIABLES
            internal : x[10];
            ...
      #NODE C

         #VARIABLES
            internal : x[10];


      #VARIABLES
         internal : y[10] <- B.x[10];
         external : z[10] <- C.x[10];

A full valid, hierarchical GBOML is given as follows,

 .. code-block:: c

   #TIMEHORIZON T = 2;

   #NODE A
      #PARAMETERS
         parameter_A = 1;

      #NODE B
         #PARAMETERS
            parameter_B = 1+A.parameter_A;
         #VARIABLES
            internal : x[10];
         #CONSTRAINTS
            x[t] >= parameter_B;

      #NODE C
         #PARAMETERS
            parameter_C = 2+A.parameter_A;
         #VARIABLES
            internal : x[10];
         #CONSTRAINTS
            x[t] >= parameter_C;

      #VARIABLES
         internal : y[10] <- B.x[10];
         external : z[10] <- C.x[10];

      #CONSTRAINTS
         y[t]+z[t] >= 6;

      #OBJECTIVES
         min: y[t]+z[t];
