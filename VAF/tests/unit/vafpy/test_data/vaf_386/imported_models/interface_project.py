import os

from vaf.vafpy.runtime import (
    get_module_interface,
    import_model,
)

script_path = os.path.dirname(os.path.realpath(__file__))

import_model(os.path.join(script_path, "InterfaceProject.json"))


class Localplanner:
    class Costmap:
        # ModuleInterfaces
        costmap_interface = get_module_interface("CostmapInterface", "localplanner::costmap")

    class Pathcoordinates:
        # ModuleInterfaces
        path_interface = get_module_interface("PathInterface", "localplanner::pathcoordinates")


class Nsprototype:
    class Nsserviceinterface:
        class Nshvaccontrol:
            # ModuleInterfaces
            hvac_control = get_module_interface("HvacControl", "nsprototype::nsserviceinterface::nshvaccontrol")

        class Nshvacstatus:
            # ModuleInterfaces
            hvac_status = get_module_interface("HvacStatus", "nsprototype::nsserviceinterface::nshvacstatus")
