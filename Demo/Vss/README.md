# Vehicle Application Framework - using the COVESA VSS catalog

The following tutorial guides you through an example with the **Vehicle Application Framework
(VAF)** that illustrates how interfaces from the [COVESA Vehicle Signal Specification
(VSS)](https://covesa.global/project/vehicle-signal-specification/) can be derived and used.

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

## Overview
Plan in this demo is to develop one executable with two application modules. The example does not
use a platform for communication, the app-modules only communicate directly. That means, they share
an internal communication channel, which is based on VSS. A high-level illustration of this setup is
given below:

![vss](../figures/vss.drawio.svg)

## Definition of interfaces

First step in this demo is the modeling of interfaces based on datatype and signal descriptions as
imported from a catalogue in VSS format. Those interfaces are later used for data exchange between
the application modules.

Create a new interface project for that purpose using the VAF command line tool:

``` bash
vaf project init interface
Enter the name of the project: VssInterfaces
Enter the directory to store your project in: .
```

Next, switch to the just created project directory.

``` bash
cd VssInterfaces
```

Then, import a VSS data catalogue to the project. The [VSS catalogue as provided on
GitHub](https://github.com/COVESA/vehicle_signal_specification) is provided as JSON file and part of the container. It is located in: `/opt/vaf/Demo/Vss/model/vss/vss.json`.
``` bash
vaf model import vss
Enter the path to the VSS catalogue file in JSON format /opt/vaf/Demo/Vss/model/vss/vss.json
```

Open the template file `vss_interfaces.py` within the newly created interface project. Import the
VSS content from the previous step and define the interfaces for this demo using this input:

``` python
from .vss import *

acceleration_if = vafpy.ModuleInterface(name="Acceleration_If", namespace="demo")
acceleration_if.add_data_element(name="Lateral", datatype=Vss.Vehicle.Acceleration.lateral)
acceleration_if.add_data_element(name="Longitudinal", datatype=Vss.Vehicle.Acceleration.longitudinal)
acceleration_if.add_data_element(name="Vertical", datatype=Vss.Vehicle.Acceleration.vertical)

driver_if = vafpy.ModuleInterface(name="Driver_If", namespace="demo")
driver_if.add_data_element(name="Identifier", datatype=Vss.Vehicle.Driver.identifier)
driver_if.add_data_element(name="IsEyesOnRoad", datatype=Vss.Vehicle.Driver.is_eyes_on_road)
```

Once complete, the configuration needs to be exported to JSON by using the following command:

``` bash
vaf model generate
```

The exported JSON file gets stored to the subdirectory `./export` by default, along with its CaC
support file for later use in application module projects.

Before the next step, switch folders to the workspace again.
``` bash
cd ..
```

## DemoExecutable

Create a new integration project using the VAF command line tool:

``` bash
vaf project init integration
Enter your project name: DemoExecutable
```

Next, switch folders:
``` bash
cd DemoExecutable
```

### Configuration and implementation of app-modules

Add two application modules to the project using:

``` bash
vaf project create app-module
Enter the name of the app-module: VssProvider
Enter the namespace of the app-module: demo

vaf project create app-module
Enter the name of the app-module: VssConsumer
Enter the namespace of the app-module: demo
```

Next, switch folders accordingly:
``` bash
cd src/application_modules/vss_<consumer/provider>
```

Then, import the outcome from the previously completed Interface project.
``` bash
vaf project import
Please provide the path to the exported VAF model JSON file ../../../../VssInterfaces/export/VssInterfaces.json
```

Two new files are added to the `model/imported_models` folder by this command. `VssInterfaces.json`
is the VAF model file in JSON format. `vss_interfaces.py` is the Configuration as Code (CaC)
support, which is needed to access the model artifacts from the Python configuration.

Next step is the configuration of the app-module in `./model/vss_<consumer/provider>.py`. 

To use the just imported content from the previous step, uncomment the following line:
``` python
from .imported_models import *
```

The app-module configuration template already contains the app-module object and a default task. On
top, the interface definitions need to be added.

For the VssConsumer use:
``` python
vss_consumer = vafpy.ApplicationModule(name="VssConsumer", namespace="demo")

vss_consumer.add_consumed_interface("AccelerationConsumer", interface=vss_interfaces.Demo.acceleration_if)
vss_consumer.add_consumed_interface("DriverConsumer", interface=vss_interfaces.Demo.driver_if)

periodic_task = vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=200))
vss_consumer.add_task(task=periodic_task)
```

For the VssProvider use:
``` python
vss_provider = vafpy.ApplicationModule(name="VssProvider", namespace="demo")

vss_provider.add_provided_interface("AccelerationProvider", interface=vss_interfaces.Demo.acceleration_if)
vss_provider.add_provided_interface("DriverProvider", interface=vss_interfaces.Demo.driver_if)

periodic_task = vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=200))
vss_provider.add_task(task=periodic_task)
```

Continue from here with model and code generation:
``` bash
vaf project generate
```

Some sample code for the app-modules is provided for reference in: `/opt/vaf/Demo/Vss/src/vss_<consumer/provider>/src/vss_<consumer/provider>.cpp`.
Feel free to copy it to the generated implementation stubs in: `./implementation/src/vss_<consumer/provider>.cpp`

Finally, check if the app-module library compiles using:
``` bash
vaf make build
```

With this part completed for both, the VssProvider and the VssConsumer, the final integration on
executable-level can be started.

### Executable integration
Back in the integration project, plan is to define one executable with one instance of the
above-created app-modules each. 

Before we can start with the configuration, the changes from the application module projects need to
be updated, such that the configuration is available in the integration project. To do so, use the
following command and select both app-modules from the selection.
``` bash
cd <path-to-integration-project>
vaf model update
```

Continuing with the configuration in `./model/vaf/demo_executable.py`, we first define and configure one
executable as follows:
``` python
executable = Executable("DemoExecutable", timedelta(milliseconds=10))
```

Next, we can directly continue with the step of instantiating and adding app-modules as follows:
``` python
executable.add_application_module(VssProvider, [(Instances.VssProvider.Tasks.PeriodicTask, timedelta(milliseconds=1), 0)])
executable.add_application_module(VssConsumer, [(Instances.VssConsumer.Tasks.PeriodicTask, timedelta(milliseconds=1), 1)])
```

The second parameter, allows the definition of an integration-specific task mapping. This includes
the task period and execution order and allows the integrator to overrule the original settings from
the application module project. In this example, we want the provider to be executed before the consumer.

The two app-modules instances now can be connected as follows:
``` python
executable.connect_interfaces(VssProvider, Instances.VssProvider.ProvidedInterfaces.AccelerationProvider,
                              VssConsumer, Instances.VssConsumer.ConsumedInterfaces.AccelerationConsumer)
executable.connect_interfaces(VssProvider, Instances.VssProvider.ProvidedInterfaces.DriverProvider,
                              VssConsumer, Instances.VssConsumer.ConsumedInterfaces.DriverConsumer)
```

With this, the configuration part in the integration project is complete. Model and integration code
can be generated in one step using:
``` bash
vaf project generate
```

To complete the demo, compilation of the executable binary is missing.
``` bash
vaf make build
vaf make install
```

## Running the application
The binary can now be run from the `./build/Release/install/opt/DemoExecutable` directory. Change
folders and execute:
``` bash
./bin/DemoExecutable
```
