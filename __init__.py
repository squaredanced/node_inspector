from importlib import reload
from . import node_inspector_ui
from . import printer
from . import generate_wrapper
from . import python_highlighter
from . import widgets_construct

# Reload modules
reload(node_inspector_ui)
reload(printer)
reload(generate_wrapper)
reload(widgets_construct)

# Import into package namespace
from . import node_inspector_ui as ni
from . import printer
from . import generate_wrapper
from . import widgets_construct
