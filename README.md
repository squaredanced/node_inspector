# Houdini Node Inspector

This is toolset for gathering information from the node in covnenient form.
I have been using a lot of it's fuctionality in my Houdini TD work but every time I had to rewrite the same functionality.
This is a collection of small things that never around when they needed.
____

So I decided to make a swiss-knife-style toolset for quickly getting info from the node like:
  - Get all parameter names
  - Get all parameter labels
  - Get user data
  - Quickly convert parameters to class-properties
  - Get callbacks
  - Get conditionals
  - Explode HDA to subnetwork
  - etc.
___

## Installation

Right now it is not fully wrapped and I plan to deliver it in different flavors later (py-panel, node, shelf-tool).

If you want to use or test it now, here's how:
- Clone this repo to your `$HOME\houdini19.X\python3.9libs` (user preferences folder).
- Restart Houdini if it was running.
- In Houdini create shelf tool with following code:
  ```python
  from node_inspector import node_inspector_ui as ni
  window = ni.MainWIndow()
  window.show()
  ```
  

## Current State 

Right now this is just a skeleton of future toolset.
I implemented PySide2 interface (i think a lot of things from here would be helpful to people learning PySide/PyQt).
This shouldn't take too long to finish and can be useful on any stage of development
    
