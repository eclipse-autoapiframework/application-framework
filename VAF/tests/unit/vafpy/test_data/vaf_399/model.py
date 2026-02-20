"""Execute to generate the complete model."""

import os

# import the application module model to build up its model
from vaf import save_part_of_main_model

if __name__ == "__main__":
    script_path = os.path.dirname(os.path.realpath(__file__))
    save_part_of_main_model(
        os.path.join(script_path, "model.json"),
        ["DataTypeDefinitions", "ModuleInterfaces", "ApplicationModules"],
        cleanup=CleanupOverride.ENABLE,
    )
