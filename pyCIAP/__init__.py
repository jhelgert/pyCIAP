
from .dsur_cy import DSUR
try:
    from .ciap_mdt import solveCIAPMDT
except ImportError:
    print("Gurobipy is not installed. solveCIAPMDT disabled.")
