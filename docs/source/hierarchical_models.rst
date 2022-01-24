Hierarchical Models
-------------------

In the hierarchical hypergraph abstraction underpinning the GBOML language, each node can itself be viewed as a hierarchical hypergraph. Nodes may therefore be constructed from *children* nodes (also referred to as *sub-nodes*) linked by *sub-hyperedges*.

Additional syntax rules must therefore be introduced to enable this feature, as discussed below.

Parameters
==========

Node parameters are local to a parent node, its child nodes and hyperedges. Therefore, parameters defined in a parent node can be accessed in any resulting sub-node or sub-hyperedge by referring to the parent node's identifier in the prefix. In other words, all parent node parameters can be referred to as:

 .. math::

    \texttt{<parent node identifier>.<parameter identifier>}

Given these syntax rules, the following is a valid example of hierarchical parameter use:

 .. code-block:: c

   #PARAMETERS
   gravity       = 9.81;
   speed         = import "speed.txt";

Variables
=========

A parent node can link one or several of its variables with a child node's variable by adding the following to the concerned variable definition before the semicolon,

 .. math::

    \texttt{<- <child node identifier>.<variable identifier>}

 .. math::

    \texttt{<- <child node identifier>.<variable identifier>[<expression>]}

Note that, the child's variable must be of same length and can only be linked with the one of its direct parent.

Given these syntax rules, the following is a valid example of hierarchical variable use:

 .. code-block:: c

   #PARAMETERS
   gravity       = 9.81;
   speed         = import "speed.txt";

Constraints
===========

TBA

Objectives
==========

TBA

Examples should be added to illustrate these features
