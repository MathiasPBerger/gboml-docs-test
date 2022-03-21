---
title: 'GBOML: Graph-Based Optimization Modeling Language'
author:
  - name: Bardhyl Miftari
    email: bmiftari@uliege.be
    equal_contributor: True
    correspondence: True
    institute: ULg
  - name: Mathias Berger
    email: mathias.berger@uliege.be
    equal_contributor: True
    correspondence: True
    institute: ULg
  - name: Hatim Djelassi
    institute: ULg
  - name: Damien Ernst
    institute: ULg, Telecom
institute:
  - ULg: Department of Electrical Engineering and Computer Science, University of Liège.
  - Telecom: LTCI, Telecom Paris, Institut Polytechnique de Paris.
date: 28 January 2021
output:
  pdf_document:
    number_sections: yes
    toc: yes
    toc_depth: 4
    pandoc_args:
      - '--lua-filter=scholarly-metadata.lua'
      - '--lua-filter=author-info-blocks.lua'
bibliography: references.bib
---

# Summary

The Graph-Based Optimization Modeling Language (GBOML) is a modeling language for mathematical programming enabling the easy implementation of a broad class of structured mixed-integer linear programs typically found in applications ranging from energy system planning to supply chain management. More precisely, the language is particularly well-suited for representing problems involving the optimization of discrete-time dynamical systems over a finite time horizon and possessing a block structure that can be encoded by a hierarchical hypergraph. The language combines elements of both algebraic and object-oriented modeling languages in order to facilitate problem encoding and model re-use, speed up model generation, expose problem structure to specialised solvers and simplify post-processing. The GBOML parser, which is implemented in Python, turns GBOML input files into hierarchical graph data structures representing optimization models. The associated tool provides both a command-line interface and a Python API to construct models, and directly interfaces with a variety of open-source and commercial solvers, including structure-exploiting ones.

# Statement of need

Many planning and control problems (e.g., in the field of energy systems) can be formulated as mathematical programs. Notably, many models of practical interest can be viewed as collections of smaller models with some form of coupling between them. Such models display a natural block structure, where each block represents a small model.

Broadly speaking, two classes of tools can be used to implement such models, namely algebraic modeling languages (AMLs) and so-called object-oriented modeling environments (OOEMs). In short, AMLs typically allow users to compactly encode broad classes of optimization problems (e.g., mixed-integer nonlinear programs) while decoupling models and solvers. AMLs can be either stand-alone (e.g., GAMS [@GAMS] or AMPL [@AMPL]) or embedded in general-purpose programming languages, such as JuMP [@JuMP] (in Julia), Pyomo [@Pyomo] and PuLP [@PuLP] (in Python). They may also be open source (e.g., JuMP, Pyomo and PuLP). On the other hand, OOEMs usually make it easy to construct instances of specific problems from pre-defined components. For instance, in the field of energy systems, established OOEMs include PyPSA (power flow calculations and capacity expansion planning) [@PyPSA], Calliope (multi-energy carrier capacity expansion planning) [@Calliope] or Balmorel (long-term planning and short-term operational analyses) [@Balmorel].

Unfortunately, both AMLs and OOEMS suffer from several drawbacks. More precisely, AMLs usually lack modularity, which is defined as the ability to take advantage of problem structure for various purposes, including simplifying problem encoding, enabling model re-use, speeding up model generation (e.g., by parallelising it) and facilitating the use of structure-exploiting solution algorithms. Extensions to established AMLs were proposed to address the latter concern, such as StructJuMP [@StructJuMP], BlockDecomposition.jl [@BlockDecomposition] (extending JuMP), PySP [@PySP] and SML [@SML] (extending Pyomo and AMPL, respectively). However, these extensions were usually designed with the primary aim of exposing very specific problem structures (e.g., dual block angular structures found in stochastic linear  programming models) or facilitating the use of specific structure-exploiting algorithms (e.g., branch-price-and-cut). On the other hand, OOEMs typically lack expressiveness and adding components is often cumbersome. Furthermore, they usually rely on established AMLs themselves and thus automatically inherit any shortcomings of the AML on top of which they are built (e.g., it may not be open source).

The tools that appear closest in spirit to our own are the recent SMS++ modeling framework [@SMSpp] and Plasmo.jl [@Plasmo] (an extension of JuMP). The former makes it possible to implement fairly general block-structured models and aims to ease the development and deployment of advanced structure-exploiting algorithms. The latter relies on a graph abstraction of optimization models to enable modular model construction, partitioning and the use of structure-exploiting algorithms.

Against this backdrop, GBOML was designed to blend and natively support some key features of AMLs and OOMEs. Notably, it was built with the following goals in mind:

- being open-source, stand-alone and lightweight
- allowing any mixed-integer linear program to be represented
- enabling any hierarchical block structure to be exposed and exploited
- facilitating the encoding and construction of time-indexed models
- allowing low-level model encoding to be close to mathematical notation
- making it easy to re-use and combine components and models
- interfacing with commercial and open-source solvers, including structure-exploiting ones

Next, we describe a short example illustrating the GBOML workflow. First, a model must encoded by a user in a GBOML input file. The code block below displays such an input file. The

.. code-block::

	#TIMEHORIZON
	T = 24; // number of hours in twenty years

	#NODE SOLAR_PV
	#PARAMETERS
	capex = 600; // capital expenditure per unit capacity
	capacity_factor = import "pv_gen.csv";
	#VARIABLES
	internal: capacity;
	internal: investment_cost;
	external: electricity[T];
	#CONSTRAINTS
	capacity >= 0;
	electricity[t] >= 0;
	electricity[t] <= capacity_factor[mod(t, 24)] * capacity;
	investment_cost == capex * capacity;
	#OBJECTIVES
	min: investment_cost;

	#NODE BATTERY
	#PARAMETERS
	capex = 150; // capital expenditure per unit capacity
	efficiency = 0.75;
	#VARIABLES
	internal: capacity;
	internal: investment_cost;
	internal: energy[T];
	external: charge[T];
	external: discharge[T];
	#CONSTRAINTS
	capacity >= 0;
	energy[t] >= 0;
	charge[t] >= 0;
	discharge[t] >= 0;
	energy[t] <= capacity;
	energy[t+1] == energy[t] + efficiency * charge[t] - discharge[t] / efficiency;
	energy[0] == energy[T-1];
	investment_cost == capex * capacity;
	#OBJECTIVES
	min: investment_cost;

	#HYPEREDGE POWER_BALANCE
	#PARAMETERS
	load = 10;
	#CONSTRAINTS
	SOLAR_PV.electricity[t] + BATTERY.discharge[t] == load[t] + BATTERY.charge[t];

This file must then be parsed by the GBOML parser, which is implemented in Python. A command-line interface as well as a Python API are available to work with models, which makes it possible to cater to a broad audience including both users with little programming experience and users who are proficient in Python. Model generation can also be parallelised based on the structure provided by the user. Models are then passed to open-source or commercial solvers. Direct access to solver APIs is also provided, allowing users to tune algorithm parameters and retrieve complementary information (e.g., dual variables, slacks or basis ranges, when available). Finally, results are retrieved and can be either used directly in Python or printed to file. Two file formats are currently supported, namely CSV and JSON.

An early version of the tool was used in a research article studying the economics of carbon-neutral fuel production in remote areas where renewable resources are abundant [@RemoteHub]. The tool is also used in the context of a research project focusing on the design of the future Belgian energy system.

# Acknowledgements

The authors gratefully acknowledge the support of the Federal Government of Belgium through its Energy Transition Fund and the INTEGRATION project. The authors would also like to thank Adrien Bolland for his help with an early version of the documentation, Jocelyn Mbenoun for testing some early features of the tool, as well as Ghislain Detienne and Thierry Deschuyteneer for constructive discussions.

# References
