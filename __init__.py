from importlib import reload
from . import node_inspector_ui
from . import printer
from . import generate_wrapper
from . import python_highlighter

# Reload modules
reload(node_inspector_ui)
reload(printer)
reload(generate_wrapper)

# Import into package namespace
from . import node_inspector_ui as ni
from . import printer
from . import generate_wrapper
from . import python_highlighter
