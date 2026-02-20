from pathlib import Path

# Import the application module model
from vaf import save_part_of_main_model
from vaf.core.common.utils import ProjectType


def export_model():
    script_path = Path(__file__).resolve().parent
    save_part_of_main_model(
        script_path / "model.json",
        ["DataTypeDefinitions", "ModuleInterfaces", "ApplicationModules"],
        project_type=ProjectType.APP_MODULE,
        cleanup=CleanupOverride.ENABLE,
    )


if __name__ == "__main__":
    export_model()
