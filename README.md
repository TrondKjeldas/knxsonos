# knxsonos [![Build Status](https://travis-ci.org/TrondKjeldas/knxsonos.svg?branch=master)](https://travis-ci.org/TrondKjeldas/knxsonos) [![Latest PyPI version](https://img.shields.io/pypi/v/knxsonos.svg?style=flat)](https://pypi.python.org/pypi/knxsonos/) [![Number of PyPI downloads](https://img.shields.io/pypi/dm/knxsonos.svg?style=flat)](https://pypi.python.org/pypi/knxsonos/)

Control a Sonos system from your KNX installation.

Simple bridging between a KNX system and a Sonos installation.

Specify KNX group addresses for triggering Sonos play/pause/volum/etc.

Supports simple macros, to run multiple commands for the same group address.

Uses [SoCo](https://github.com/SoCo/SoCo) for Sonos control.

## Documentation

### Prerequisites

A KNX IP router/gateway must be available and accessible (currently tested only with EIBD.)

The SoCo python module must be installed (pip install soco)

### Installation

The easiest wat to install knxsonos is to use pip, command:

>pip install knxsonos

### Configuration

The configuration file is written in XML format.

It defines a mapping between a KKNX group address, and one or mor Sonos commands.

Such mappings can be defined either to apply to all zones, or to specific zones only.

It is also possible to define macros, which are groups of commands that can be called upon from both mappings or other macros.

See the knxsonos.config file for example configuration, with comments explaining the various parts.





