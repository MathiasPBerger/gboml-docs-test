Command Line Interface
======================

.. code-block:: bash

   python main.py <file> <options>

where :math:`\texttt{<file>}` is the name of the file to be considered and :math:`\texttt{<options>}` one or several options flags that can be activated.
The options are the following :

* *Print tokens*: To print the tokens outputted by the lexer you can add

.. code-block:: bash

   --lex

* *Print the syntax tree*: To print the syntax tree by the parser you can add

.. code-block:: bash

   --parser

* *Print the matrices*: To print the matrix A, the vector b and C

.. code-block:: bash

   --matrix

* *Linprog*: Use Linprog solver

.. code-block:: bash

   --linprog

* *Gurobi*: Use Gurobi solver

.. code-block:: bash

   --gurobi

* *CPLEX*: Use CPLEX solver

.. code-block:: bash

   --cplex

* *Cbc/Clp*: Use Cbc/Clp solver

.. code-block:: bash

   --clp

* *DSP Extensive form*: Use DSP's Extensive Form algorithm (Warning still experimental)

.. code-block:: bash

   --dsp_de

* *DSP Dantzig-Wolf*: Use DSP's Dantzig-Wolf algorithm  (Warning still experimental)

.. code-block:: bash

   --dsp_dw

* *CSV*: Output a csv file of the solution

.. code-block:: bash

   --csv

* *JSON*: Output a json file of the solution

.. code-block:: bash

   --json

* *detailed Json*: Output a more detailed version of the json file containing various solver info

.. code-block:: bash

	--detailed_json

* *Multi-processing*: Number of processes considered for the model creation

.. code-block:: bash

	--nb_processes <number>

where :math:`\texttt{<number>}` is a integer with the default value being 1

* *output*: Set the output name

.. code-block:: bash

	--output <output_filename>

where :math:`\texttt{<output_filename>}` is the output filename once the extension (either csv or json) is chosen. The default output name is the :math:`\texttt{<file>}`'s name with the addition of the date and the corresponding chosen extension.
