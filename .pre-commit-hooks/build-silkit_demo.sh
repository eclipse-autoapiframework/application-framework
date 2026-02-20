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

#################################### ADAS DEMO APP PROJECT #############################################################
DEMO_APP_SRC_PATH=$DEMO_SRC_PATH/app

# Interface project
vaf project init interface --name Interfaces --project-dir "$PROJECT_PATH"
cd "$PROJECT_PATH"/Interfaces
cp "$DEMO_APP_SRC_PATH"/model/interfaces.py .
vaf model generate --model-dir . --mode ALL

# SensorFusion
vaf project init app-module --name SensorFusion --namespace NsApplicationUnit::NsSensorFusion --project-dir "$PROJECT_PATH"
cd "$PROJECT_PATH"/SensorFusion
vaf project import --input-file ../Interfaces/export/Interfaces.json --model-dir model
cp "$DEMO_APP_SRC_PATH"/model/sensor_fusion.py ./model/
vaf project generate --mode prj --project-dir . --type-variant std --skip-make-preset
cp -r "$DEMO_APP_SRC_PATH"/src/sensor_fusion/* ./implementation/

# CollisionDetection
vaf project init app-module --name CollisionDetection --namespace NsApplicationUnit::NsCollisionDetection --project-dir "$PROJECT_PATH"
cd "$PROJECT_PATH"/CollisionDetection
vaf project import --input-file ../Interfaces/export/Interfaces.json --model-dir model
cp "$DEMO_APP_SRC_PATH"/model/collision_detection.py ./model/
vaf project generate --mode prj --project-dir . --type-variant std --skip-make-preset
cp -r "$DEMO_APP_SRC_PATH"/src/collision_detection/* ./implementation/

# Integration project
vaf project init integration --name AdasDemoSilKit --project-dir "$PROJECT_PATH" --template ""
cd "$PROJECT_PATH"/AdasDemoSilKit
vaf project import --input-dir ../SensorFusion --project-dir .
vaf project import --input-dir ../CollisionDetection --project-dir .
cp "$DEMO_APP_SRC_PATH"/model/adas_demo_sil_kit.py ./model/vaf/
vaf project generate --mode prj --project-dir . --type-variant std
vaf make install

#################################### ADAS DEMO TEST-APP PROJECT ########################################################
DEMO_TEST_APP_SRC_PATH=$DEMO_SRC_PATH/test-app

# Integration Project
vaf project init integration --name AdasSilKitPlatform --project-dir "$PROJECT_PATH" --template ""
cd "$PROJECT_PATH"/AdasSilKitPlatform

# Creating Application Module: SilKitPlatform
vaf project create app-module --name SilKitPlatform --namespace NsApplicationUnit::NsSilKitPlatform --project-dir .
cd ./src/application_modules/sil_kit_platform/
vaf project import --input-file "$PROJECT_PATH"/Interfaces/export/Interfaces.json --model-dir model
cp "$DEMO_TEST_APP_SRC_PATH"/model/sil_kit_platform.py ./model/
vaf project generate --mode prj --project-dir . --type-variant std --skip-make-preset

# Integration Project Configuration
cd "$PROJECT_PATH"/AdasSilKitPlatform
cp "$DEMO_TEST_APP_SRC_PATH"/model/adas_sil_kit_platform.py ./model/vaf/
vaf project generate --mode ALL --project-dir . --type-variant std
# Files must be copied after the latest project generate
cp -r "$DEMO_TEST_APP_SRC_PATH"/src/sil_kit_platform/sil_kit_platform.h ./src/application_modules/sil_kit_platform/implementation/include/nsapplicationunit/nssilkitplatform/
cp -r "$DEMO_TEST_APP_SRC_PATH"/src/sil_kit_platform/sil_kit_platform.cpp ./src/application_modules/sil_kit_platform/implementation/src/
vaf make install
