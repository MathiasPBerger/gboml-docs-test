---
title: 'GBOML: Graph-Based Optimization Modeling Language'
authors:
  - name: Bardhyl Miftari^[equally contributing authors]
    affiliation: 1
  - name: Mathias Berger^[equally contributing authors]
    orcid: 0000-0003-3081-4833
    affiliation: 1
  - name: Hatim Djelassi
    affiliation: 1
  - name: Damien Ernst
    orcid: 0000-0002-3035-8260
    affiliation: "1, 2"
affiliations:
  - name: Department of Electrical Engineering and Computer Science, University of Liège, Liège, Belgium
    index: 1
  - name: LTCI, Telecom Paris, Institut Polytechnique de Paris
    index: 2
date: 21 January 2021
bibliography: references.bib
---

# Summary

The graph-based optimization modeling language (GBOML) is a modeling language for mathematical programming enabling the easy implementation of a broad class of structured mixed-integer linear programs typically found in applications ranging from energy system planning to supply chain management. More precisely, the language is particularly well-suited for representing problems involving the optimization of discrete-time dynamical systems over a finite time horizon and possessing a block structure that can be encoded by a sparse connected hypergraph. The language combines elements of both algebraic and object-oriented modeling languages in order to facilitate problem encoding and model re-use, speed up model construction, expose problem structure to specialised solvers and simplify post-processing.

# Statement of need

Many energy system planning and control problems can be formulated as mathematical programs, and the resulting models often possess special structure. Broadly speaking, two classes of tools can be used to implement such models, namely algebraic modeling languages (AMLs) and so-called application-specific tools (ASTs). On the one hand, AMLs usually make it possible to encode problems in a way that is close to mathematical notation. In addition, they are usually very expressive (e.g., any mixed-integer nonlinear program can be encoded) and application-agnostic, and they also interface with a variety of solvers. AMLs can either be stand-alone, such as GAMS [@GAMS] or AMPL [@AMPL], or they may be embedded in general-purpose programming languages, such as JuMP [@JuMP] (in Julia) or Pyomo [@Pyomo] and PuLP [@PuLP] (both in Python). Some of them are also open source (e.g., JuMP, Pyomo and PuLP). In short, AMLs enable users to compactly encode broad classes of optimization problems while decoupling models and solvers. On the other hand, ASTs focus on a specific application (e.g., capacity expansion planning) and can be better understood as modeling frameworks facilitating the construction of instances of a specific problem. As such, ASTs often provide a set of pre-defined components that can be imported to build a model, along with advanced data processing capabilities tailored to the application at hand. In summary, ASTs enable the easy and modular construction of specific problem instances. In the field of energy systems, established ASTs include PyPSA (power flow calculations and capacity expansion planning, among others) [@PyPSA], PowerModels.jl (analysis and comparison of optimal power flow formulations) [@PowerModels], Calliope (multi-energy carrier capacity expansion planning) [@Calliope], Dispa-SET (economic dispatch and unit commitment)[@DispaSET], Balmorel (long-term planning and short-term operational analyses) [@Balmorel] and OSeMOSYS (long-run energy planning) [@OSeMOSYS].

Unfortunately, both AMLs and ASTs suffer from several drawbacks. More precisely, AMLs usually lack modularity. In particular, most AMLs fail to exploit the structure that may exist in a model (e.g., to speed up model generation by parallelising it) or expose it for use by specialised solvers. Extensions to established AMLs have been proposed to address the latter concerns, such as Plasmo [@Plasmo], StructJuMP [@StructJuMP], BlockDecomposition.jl [@BlockDecomposition] (all three being extensions of JuMP), PySP [@PySP] for Pyomo and SML [@SML] for AMPL. However, they still fall short in some ways. For instance, several of them were designed with stochastic programming models in mind, such that only problems with simple primal or dual block angular structures can be represented. On the other hand, ASTs typically lack expressiveness and adding components is often cumbersome. Furthermore, they almost universally rely on AMLs themselves, which implies that they automatically inherit any associated shortcomings. The tool that appears closest in spirit to our own is perhaps the recent SMS++ modeling framework [@SMSpp]. Although the code is publicly available, to the authors' best knowledge, documentation and examples are particularly sparse at the time of writing, which complicates its deployment and use in a practical setting.

In order to address some of these shortcomings, GBOML was designed with the following objectives in mind:

- allowing any mixed-integer linear program to be represented
- enabling hierarchical block structure to be exposed and exploited
- facilitating the encoding and construction of time-indexed models
- allowing low-level model encoding to be close to mathematical notation
- making it easy to re-use and combine components and models
- interfacing with commercial and open source solvers, including structure-exploiting algorithms

The tool has already been used in a research article studying the economics of carbon-neutral fuel production in remote areas where renewable resources are abundant [@RemoteHub].

# Acknowledgements

The authors gratefully acknowledge the support of the Federal Government of Belgium through its Energy Transition Fund and the INTEGRATION project. The authors would also like to thank Adrien Bolland for his help with an early version of the documentation, Jocelyn Mbenoun for testing some early features of the tool, as well as Ghislain Detienne and Thierry Deschuyteneer for constructive discussions.

# References
