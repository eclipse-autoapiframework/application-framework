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
/*!        \file  logging.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef VAF_LOGGING_H_
#define VAF_LOGGING_H_

#include "vaf/output_sync_stream.h"
#include <mutex>
#include <list>

namespace vaf {
    class LoggerSingleton;

    class Logger {
    public:
        ~Logger() {
            if (previous_line_streamed) {
                vaf::OutputSyncStream{} << std::endl;
            }
            vaf::OutputSyncStream{} << std::flush;
        }

        auto LogFatal() -> Logger & {
            current_log_level_ = FATAL;
            log_start_message = true;
            if (previous_line_streamed) {
                vaf::OutputSyncStream{} << std::endl;
            }
            return *this;
        }


        auto LogError() -> Logger & {
            current_log_level_ = ERROR;
            log_start_message = true;
            if (previous_line_streamed) {
                vaf::OutputSyncStream{} << std::endl;
            }
            return *this;
        }

        auto LogWarn() -> Logger & {
            current_log_level_ = WARN;
            log_start_message = true;
            if (previous_line_streamed) {
                vaf::OutputSyncStream{} << std::endl;
            }
            return *this;
        }

        auto LogInfo() -> Logger & {
            current_log_level_ = INFO;
            log_start_message = true;
            if (previous_line_streamed) {
                vaf::OutputSyncStream{} << std::endl;
            }
            return *this;
        }

        auto LogDebug() -> Logger & {
            current_log_level_ = DEBUG;
            log_start_message = true;
            if (previous_line_streamed) {
                vaf::OutputSyncStream{} << std::endl;
            }
            return *this;
        }

        auto LogVerbose() -> Logger & {
            current_log_level_ = VERBOSE;
            log_start_message = true;
            if (previous_line_streamed) {
                vaf::OutputSyncStream{} << std::endl;
            }
            return *this;
        }

        auto operator<<(const char *s) noexcept -> Logger & {
            if (current_log_level_ <= aimed_log_level_) {
                previous_line_streamed = true;
                if (log_start_message) {
                    vaf::OutputSyncStream{} << "[" << ctx_id_ << ": " << ctx_description_ << "] ";
                    log_start_message = false;
                }
                vaf::OutputSyncStream{} << s;
            }
            return *this;
        }

        auto operator<<(int i) noexcept -> Logger & {
            if (current_log_level_ <= aimed_log_level_) {
                previous_line_streamed = true;
                if (log_start_message) {
                    vaf::OutputSyncStream{} << "[" << ctx_id_ << ": " << ctx_description_ << "] ";
                    log_start_message = false;
                }
                vaf::OutputSyncStream{} << i;
            }
            return *this;
        }

        friend class LoggerSingleton;

        Logger(Logger &&logger_) {
            this->log_start_message = logger_.log_start_message;
            this->previous_line_streamed = logger_.previous_line_streamed;
            this->current_log_level_ = logger_.current_log_level_;
            this->ctx_description_ = logger_.ctx_description_;
            this->ctx_id_ = logger_.ctx_id_;
            this->aimed_log_level_ = logger_.aimed_log_level_;
        }

    private:

        enum LogLevel {
            OFF = 0,
            FATAL = 1,
            ERROR = 2,
            WARN = 3,
            INFO = 4,
            DEBUG = 5,
            VERBOSE = 6
        };

        Logger(const char *ctx_id, const char *ctx_description, LogLevel aimed_log_level) : ctx_id_{ctx_id},
                                                                                            ctx_description_{
                                                                                                    ctx_description},
                                                                                            aimed_log_level_{
                                                                                                    aimed_log_level} {}

        Logger() = delete;

        Logger(const Logger &) = delete;

        Logger &operator=(const Logger &) = delete;

        const char *ctx_id_;
        const char *ctx_description_;
        LogLevel aimed_log_level_;
        LogLevel current_log_level_ = DEBUG;
        bool log_start_message = false;
        bool previous_line_streamed = false;
    };

    class LoggerSingleton {
    private:
        LoggerSingleton() : log_level_{Logger::LogLevel::FATAL},
                            default_logger_{CreateLogger("DL", "DefaultLogger")} {}

        LoggerSingleton(const LoggerSingleton &) = delete;

        LoggerSingleton &operator=(const LoggerSingleton &) = delete;

        static std::mutex mtx; // Mutex for thread safety
        static LoggerSingleton *instance;

        std::list<Logger> loggers_{};

        Logger::LogLevel log_level_;
    public:
        static LoggerSingleton *getInstance() {
            // Acquire lock before checking instance
            std::lock_guard<std::mutex> lock(mtx); // automatically releases lock
            if (instance == nullptr) {
                instance = new LoggerSingleton(); // Create the instance only once
            }
            return instance;
        }

        Logger &CreateLogger(const char *ctx_id, const char *ctx_description) {
            loggers_.push_back(std::move(Logger{ctx_id, ctx_description, log_level_}));
            return loggers_.back();
        }

        void SetLogLevelOff() {
            log_level_ = Logger::LogLevel::OFF;
        };

        void SetLogLevelFatal() {
            log_level_ = Logger::LogLevel::FATAL;
        };

        void SetLogLevelError() {
            log_level_ = Logger::LogLevel::ERROR;
        };

        void SetLogLevelWarn() {
            log_level_ = Logger::LogLevel::WARN;
        };

        void SetLogLevelInfo() {
            log_level_ = Logger::LogLevel::INFO;
        };

        void SetLogLevelDebug() {
            log_level_ = Logger::LogLevel::DEBUG;
        };

        void SetLogLevelVerbose() {
            log_level_ = Logger::LogLevel::VERBOSE;
        };

        void CleanLoggers() {
            loggers_.clear();
        }

        Logger &default_logger_;
    };

    Logger &CreateLogger(const char *ctx_id, const char *ctx_description);

} // namespace vaf

#endif // VAF_LOGGING_H_
