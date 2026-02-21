# ADAS demo, app-centric scenario using SIL Kit

This ADAS demo leverages an app-centric workflow using the **Vehicle Application Framework (VAF)**
with SilKit. The setup focuses on developing applications independently from the platform. The
applications are then connected to a platform using an automated generation process, which
eliminates the need for platform-specific design and relies on preset configurations for seamless
integration. This approach is ideal for rapid prototyping, facilitating quick development, and
testing iterations.

The following **design of the internal architecture** is used for the ADAS example. The development
starts with creating an architecture of the ADAS application using application modules. Within an
executable two application modules - sensor fusion and collision detection - will be used. The
collision detection receives the object detection list from the sensor fusion application module.
The sensor fusion tasks consume the left and right camera's ImageService, the VelocityService and
the SteeringAngleService. From this information, the object detection list is prepared and send to
the collision detection application module. The collision detection application module then commands
the the brake service accordingly. A high-level illustration of this setup is given below:

![adas_start](../figures/silkit.drawio.svg)

For the architecture, the following interfaces are defined:

| Service: BrakeService                                | Service: ImageService                           |
| ---------------------------------------------------- | ----------------------------------------------- |
| DataElement: brake_action                            | DataElement: camera_image                       |
| DataElement: brake_summand_coefficient_FieldNotifier | DataElement: image_scaling_factor_FieldNotifier |
| Operation: brake_summand_coefficient_FieldGetter     | Operation: image_scaling_factor_FieldGetter     |
| Operation: brake_summand_coefficient_FieldSetter     | Operation: image_scaling_factor_FieldSetter     |
| Operation: SumTwoSummands                            | Operation: GetImageSize                         |

| Service: Object Detection List (Sensor Fusion) |
| ---------------------------------------------- |
| DataElement: object_detection_list             |

| Service: SteeringAngleService | Service: VelocityService  |
| ------------------------------ | ------------------------- |
| DataElement: steering_angle    | DataElement: car_velocity |

These interfaces are defined completely by the Configuration as Code (CaC) interface of the VAF.

## Project setup
Make sure you have built the VAF Docker container image as described in the getting started section
of the top-level [README](../../README.md).

With the image ready, open a terminal window, run the container, and create a new VAF workspace at a
location of your choice as follows:
```bash
docker run -it --rm -v$PWD:$PWD -w$PWD vaf:latest /bin/bash

cd <your-working-directory>

vaf workspace init

Enter your workspace name: <your-workspace-name>
? Enter the directory to store your workspace in .
bash
```

Next, switch folders to this workspace. Ideally, you open this folder directly in VS Code and select
`Reopen folder in Container`.

## AdasExecutable (app)

To develop our ADAS application executable, the first step is to define the interfaces as described
above. Afterwards, these interfaces are used to create and implement the application modules. In a
final CaC step, the application module's external interfaces are connected to SilKit. The final
result will be an executable, which uses the proposed internal architecture and communicates to the
outside world using SilKit.

### Definition of interfaces

At first, internal and external interfaces and data types for the application modules need to be
defined. For that, a **VAF interface project** can be used.

To get started, create a new interface project using the VAF command line tool:

``` bash
vaf project init interface
Enter the name of the project: Interfaces
Enter the directory to store your project in: .
```

Next, switch to the just created project directory.

``` bash
cd Interfaces
```

Next step is the configuration of the interface definition. For that, open the template file
`interfaces.py` within the newly created interface project. We now add the required interfaces:

``` python
# Brake Service
brake_pressure = vafpy.datatypes.Struct(name="BrakePressure", namespace="datatypes")
brake_pressure.add_subelement(name="timestamp", datatype=BaseTypes.UINT64_T)
brake_pressure.add_subelement(name="value", datatype=BaseTypes.UINT8_T)

brake_service = vafpy.ModuleInterface(name="BrakeService", namespace="af::adas_demo_app::services")
brake_service.add_data_element(name="brake_action", datatype=brake_pressure)
brake_service.add_data_element(name="brake_summand_coefficient_FieldNotifier", datatype=BaseTypes.UINT64_T)
brake_service.add_operation(name="brake_summand_coefficient_FieldGetter", out_parameter={"data": BaseTypes.UINT64_T})
brake_service.add_operation(name="brake_summand_coefficient_FieldSetter", in_parameter={"data": BaseTypes.UINT64_T})
brake_service.add_operation(
    name="SumTwoSummands",
    in_parameter={"summand_one": BaseTypes.UINT16_T, "summand_two": BaseTypes.UINT16_T},
    out_parameter={"sum": BaseTypes.UINT16_T},
)


# Object Detection List
od_struct = vafpy.datatypes.Struct(name="ObjectDetection", namespace="adas::interfaces")
od_struct.add_subelement(name="x", datatype=BaseTypes.UINT64_T)
od_struct.add_subelement(name="y", datatype=BaseTypes.UINT64_T)
od_struct.add_subelement(name="z", datatype=BaseTypes.UINT64_T)

od_list = vafpy.datatypes.Vector(
    name="ObjectDetectionList",
    namespace="adas::interfaces",
    datatype=od_struct,
)

od_interface = vafpy.ModuleInterface(
    name="ObjectDetectionListInterface",
    namespace="nsapplicationunit::nsmoduleinterface::nsobjectdetectionlist",
)
od_interface.add_data_element(name="object_detection_list", datatype=od_list)


# ImageService
uint8_vector_307200 = vafpy.datatypes.Vector(
    name="UInt8Vector", namespace="datatypes", datatype=BaseTypes.UINT8_T
)

image = vafpy.datatypes.Struct(name="Image", namespace="datatypes")
image.add_subelement(name="timestamp", datatype=BaseTypes.UINT64_T)
image.add_subelement(name="height", datatype=BaseTypes.UINT16_T)
image.add_subelement(name="width", datatype=BaseTypes.UINT16_T)
image.add_subelement(name="R", datatype=uint8_vector_307200)
image.add_subelement(name="G", datatype=uint8_vector_307200)
image.add_subelement(name="B", datatype=uint8_vector_307200)

image_service = vafpy.ModuleInterface(name="ImageService", namespace="af::adas_demo_app::services")
image_service.add_data_element(name="camera_image", datatype=image)
image_service.add_data_element(name="image_scaling_factor_FieldNotifier", datatype=BaseTypes.UINT64_T)
image_service.add_operation(name="image_scaling_factor_FieldGetter", out_parameter={"data": BaseTypes.UINT64_T})
image_service.add_operation(name="image_scaling_factor_FieldSetter", in_parameter={"data": BaseTypes.UINT64_T})
image_service.add_operation(
    name="GetImageSize", out_parameter={"width": BaseTypes.UINT16_T, "height": BaseTypes.UINT16_T}
)


# VelocityService
velocity = vafpy.datatypes.Struct(name="Velocity", namespace="datatypes")
velocity.add_subelement(name="timestamp", datatype=BaseTypes.UINT64_T)
velocity.add_subelement(name="value", datatype=BaseTypes.UINT16_T)

velocity_service = vafpy.ModuleInterface(name="VelocityService", namespace="af::adas_demo_app::services")
velocity_service.add_data_element(name="car_velocity", datatype=velocity)


# Steering Angle
steering_angle = vafpy.datatypes.Struct(name="SteeringAngle", namespace="datatypes")
steering_angle.add_subelement(name="timestamp", datatype=BaseTypes.UINT64_T)
steering_angle.add_subelement(name="value", datatype=BaseTypes.UINT16_T)

steering_angle_service = vafpy.ModuleInterface(name="SteeringAngleService", namespace="af::adas_demo_app::services")
steering_angle_service.add_data_element(name="steering_angle", datatype=steering_angle)
```

Once complete, the configuration needs to be exported to JSON by using the following command:

``` bash
vaf model generate
```

The exported JSON file gets stored to the subdirectory `./export` by default, along with its CaC
support file for later use in an application module project.

### Configuration and implementation of app-modules

Application modules are supposed to be self-contained. The corresponding **VAF app-module project**
allows to configure, implement, test, and maintain it stand-alone and thus separate from the later
integration step. This further allows to use app-modules in different integration projects.

For the ADAS executable, we need the two application modules for Sensor Fusion and Collision
Detection.

#### Preparing the Sensor Fusion application module

``` bash
vaf project init app-module
Enter the name of the app-module: SensorFusion
Enter the namespace of the app-module: NsApplicationUnit::NsSensorFusion

cd SensorFusion
```

The above-created data exchange file from the interface project needs to be imported to make the
model elements from there accessible in the app-module project. Use the following command for that:

```bash
vaf project import
Enter the path to the exported VAF model JSON file: ../Interfaces/export/Interfaces.json
```

Next step is the configuration of the application module. For that, open the file `./model/sensor_fusion.py`. To
complete the import from the interface project, uncomment line #6:

``` python
from .imported_models import *
```

The configuration of the application module is done completely in this Configuration as Code file.
According to the illustration above, `SensorFusion` is supposed to connected to the left/right
camera `ImageService` and therefore needs a corresponding consumer interface. Likewise, consumer
interfaces for the SteeringAngleService and VelocityService are required. For communication with
`collision_detection` it acts as provider of the earlier defined `ObjectDetectionListInterface`. The
`collision_detection` acts as consumer counterpart for the `ObjectDetectionListInterface` and
towards the platform-side, needs a provider interface for `BrakeService`.

The configuration for `sensor_fusion`:

``` python
sensor_fusion = vafpy.ApplicationModule(name="SensorFusion", namespace="NsApplicationUnit::NsSensorFusion")

sensor_fusion.add_provided_interface("ObjectDetectionListModule", interfaces.Nsapplicationunit.Nsmoduleinterface.Nsobjectdetectionlist.object_detection_list_interface)
sensor_fusion.add_consumed_interface("ImageServiceConsumer1", interfaces.Af.AdasDemoApp.Services.image_service)
sensor_fusion.add_consumed_interface("ImageServiceConsumer2", interfaces.Af.AdasDemoApp.Services.image_service)
sensor_fusion.add_consumed_interface("SteeringAngleServiceConsumer", interfaces.Af.AdasDemoApp.Services.steering_angle_service)
sensor_fusion.add_consumed_interface("VelocityServiceConsumer", interfaces.Af.AdasDemoApp.Services.velocity_service)

p_200ms = timedelta(milliseconds=200)
step1 = vafpy.Task(name="Step1", period=p_200ms, preferred_offset=0)
step2 = vafpy.Task(name="Step2", period=p_200ms, preferred_offset=0)
step3 = vafpy.Task(name="Step3", period=p_200ms, preferred_offset=0)

sensor_fusion.add_task(task=step1)
sensor_fusion.add_task_chain(tasks=[step2, step3], run_after=[step1])
sensor_fusion.add_task(vafpy.Task(name="Step4", period=p_200ms, preferred_offset=0, run_after=[step1]))
```

#### Preparing the Collision Detection application module

Using the above mentioned workflow you can prepare the collision detection application module using:

``` bash
vaf project init app-module
Enter the name of the app-module: CollisionDetection
Enter the namespace of the app-module: NsApplicationUnit::NsCollisionDetection 
```

Import from the interface project as previously done for the SensorFusion application module:

```bash
vaf project import
Enter the path to the exported VAF model JSON file: ../Interfaces/export/Interfaces.json
```

The configuration for `collision_detection`:

``` python
collision_detection = vafpy.ApplicationModule(
    name="CollisionDetection", namespace="NsApplicationUnit::NsCollisionDetection"
)

collision_detection.add_provided_interface("BrakeServiceProvider", interfaces.Af.AdasDemoApp.Services.brake_service)
collision_detection.add_consumed_interface("ObjectDetectionListModule", interfaces.Nsapplicationunit.Nsmoduleinterface.Nsobjectdetectionlist.object_detection_list_interface)

periodic_task = vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=200))
collision_detection.add_task(task=periodic_task)
```

#### Steps that apply for both application module projects

Once complete, the next step is the code generation:

``` bash
vaf project generate
```

The generated code can be divided into read-write and read-only parts. Former gets generated to the
`./implementation` folder. This is user space, where the framework only provides implementation
stubs for the developer to start. In case of re-generation, a 3-way merge strategy based on
git-merge is applied to the files in this location. The read-only parts get generated to `./src-gen`
and `./test-gen`. Those folders are under control of the framework. Any user modification will be
overwritten in case of re-generation.

The entry file for the user to add own code is located in `./implementation/src/sensor_fusion.cpp`
and `./implementation/src/collision_detection.cpp` respectively. Corresponding headers are located
in `./implementation/include/` subdirectories. Some sample code for reference is shipped as part of
the container and located in: `/opt/vaf/Demo/SilKit/app/src`.

The application module project is also ready to be built as library. To do so and in order to check
if added code passes the compiler checks, execute the following two steps. First, start preset to
prepare the build step, which includes CMake preset and Conan cache setup. Second, trigger the
CMake-based build process. On the command line run:

``` bash
vaf make preset
vaf make build
```

### Unit testing of app-modules

The Vehicle Application Framework provides means for unit testing. Test mocks for Googletest are
generated to `./test-gen` accordingly and allow independent first-level testing of application
modules. Custom test code can be added in the corresponding `tests.cpp` file in the
`./implementation/test/unittest` folder.

> **ℹ️ Note**  
> The build step of these unit tests is enabled by default. To deactivate it, use the following commands:
>
> ``` bash
> vaf make preset -d -DVAF_BUILD_TESTS=OFF
> vaf make build
> ```

The resulting test binaries get stored in `./build/Release/bin` for execution.

### Executable integration

Final integration of all application modules is done using a **VAF integration project**. This is
where the whole application, which potentially consists of multiple executables, gets integrated. In
practice, app-modules and platform modules, as provided by the framework, get instantiated and
connected. The complete picture of the AdasExecutable is illustrated below.

To start a new integration project, execute the following steps:

``` bash
vaf project init integration
Enter your project name: AdasDemoSilKit

cd AdasDemoSilKit
```

To get started, all relevant application-module projects need to be imported:

```bash
vaf project import
Enter the path to the application module project to be imported: ../SensorFusion/

vaf project import
Enter the path to the application module project to be imported: ../CollisionDetection/
```

The import command adds new files to `./model/vaf/application_modules`. This includes relevant path
information but, most and foremost, the importer and CaC-support artifacts, which make the model
elements from the app-module accessible for the configuration in the integration project.

For this, the next step is the configuration of the integration project in `./model/vaf/adas_demo_sil_kit.py`.

At first, we need to create the executable for the ADAS demo

```python
adas_demo_app = Executable("adas_demo_app", timedelta(milliseconds=20))
```

Then we add the application modules for Sensor Fusion and Collision Detection, including scheduling
information for the execution of the application module tasks.

```python
b_10ms = timedelta(milliseconds=10)
adas_demo_app.add_application_module(
    SensorFusion,
    [
        (Instances.SensorFusion.Tasks.Step1, b_10ms, 0),
        (Instances.SensorFusion.Tasks.Step2, b_10ms, 0),
        (Instances.SensorFusion.Tasks.Step3, b_10ms, 0),
        (Instances.SensorFusion.Tasks.Step4, b_10ms, 0),
    ],
)
adas_demo_app.add_application_module(
    CollisionDetection, [(Instances.CollisionDetection.Tasks.PeriodicTask, timedelta(milliseconds=1), 1)]
)
```

The two app-module instances now can be connected. Among each other, on the one hand, and with
SilKit, on the other hand. The below configuration code snippet details the part for
executable-internal communication in this example project:

``` python
adas_demo_app.connect_interfaces(
    SensorFusion,
    Instances.SensorFusion.ProvidedInterfaces.ObjectDetectionListModule,
    CollisionDetection,
    Instances.CollisionDetection.ConsumedInterfaces.ObjectDetectionListModule,
)
```

The communication with a lower-layer platform is abstracted by platform modules. They deal with the
platform API towards the lower layer, i.e. the middleware stack, and with the VAF API towards the
upper, the application layer. The connection between application and platform modules is configured
as follows:

``` python
adas_demo_app.connect_consumed_interface_to_silkit(
    SensorFusion,
    Instances.SensorFusion.ConsumedInterfaces.ImageServiceConsumer1,
    "Silkit_ImageService1",
)
adas_demo_app.connect_consumed_interface_to_silkit(
    SensorFusion,
    Instances.SensorFusion.ConsumedInterfaces.ImageServiceConsumer2,
    "Silkit_ImageService2",
)
adas_demo_app.connect_consumed_interface_to_silkit(
    SensorFusion,
    Instances.SensorFusion.ConsumedInterfaces.SteeringAngleServiceConsumer,
    "Silkit_SteeringAngleService",
)
adas_demo_app.connect_consumed_interface_to_silkit(
    SensorFusion,
    Instances.SensorFusion.ConsumedInterfaces.VelocityServiceConsumer,
    "Silkit_VelocityService",
)

adas_demo_app.connect_provided_interface_to_silkit(
    CollisionDetection,
    Instances.CollisionDetection.ProvidedInterfaces.BrakeServiceProvider,
    "Silkit_BrakeService",
)
```

With this step done, the integration project configuration part is complete. The next step is model
and code generation using:

``` bash
vaf project generate
```

Using `--mode prj` or `--mode all` further allows to set the scope of this command to either, the
current integration project only (prj), or to this and all related sub-projects (all).

To complete the integration project, build and finally installation are missing:

``` bash
vaf make build
vaf make install
```

The final executable for execution is stored in `./build/Release/install/opt`.

## AdasPlatform (test-app)

In order to run the AdasExecutable application, a counterpart is required that mimics the platform
side and consumes/provides the necessary services as expected from there. This counterpart can be
built with the same workflow as described above for the AdasExecutable.

>**ℹ️ Note**  
> The AdasPlatform executable in the example contains one app-module only (SilKitPlatform). The
> app-module project can also be created directly within the integration project instead of
> importing it. To do so, use `vaf project create app-module`. Instead of being linked to the
> integration project, the app-module will live as local copy in `./src/application_modules`.

The VAF configuration and source code samples are provided in:
`/opt/vaf/Demo/SilKit/test-app`.

## Running the ADAS application

Open three terminal sessions to get started. One for the AdasExecutable process (app), one for the
counterpart (test-app), and one for the SIL Kit registry.

>**ℹ️ Note**  
> It is important to run all sessions (processes) on the same machine or within the same container.
> The compiled applications have no dependencies on the devcontainer and can be run on your host
> machine. Running inside a container is discouraged, as the container requires special network
> configuration/permissions to set up the loopback interface.

In the first terminal, start the SIL Kit registry located in: `./build/Release/install/opt/silkit`
with the following command:
``` bash
./bin/sil-kit-registry --listen-uri "silkit://localhost:8501"
```

The given URI needs to match with the one used by the VAF executables. For that reason, its value is
configurable via environment variable and parsed at runtime. If not defined, the default value
`silkit://localhost:8501` is used. If you want to use your custom URI, just define a value for the
environment variable `SILKIT_REGISTRY_URI` as follows:
``` bash
export SILKIT_REGISTRY_URI="silkit://hostofmylife:7727"
```

Finally, launch both executables, each from its own terminal window. It is important to change the
directory to the base folder of the installed application. Otherwise, relevant configuration files
cannot be found during startup.

For the AdasExecutable (app):
``` bash
cd ./build/Release/install/opt/adas_demo_app
./bin/adas_demo_app
```

And similar for the AdasPlatform (test-app).

## Running the ADAS application

Open three terminal sessions to get started. One for the AdasExecutable process (app), one for the
counterpart (test-app), and one for the SilKit registry.

>**ℹ️ Note**  
> It is important to run all sessions (processes) on the same machine or within the same container.
> The compiled applications have no dependencies on the devcontainer and can be run on your host
> machine. Running inside a container is discouraged, as the container requires special network
> configuration/permissions to set up the loopback interface.

In the first terminal, start the SilKit registry located in: `./build/Release/install/opt/silkit`.
The registry is configurable via environment variable `SILKIT_REGISTRY_URI`. By default, the
registry uri would be `silkit://localhost:8501`. 
``` bash
export SILKIT_REGISTRY_URI="silkit://hostofmylife:7727"
```

Then launch both executables, located in the corresponding `./build/Release/install/opt` directories
of your `AdasDemoSilKit` and `AdasSilKitPlatform` projects.
