#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# Check arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <demo_src_path> <output_path>"
    exit 1
fi

# Create output directory
mkdir -p "$2"

# Convert to absolute paths
DEMO_SRC_PATH="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
PROJECT_PATH="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"

# Validate input path
if [ ! -d "$DEMO_SRC_PATH" ]; then
    echo "Error: DEMO source path '$DEMO_SRC_PATH' does not exist."
    exit 1
fi

#################################### HELLO VAF DEMO PROJECT #############################################################

# Interface project
vaf project init interface --name HelloInterfaces --project-dir "$PROJECT_PATH"
cd "$PROJECT_PATH"/HelloInterfaces
cp "$DEMO_SRC_PATH"/model/hello_interfaces.py .
vaf model generate --model-dir . --mode all

# Integration project (part 1)
vaf project init integration --name HelloVaf --project-dir "$PROJECT_PATH" --template ""
cd "$PROJECT_PATH"/HelloVaf

# AppModule1
vaf project create app-module --name AppModule1 --namespace demo --project-dir .
cd "$PROJECT_PATH"/HelloVaf/src/application_modules/app_module1
vaf project import --input-file "$PROJECT_PATH"/HelloInterfaces/export/HelloInterfaces.json --model-dir model
cp "$DEMO_SRC_PATH"/model/app_module1.py ./model/
vaf project generate --mode prj --project-dir . --type-variant std --skip-make-preset
cp -r "$DEMO_SRC_PATH"/src/app_module1/* ./implementation/
cd "$PROJECT_PATH"/HelloVaf

# AppModule2
vaf project create app-module --name AppModule2 --namespace demo --project-dir .
cd "$PROJECT_PATH"/HelloVaf/src/application_modules/app_module2
vaf project import --input-file "$PROJECT_PATH"/HelloInterfaces/export/HelloInterfaces.json --model-dir model
cp "$DEMO_SRC_PATH"/model/app_module2.py ./model/
vaf project generate --mode prj --project-dir . --type-variant std --skip-make-preset
cp -r "$DEMO_SRC_PATH"/src/app_module2/* ./implementation/
cd "$PROJECT_PATH"/HelloVaf

# Integration project (part 2)
cp "$DEMO_SRC_PATH"/model/hello_vaf.py ./model/vaf/
vaf model update -p . --model-dir model/vaf --app-modules ""$PROJECT_PATH"/HelloVaf/src/application_modules/app_module1" --app-modules ""$PROJECT_PATH"/HelloVaf/src/application_modules/app_module2"
vaf project generate --mode prj --project-dir . --type-variant std
vaf make install
