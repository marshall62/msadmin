# admin.py needs to be in this main directory because Django looks for it here to define the way
# admin site works.   The customizations are imported from each of the modules admin files.
from .sa2.admin import *