#include "vaf/runtime.h"
#include "vaf/logging.h"

namespace vaf {

    Runtime::Runtime() {
        vaf::LoggerSingleton::getInstance()->SetLogLevelVerbose();
    }

    Runtime::~Runtime() {
        vaf::LoggerSingleton::getInstance()->CleanLoggers();
    }

} // namespace vaf
