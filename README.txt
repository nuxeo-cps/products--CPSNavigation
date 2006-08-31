======
README
======

:Author: Benoit Delbosc
:Revision: $Id$

.. sectnum::    :depth: 4
.. contents::   :depth: 4


Goal
====

Make it very easy to create a kind of Explorer for each of the
following:

- Documents

  - using portal_tree for folders and documents

- All Vocabularies

  - Hierarchy vocabulary

- Directories

  - acl_users

  - ldap


What is an explorer?
====================

Assuming that a node is a container and a leaf is not.

An Explorer contains 2 parts:

- The left part displays the hierarchy of node using a tree; the path
  to the selected node is expanded (display all children of
  parents of the selected node).

- The right part displays a listing of the content of the selected
  node; it may display either nodes and leaves, only nodes, or only
  leaves. This part should handle filtering, sorting and batching.


Make These Tasks Easy
=====================

The following should be easy to do:

- We don't want any processing from ZPT or Python scripts.

- Writing a new explorer should be simple.


Howto write a new explorer
==========================

You have to write a new navigation class.

To write your navigation class you have to inherit from BaseNavigation and
implement the IFinder interface.



.. Emacs
.. Local Variables:
.. mode: rst
.. End:
.. Vim
.. vim: set filetype=rst:

