# -*- coding: utf-8 -*-
"""
Module contains several helper classes and functions, used by the Fabric tasks.
Module is created and maintained as a part of this project i.e. is not part of the Fabric itself.

Submodules
----------
- api: The main module you should use when writing tasks. It introduces commonly used classes and functions from
  other modules
- base: Module is dependant only itself. Contains for example Config class
- utils: Util classes written using base module
- auth: Authentication specific module

Dependencies
------------
Modules are dependent on each other as follows:

    .. graphviz::

        digraph dependencies {
            fabric -> base;
            fabric -> base -> auth -> api;
            fabric -> base -> utils -> api;
        }

"""
