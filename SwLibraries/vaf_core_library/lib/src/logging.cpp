#include "vaf/logging.h"

namespace vaf {

// Initialize static members outside the class definition
    std::mutex LoggerSingleton::mtx;
    LoggerSingleton *LoggerSingleton::instance = nullptr;

    Logger &CreateLogger(const char *ctx_id, const char *ctx_description) {
        return LoggerSingleton::getInstance()->CreateLogger(ctx_id, ctx_description);
    }

} // namespace vaf