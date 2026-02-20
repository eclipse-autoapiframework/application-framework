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

#################################### VSS DEMO PROJECT #############################################################

# Integration project (part 1)
vaf project init integration --name DemoExecutable --project-dir "$PROJECT_PATH" --template ""
cd "$PROJECT_PATH"/DemoExecutable

# VSS Provider
vaf project create app-module --name VssProvider --namespace demo --project-dir .
cd "$PROJECT_PATH"/DemoExecutable/src/application_modules/vss_provider
vaf model import vss --input-file "$DEMO_SRC_PATH"/model/vss/vss.json
cp "$DEMO_SRC_PATH"/model/vaf/vss_provider.py ./model/
vaf project generate --mode prj --project-dir . --type-variant std --skip-make-preset
cp -r "$DEMO_SRC_PATH"/src/vss_provider/* ./implementation/
cd "$PROJECT_PATH"/DemoExecutable

# VSS Consumer
vaf project create app-module --name VssConsumer --namespace demo --project-dir .
cd "$PROJECT_PATH"/DemoExecutable/src/application_modules/vss_consumer
vaf model import vss --input-file "$DEMO_SRC_PATH"/model/vss/vss.json
cp "$DEMO_SRC_PATH"/model/vaf/vss_consumer.py ./model/
vaf project generate --mode prj --project-dir . --type-variant std --skip-make-preset
cp -r "$DEMO_SRC_PATH"/src/vss_consumer/* ./implementation/
cd "$PROJECT_PATH"/DemoExecutable

# Integration project (part 2)
cp "$DEMO_SRC_PATH"/model/vaf/demo_executable.py ./model/vaf/
vaf model update -p . --model-dir model/vaf --app-modules ""$PROJECT_PATH"/DemoExecutable/src/application_modules/vss_provider" --app-modules ""$PROJECT_PATH"/DemoExecutable/src/application_modules/vss_consumer"
vaf project generate --mode prj --project-dir . --type-variant std
vaf make install
