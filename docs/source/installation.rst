Installation
============

The installation steps are the following:

* First, GBOML from the git

* Second, install its requirements

* Third, install a solver from the list of supported solvers and install its interface library

And that's it.

Cloning the git
-----------------
The git can be found at https://gitlab.uliege.be/smart_grids/public/gboml. You can either directly download it from there or use

::

	$ git clone https://gitlab.uliege.be/smart_grids/public/gboml

Installing the requirements
---------------------------

To install all the requirements, all you need to do is

::

	$ pip install -r requirements.txt

Installing the solvers
----------------------
GBOML interfaces with Gurobi, CPLEX, CBC/CLP and DSP. Only one of these is required to solve a GBOML problem. Gurobi and CPLEX are commercial solvers for which academic licences can be granted. CBC/CLP is an open-source solver. DSP is an open-source project which relies on CPLEX and Gurobi to implement structure exploiting methods. The state of DSP is still experimental and should be checked.

Gurobi
~~~~~~

First, you need to install Gurobi. For that, please refer to https://www.gurobi.com/.
Once Gurobi installed, you will need to install its python interface library with

::

	$ python -m pip install -i https://pypi.gurobi.com gurobipy

CPLEX
~~~~~
To be able to use CPLEX, you must install it via https://www.ibm.com/support/pages/downloading-ibm-ilog-cplex-optimization-studio-2010. Once the installation done, the python interface library can be downloaded by writing

::

	$ pip install cplex

Cbc/Clp
~~~~~~~

The installation can be done via https://projects.coin-or.org/Cbc. The interface package can be installed by doing

::

	$ pip install cylp

DSP
~~~

The installation can be done via 

::

    $ git clone --recursive https://github.com/Argonne-National-Laboratory/DSP.git
    $ mkdir build
    $ cd build
    $ cmake ..
    $ make 

The installation steps can also be found at https://github.com/Argonne-National-Laboratory/DSP. Note that the file :math:`\texttt{CMakeLists.txt}` shall be filed after the cloning with the path to the different solvers. An important note also is that DSP is unsupported by native Windows. However, installing DSP with the Windows Subsystem Linux UBUNTU 18.04 is possible. 