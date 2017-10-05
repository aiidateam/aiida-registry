# Available AiiDA Plugins


## aiida-quantumespresso

Author: The AiiDA team

Version: 0.1.0

Plugin home page: [](http://www.aiida.net)

Base entry point: quantumespresso

Install command: `pip install git+https://github.com/aiidateam/aiida-quantumespresso#egg=aiida-quantumespresso-0.1.0``

Plugin code repository: []()

### Description: 

The official AiiDA plugin for Quantum ESPRESSO

### Plugin classes:


#### calculations

* quantumespresso.cp

* quantumespresso.dos

* quantumespresso.matdyn

* quantumespresso.namelists

* quantumespresso.neb

* quantumespresso.ph

* quantumespresso.pp

* quantumespresso.pw

* quantumespresso.projwfc

* quantumespresso.pw2wannier90

* quantumespresso.q2r

* quantumespresso.pwimmigrant



#### parsers

* quantumespresso.basicpw

* quantumespresso.cp

* quantumespresso.dos

* quantumespresso.matdyn

* quantumespresso.neb

* quantumespresso.ph

* quantumespresso.projwfc

* quantumespresso.pw

* quantumespresso.q2r



#### data

* quantumespresso.forceconstants



#### aiida_quantumespresso.workflows.error_handlers



#### workflows

* quantumespresso.ph.base

* quantumespresso.pw.base

* quantumespresso.pw.relax

* quantumespresso.pw.bands

* quantumespresso.pw.band_structure



#### tools.dbexporters.tcod_plugins

* quantumespresso.cp

* quantumespresso.pw



## aiida-quantumespresso-uscf

Author: Sebastiaan P. Huber

Version: 0.1.0

Plugin home page: [](https://github.com/sphuber/aiida-quantumespresso-uscf)

Base entry point: quantumespresso.uscf

Install command: `pip install None``

Plugin code repository: []()

### Description: 

The AiiDA plugin for the Uscf module of Quantum ESPRESSO

### Plugin classes:


#### calculations

* quantumespresso.uscf



#### parsers

* quantumespresso.uscf



#### workflows

* quantumespresso.uscf.main

* quantumespresso.uscf.parallelize_atoms

* quantumespresso.uscf.base



## aiida-mul

Author: Rico Haeuselmann

Version: 0.1

Plugin home page: [](https://github.com/DropD/aiida-mul)

Base entry point: mul

Install command: `pip install git+https://github.com/DropD/aiida-mul#egg=aiida-mul-0.1``

Plugin code repository: []()

### Description: 

Simple, useless plugin for testing and demonstration

### Plugin classes:


#### calculations

* mul



#### parsers

* mul



## aiida-cp2k

Author: Ole Schütt, Aliaksandr Yakutovich, Patrick Seewald, Tiziano Müller, Andreas Glöss, Leonid Kahle

Version: 0.2.2

Plugin home page: [](https://github.com/cp2k/aiida-cp2k)

Base entry point: cp2k

Install command: `pip install None``

Plugin code repository: []()

### Description: 

A plugin to run CP2K calculations and workflows

### Plugin classes:


#### calculations

* cp2k



#### parsers

* cp2k



## aiida-wannier90

Author: Daniel Marchand, Antimo Marrazzo, Dominik Gresch, Giovanni Pizzi & The AiiDA Team.

Version: 0.1.0

Plugin home page: [](MISSING INFORMATION!)

Base entry point: wannier90

Install command: `pip install git+https://github.com/aiidateam/aiida-wannier90``

Plugin code repository: []()

### Description: 

AiiDA Plugin for Wannier90

### Plugin classes:


#### calculations

* wannier90.wannier90



#### parsers

* wannier90.wannier90



#### data



## aiida-fleur

Author: Jens Broeder

Version: 0.5.0

Plugin home page: [](https://github.com/broeder-j/aiida-fleur)

Base entry point: fleur

Install command: `pip install git+https://github.com/broeder-j/aiida_fleur/#egg=aiida-fleur-0.5.0``

Plugin code repository: []()

### Description: 

Python FLEUR simulation package containing an AiiDA Plugin for running the FLEUR-code and its input generator. Plus some workflows and utility

### Plugin classes:


#### calculations

* fleur.fleur

* fleur.inpgen



#### parsers

* fleur.fleurparser

* fleur.fleurinpgenparser



#### data

* fleur.fleurinp

* fleur.fleurinpmodifier



#### workflows

* fleur.scf

* fleur.dos

* fleur.band

* fleur.eos

* fleur.dummy

* fleur.sub_dummy

* fleur.init_cls

* fleur.corehole

* fleur.corelevel



## aiida-vasp

Author: MISSING INFORMATION!

Version: MISSING INFORMATION!

Plugin home page: [](MISSING INFORMATION!)

Base entry point: vasp

Install command: `pip install None``

Plugin code repository: []()

### Description: 

MISSING INFORMATION!

### Plugin classes:

