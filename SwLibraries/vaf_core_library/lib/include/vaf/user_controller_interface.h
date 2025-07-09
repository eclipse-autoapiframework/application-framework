#ifndef INCLUDE_VAF_USER_CONTROLLER_H_
#define INCLUDE_VAF_USER_CONTROLLER_H_

#include <memory>
#include "vaf/error_domain.h"

namespace vaf {

class UserControllerInterface {
public:
  virtual ~UserControllerInterface() = default;

  virtual void PreInitialize() = 0;
  virtual void PostInitialize() = 0;
  virtual void PreStart() = 0;
  virtual void PostStart() = 0;
  virtual void PreShutdown() = 0;
  virtual void PostShutdown() = 0;

  virtual void OnError(vaf::Error error, std::string name, bool critical) = 0;
};

} // namespace vaf

extern std::unique_ptr<vaf::UserControllerInterface> CreateUserController();

#endif // INCLUDE_VAF_USER_CONTROLLER_H_