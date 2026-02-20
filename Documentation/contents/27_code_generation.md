# Code generation (vafgeneration)

The Vehicle Application Framework (VAF) relies heavily on generated code and configuration files.
This section lists all the generators and the corresponding generated files. They are implemented in
the Python package `vafgeneration`.

## Convenience Modules

This section contains all Python modules that do not directly generate files, but provide
convenience functionality to either the caller or the code generator.

### generation

Contains helper functions relevant to the following generator modules.

### vaf_generate_application_module

Module that calls the generators needed for application module projects.

### vaf_generate_common

Contains helper functions relevant to the following generator modules. Implements the 3-way merge
strategy.

### vaf_generate_project

Module that calls the generators needed for integration projects.

## Code generators

Modules that actually generate code and similar required files are listed below.

### vaf_application_communication

Generates C++ source code and CMake files for the communication module, which allows
executable-internal communication between application modules.

Generated files:

``` text
<project>/src-gen/libs/platform_vaf
├── <module_name>
|   ├── include/application_communication
|   |   └── <interface_name>.h
|   ├── src/application_communication
|   |   └── <interface_name>.cpp
│   └── CMakeLists.txt
└── CMakeLists.txt
```

### vaf_application_module

Generates C++ source code and CMake files for application module projects. This includes base
classes as well as business logic and unit test stubs. Each module is built as a separate library.

Generated files:

``` text
<project>
├── src-gen/libs/application_module_base
│   ├── <module_name>
│   |   ├── src/<name>/<space>
│   |   |   └── <module_name>_base.cpp
│   |   ├── include/<name>/<space>
│   |   |   └── <module_name>_base.h
│   |   └── CMakeLists.txt
│   └── CMakeLists.txt
├── src/application_modules/<module_name>/implementation
│   ├── src
│   |   └── <module_name>.cpp
│   ├── include/<name>/<space>
│   |   └── <module_name>.h
│   ├── test
│   |   ├── unittest
│   |   |   ├── src
|   │   |   |   ├── main.cpp
|   │   |   |   ├── test.cpp
|   │   |   |   └── <name>/<space>
|   |   │   |   |   └── <module_name>_base.cpp
│   |   |   ├── include/<name>/<space>
|   │   |   |   └── <module_name>_base.h
│   |   |   └── CMakeLists.txt
│   |   └── CMakeLists.txt
|   └── CMakeLists.txt
└── test-gen/mocks/interfaces
    ├── include/<name>/<space>
    |   └── <interface_name>_mock.h
    └── CMakeLists.txt
```

### vaf_cac_support

Generates a Python file containing classes and attributes that allow imported model artifacts to be
used on Configuration as Code (CaC) level. This includes the VSS support as well as interface
project exports.

Generated files:

``` text
<project>
├── model
│   └── vss.py
└── export
    └── interfaces.py
```

### vaf_cmake_common

This generator is responsible for creating CMake files that add subdirectories as well as the CMake
file for the `vaf_data_types` target.

Generated files:

``` text
<project>
├── src-gen
|   ├── executables
|   │   └── CMakeLists.txt
|   ├── libs
|   |   ├── data_types
|   |   │   └── CMakeLists.txt
|   │   └── CMakeLists.txt
│   └── CMakeLists.txt
├── src
|   ├── executables
|   │   └── CMakeLists.txt
│   └── CMakeLists.txt
└── test-gen
    ├── mocks
    │   └── CMakeLists.txt
    └── CMakeLists.txt
```

### vaf_conan

Based on the dependencies used in the project, a Conan dependency list with the required Conan
packages is generated. This generator is executed for app-module and integration projects.

Generated files:

``` text
<project>/src-gen
└── conan_deps.list
```

### vaf_controller

Generates source code and CMake files for the controller and executable entry point. Also creates
stubs for the user controller.

Generated files:

``` text
<project>
├── src-gen/executables/<executable_name>
|   ├── include
|   |   └── executable_controller
|   |       └── executable_controller.cpp
|   ├── src
|   |   ├── executable_controller
|   |   |   └── executable_controller.cpp
|   |   └── main.cpp
│   └── CMakeLists.txt
└── src/executables/<executable_name>
    ├── include
    |   └── user_controller.h
    ├── src
    |   └── user_controller.cpp
    └── CMakeLists.txt
```

### vaf_interface

Generates header and CMake files to support the module interfaces configured in CaC.

Generated files:

``` text
<project>
├── src-gen/libs/interfaces
│   ├── include/<name>/<space>
│   |   ├── <interface_name>.h
│   |   └── internal/methods
|   |       └── <method_name>.h
│   └── CMakeLists.txt
└── test-gen/mocks/interfaces
    ├── include/<name>/<space>
    |   └── <interface_name>_mock.h
    └── CMakeLists.txt
```

### vaf_protobuf_serdes

Creates `.proto` files for the configured datatypes and platform interfaces. These are used to
serialize data when using SIL Kit as communication platform. It also provides helper functions
(transformers) to easily convert between VAF datatypes and protobuf.

Generated files:

``` text
<project>/src-gen/libs/protobuf_serdes
├── proto
│   ├── protobuf_<namespace>.proto
│   └── CMakeLists.txt
└── transformer
    ├── include/protobuf
    |   └── <name>/<space>
    |       └── protobuf_transformer.h
    └── CMakeLists.txt
```

### vaf_silkit

Generates the C++ source code and CMake files for platform provider and consumer modules that
communicate with SIL Kit. Each module is built as a separate library. This generator is only used in
integration projects.

Generated files:

``` text
<project>/src-gen/libs/platform_silkit
├── platform_consumer_modules
│   ├── <consumer_module>
│   |   ├── src
│   |   |   └── <consumer_module>.cpp
│   |   ├── include
│   |   |   └── <consumer_module>.h
│   |   └── CMakeLists.txt
│   └── CMakeLists.txt
└── platform_provider_modules
    ├── <provider_module>
    |   ├── src
    |   |   └── <provider_module>.cpp
    |   ├── include
    |   |   └── <provider_module>.h
    |   └── CMakeLists.txt
    └── CMakeLists.txt
```

### vaf_std_data_types

Generates header files for all used VAF datatypes. Uses primitive types and the C++ standard
library.

Generated files:

``` text
<project>/src-gen/libs/datatypes/include/<name>/<space>
└── impl_type_<typename>.h
```
