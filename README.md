# Welcome to the Vehicle Application Framework (VAF)

This project is part of the [Eclipse Automotive API Framework](https://projects.eclipse.org/projects/automotive.autoapiframework).

## Repository contents

- 📂 [.devcontainer](./.devcontainer)  
  VS Code development container configuration file for contributors of this project.
- 📂 [.pre-commit-hooks](./.pre-commit-hooks)  
  Collection of scripts that help to identify simple issues before commits.
- 📂 [.vscode](./.vscode)  
  Tasks, scripts, and settings for easier development in VS Code.
- 📂 [Container](./Container)  
  Dockerfile recipe for the container image that is supposed to be provided to users of the framework.
- 📂 [Demo](./Demo)  
  Several demo projects with sample files that demonstrate the usage of the VAF.
- 📂 [Documentation](./Documentation)  
  The VAF technical documentation.
- 📂 [VAF](./VAF)  
  The actual implementation of the framework. Includes model, Configuration as Code, importers, CLI
  tooling, and code generators.

## Getting started

Please check, which role applies to you and follow the provided instructions to get started...

### Application Framework user

1. Make sure Docker is installed on your machine. Otherwise, please follow the instructions in:
   [Install Docker using the apt
   repository.](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)
2. Optional step if you are working in a corporate environment with a SSL proxy server. Modify 
   the [eclipse.Dockerfile](./Container/eclipse.Dockerfile) in lines 42 ff. and insert your SSL 
   proxy settings.
3. Start the `build.sh` script in the [Container](./Container) folder to create the image.
4. Check out the different example projects that are provided in [Demo](./Demo). Each demo comes
   with a detailed step-by-step tutorial.
5. Start own projects based on the VAF.

In case of feedback do not hesitate to get back to us. Or, even better, become a contributor
yourself and join us on the development of the Vehicle Application Framework!

### Project contributor

To make development easier, a devcontainer is also provided for project contributors. It contains
all the necessary dependencies and development tools to contribute to this project. It includes also
all runtime dependencies to use VAF itself in this container. The dockerfile and the corresponding
devcontainer configuration are located in the [.devcontainer](./.devcontainer) directory.

Please modify the [devcontainer.json](./.devcontainer/devcontainer.json) configuration file in case
you need to mount additional files/folders into the container. At the bottom of the file there are
some samples that can be used as template. In case you work in a corporate environment with a SSL
proxy server, the [Dockerfile](./.devcontainer/Dockerfile) must also be adapted with SSL proxy
settings. To do this, adapt lines 42 ff. according to your requirements.

The project uses `Conan` to manage C++ dependencies. Since there are no prebuilt packages available
in the public Conan center for the used compiler settings, the packages are built as the last step
of the dockerfile. This avoids a long wait when (re-)creating a new container.

>**ℹ️ Note**  
>On first start of the devcontainer it will take a few minutes, depending on your machine, to
>build all the Conan dependencies.

#### Building vaf-cli

The VAF CLI program uses `uv` as build tool. To build VAF and create a virtual environment (venv) in
your container, go to the `./VAF` directory and run:

``` bash
make start
```

This will setup the venv, install the dependencies, and finally add the project as an editable
package so you don't have to re-install every time you make a change. The created virtual
environment should be selected as the Python environment in VS Code to enable IntelliSense. When
working in a terminal window, the virtual environment must be activated. To do this, execute the
following command in the `./VAF` directory:

``` bash
source .venv/bin/activate
```

The VAF supports bash completion. To enable it, activate the virtual environment as described
above. Then execute the following commands:

``` bash
mkdir -p ~/.local/share/bash-completion/completions
_VAF_COMPLETE=bash_source vaf > ~/.local/share/bash-completion/completions/vaf.sh
source ~/.local/share/bash-completion/completions/vaf.sh
```

## Related projects

This project makes use of the following open-source projects:

- [expected by TartanLlama](https://github.com/TartanLlama/expected) available under [CC0 1.0
  Universal License](https://creativecommons.org/publicdomain/zero/1.0/legalcode.txt)
- [Vector SIL Kit](https://github.com/vectorgrp/sil-kit) available under [MIT
  License](https://mit-license.org/)

Other dependencies via Conan include:

- [protobuf v5.27.0](https://github.com/protocolbuffers/protobuf/tree/v5.27.0)
- [gtest v1.13.0](https://github.com/google/googletest/tree/v1.13.0)
- [leveldb v1.23](https://github.com/google/leveldb/v1.23)
