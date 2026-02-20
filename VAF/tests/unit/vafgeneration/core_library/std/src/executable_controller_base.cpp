/*!********************************************************************************************************************
 *  COPYRIGHT
 *  -------------------------------------------------------------------------------------------------------------------
 *  \verbatim
 *  Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
 *  SPDX-License-Identifier: Apache-2.0
 *  \endverbatim
 *  -------------------------------------------------------------------------------------------------------------------
 *  FILE DESCRIPTION
 *  -----------------------------------------------------------------------------------------------------------------*/
/*!        \file  executable_controller_base.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "vaf/executable_controller_base.h"
#include <algorithm>
#include <csignal>
#include "vaf/output_sync_stream.h"
#include <memory>
#include <thread>
#include <utility>
#include "vaf/controller_interface.h"
#include "vaf/module_states.h"
#include "vaf/user_controller_interface.h"

namespace vaf {

ExecutableControllerBase::ExecutableControllerBase()
    : signal_handling_init_{[this]() {
        InitializeSignalHandling();
        return 1;
      }()}, // InitializeSignalHandling must be called before the runtime is created
      runtime_{},
      shutdown_requested_{false},
      logger_{vaf::CreateLogger("ECB", "ExecutableControllerBase")},
      modules_{},
      user_controller_{CreateUserController()},
      signal_handler_thread_{} {}

void ExecutableControllerBase::Run(bool use_exec_mgr) noexcept { Run(0, nullptr, use_exec_mgr); }

void ExecutableControllerBase::Run(int /*argc*/, char** /*argv*/, bool use_exec_mgr) noexcept {
  use_execution_mgr_ = use_exec_mgr;

  InitializeSignalHandling();

  user_controller_->PreInitialize();
  DoInitialize();
  user_controller_->PostInitialize();
  user_controller_->PreStart();
  DoStart();
  user_controller_->PostStart();

  while (!IsShutdownRequested()) {
    std::this_thread::sleep_for(std::chrono::milliseconds{100}); // TODO magic number
    StartModules();
    CheckStartingModules();
  }

  user_controller_->PreShutdown();
  DoShutdown();
  user_controller_->PostShutdown();
}

void ExecutableControllerBase::InitiateShutdown() noexcept { shutdown_requested_ = true; }

void ExecutableControllerBase::RegisterModule(std::shared_ptr<vaf::ControlInterface> module) {
  modules_.emplace_back(module->GetName(), std::move(module), module->GetDependencies());
}

void ExecutableControllerBase::ReportOperationalOfModule(vaf::String name) {
  ChangeStateOfModule(name, ModuleStates::kOperational);
}

void ExecutableControllerBase::SkipStartingOfModule(vaf::String name) {
  ChangeStateOfModule(name, ModuleStates::kNotOperational);
}

void ExecutableControllerBase::ReportErrorOfModule(const vaf::Error& error, vaf::String name, bool critical) {
  user_controller_->OnError(error, name, critical);
  if (critical) {
    ChangeStateOfModule(name, ModuleStates::kNotOperational);
  }

  for (ModuleContainer& module: modules_) {
    if (std::find(module.dependencies_.begin(), module.dependencies_.end(), name) != module.dependencies_.end()) {
      module.module_->OnError(error);
    }
  }
}

void ExecutableControllerBase::ChangeStateOfModule(vaf::String name, ModuleStates state) {
  vaf::OutputSyncStream{} << "ExecutableControllerBase::ChangeStateOfModule: name " << name
            << " state: " << ModuleStateToString(state) << std::endl;

  auto module_pos = std::find_if(modules_.begin(), modules_.end(), [&name](ModuleContainer& m) {
    return m.name_ == name;
  });

  if (module_pos == modules_.end()) {
    vaf::OutputSyncStream{std::cerr} << "ExecutableControllerBase::ChangeStateOfModule: Unknown module: " << name << std::endl;
    std::abort();
  }

  ModuleStates current_state{module_pos->state_};
  module_pos->state_ = state;

  switch (state) {
    case ModuleStates::kNotInitialized:
      vaf::OutputSyncStream{std::cerr} << "ExecutableControllerBase: Invalid state transition for module " << name << " from "
                << ModuleStateToString(current_state) << " to kNotInitialized\n";
      std::abort();
      break;
    case ModuleStates::kNotOperational:
      if (current_state == ModuleStates::kNotInitialized) {
        module_pos->module_->Init();
      } else {
        StopEventHandlersForModule(module_pos->name_, module_pos->dependencies_);
        module_pos->module_->StopExecutor();
        module_pos->module_->Stop();
      }
      break;
    case ModuleStates::kStarting:
      module_pos->starting_counter_ = 0;
      module_pos->module_->Start();
      module_pos->module_->StartExecutor();
      break;
    case ModuleStates::kOperational:
      StartEventHandlersForModule(module_pos->name_, module_pos->dependencies_);
      break;
    case ModuleStates::kShutdown:
      module_pos->module_->DeInit();
      break;
  }
}

void ExecutableControllerBase::StartModules() {
  auto canStart = [this](ModuleContainer& module) {
    return std::all_of(module.dependencies_.begin(), module.dependencies_.end(), [this](const vaf::String& dependency) {
      for (size_t i = 0; i < modules_.size(); ++i) {
        if (modules_[i].name_ == dependency) {
          if (modules_[i].state_ == ModuleStates::kOperational) {
            return true;
          }
          break;
        }
      }
      return false;
    });
  };

  for (ModuleContainer& module: modules_) {
    if (module.state_ == ModuleStates::kNotOperational) {
      if (canStart(module)) {
        ChangeStateOfModule(module.name_, ModuleStates::kStarting);
      }
    }
  }
}

void ExecutableControllerBase::StartEventHandlersForModule(const vaf::String& module_name,
                                                           const vaf::Vector<vaf::String>& dependencies) {
  for (const vaf::String& dependency: dependencies) {
    auto dependency_pos{std::find_if(modules_.begin(), modules_.end(), [&dependency](ModuleContainer& module) {
      return module.name_ == dependency;
    })};

    dependency_pos->module_->StartEventHandlerForModule(module_name);
  }
}

void ExecutableControllerBase::StopEventHandlersForModule(const vaf::String& module_name,
                                                          const vaf::Vector<vaf::String>& dependencies) {
  for (const vaf::String& dependency: dependencies) {
    auto dependency_pos{std::find_if(modules_.begin(), modules_.end(), [&dependency](ModuleContainer& module) {
      return module.name_ == dependency;
    })};

    dependency_pos->module_->StopEventHandlerForModule(module_name);
  }
}

void ExecutableControllerBase::CheckStartingModules() {
  for (ModuleContainer& module: modules_) {
    if (module.state_ == ModuleStates::kStarting) {
      module.starting_counter_ += 1;
      if (module.starting_counter_ > 3000) {  // TODO: magic number must be replaced with user configuration
        vaf::OutputSyncStream{} << "Module " << module.name_ << " violated its startup time limit\n";
        ChangeStateOfModule(module.name_, ModuleStates::kNotOperational);
      }
    }
  }
}

void ExecutableControllerBase::DoInitialize() {
  SetupExecutionManager();
  signal_handler_thread_ = std::thread{&ExecutableControllerBase::SignalHandlerThread, this};

  for (ModuleContainer& module: modules_) {
    ChangeStateOfModule(module.name_, ModuleStates::kNotOperational);
  }
}

void ExecutableControllerBase::DoStart() {
  for (ModuleContainer& module: modules_) {
    if (module.dependencies_.empty()) {
      ChangeStateOfModule(module.name_, ModuleStates::kStarting);
    }
  }
}

void ExecutableControllerBase::DoShutdown() {
  for (auto iterator = modules_.rbegin(); iterator != modules_.rend(); ++iterator) {
    ChangeStateOfModule(iterator->name_, ModuleStates::kNotOperational);
  }
  for (auto iterator = modules_.rbegin(); iterator != modules_.rend(); ++iterator) {
    ChangeStateOfModule(iterator->name_, ModuleStates::kShutdown);
  }
  ReportStateToExecutionManager(false);
  signal_handler_thread_.join();
}

void ExecutableControllerBase::InitializeSignalHandling() noexcept {
  bool success{true};
  sigset_t signals;

  // Block all signals except the SIGABRT, SIGBUS, SIGFPE, SIGILL, SIGSEGV
  // signals because blocking them will lead to undefined behavior. Their
  // default handling shall not be changed (dependent on underlying POSIX
  // environment, usually process is killed and a dump file is written). Signal
  // mask will be inherited by subsequent threads.

  success = success && (0 == sigfillset(&signals));
  success = success && (0 == sigdelset(&signals, SIGABRT));
  success = success && (0 == sigdelset(&signals, SIGBUS));
  success = success && (0 == sigdelset(&signals, SIGFPE));
  success = success && (0 == sigdelset(&signals, SIGILL));
  success = success && (0 == sigdelset(&signals, SIGSEGV));
  success = success && (0 == pthread_sigmask(SIG_SETMASK, &signals, nullptr));

  if (!success) {
    logger_.LogFatal() << "InitializeSignalHandling failed.";
    std::abort();
  }
}

void ExecutableControllerBase::SignalHandlerThread() {
  sigset_t signal_set;

  if (0 != sigemptyset(&signal_set)) {
    logger_.LogFatal() << "Could not empty signal set.";
    std::abort();
  }

  if (0 != sigaddset(&signal_set, SIGTERM)) {
    logger_.LogFatal() << "Cannot add signal to signalset: SIGTERM";
    std::abort();
  }

  if (0 != sigaddset(&signal_set, SIGINT)) {
    logger_.LogFatal() << "Cannot add signal to signalset: SIGINT";
    std::abort();
  }

  // Loop until SIGTERM or SIGINT signal received
  int sig{-1};

  do {
    if (0 != sigwait(&signal_set, &sig)) {
      logger_.LogFatal() << "Called sigwait() with invalid signalset.";
      std::abort();
    }
    logger_.LogInfo() << "Received signal: " << sig << ".";

    if ((sig == SIGTERM) || (sig == SIGINT)) {
      logger_.LogInfo() << "Received SIGTERM or SIGINT, requesting application shutdown.";
      if (!shutdown_requested_) {
        // Request application exit. (SignalHandler initiate the shutdown!)
        shutdown_requested_ = true;
      }
    }
  } while (!shutdown_requested_);
}

bool ExecutableControllerBase::IsShutdownRequested() { return shutdown_requested_; }

void ExecutableControllerBase::SetupExecutionManager() {
#if 0
  if (use_execution_mgr_) {
    app_client_ = std::make_unique<ApplicationClient>();
  }
#endif
}

void ExecutableControllerBase::ReportStateToExecutionManager(bool is_running) {
#if 0
  if (app_client_ != nullptr) {
    if (is_running) {
      app_client_->ReportApplicationState(ApplicationState::kRunning);
    } else {
      app_client_->ReportApplicationState(ApplicationState::kTerminating);
    }
  }
#endif
}

}  // namespace vaf
