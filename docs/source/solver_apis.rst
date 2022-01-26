Solver APIs
-----------

The GBOML parser interfaces with a variety of open source and commercial solvers in order to solve optimization models.
Direct access to their API is provided for several solvers, allowing users to tune algorithm parameters and query complementary information
(e.g., dual variables, slacks or basis ranges, when available). Such parameters must be placed in file named *solver_name.opt*.
More information about solver parameters can typically be found on the website of the respective solver (e.g., for `Gurobi <https://www.gurobi.com/documentation/9.1/refman/parameters.html>`_).

The list of attributes that may be queried from the different solvers can be found below:

* Gurobi: the following constraint attributes can be queried from the solver: *Pi* (dual variables), *Slack* (slack variables), *CBasis* (whether slack variable is in simplex basis), *SARHSLow* (right-hand side basis sensitivity information), *SARHSUp* (right-hand side basis sensitivity information).
In addition, the following variable attributes can be queried (most of them useful for sensitivity  analyses): *VBasis*, *SAObjLow*, *SAObjUp*, *SALBLow*, *SALBUp*, *SAUBLow*, *SAUBUp*. More details can be found on the `Gurobi website <https://www.gurobi.com/documentation/9.1/refman/attributes.html>`_.

* CPLEX: the following constraint attributes can be queried: dual and slack variables. The following variable attributes can be queried: basis information and dual norms.

* Xpress: constrs: "dual", "slack"; vars: "reduced_cost",

* Cbc/Clp: the Cbc/Clp API is still under development at present.
