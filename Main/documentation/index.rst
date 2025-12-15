.. Shroom Raider documentation master file, created by
   sphinx-quickstart on Sun Dec 14 22:37:58 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

=============
Shroom Raider 
=============

Main Game Logic
***************

.. automodule:: shroom_raider
   :members:
   
Entity 
******

.. automodule:: classes.entity
   :members:

Entities
--------

Axe
^^^
.. automodule:: classes.entities.axe
   :members:

Flamethrower
^^^^^^^^^^^^
.. automodule:: classes.entities.flamethrower
   :members:

Mushroom
^^^^^^^^
.. automodule:: classes.entities.mushroom
   :members:

Paved Tile
^^^^^^^^^^
.. automodule:: classes.entities.pavedtile
   :members:

Player
^^^^^^
.. automodule:: classes.entities.player
   :members:

Rock
^^^^
.. automodule:: classes.entities.rock
   :members:

Tree
^^^^
.. automodule:: classes.entities.tree
   :members:

Water
^^^^^
.. automodule:: classes.entities.water
   :members:


Import Tools
------------
.. autofunction:: classes.entities.import_entities.import_entities


Grid
****
.. automodule:: classes.grid
   :members:


Leaderboard and Player Data
***************************

Leaderboard
-----------
.. automodule:: bonusclasses.leaderboard 
   :members:


Player Data
-----------
.. automodule:: bonusclasses.playerdata
   :members:

Security System
---------------
.. automodule:: bonusclasses.security
   :members:


Utils
*****

Enums
-----
.. automodule:: utils.enums
   :members:

General Utils
-------------
.. automodule:: utils.general_utils
   :members:

.. automodule:: utils.generate_tests_to_csv