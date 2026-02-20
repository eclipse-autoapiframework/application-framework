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
/*!        \file  executor.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef VAF_EXECUTOR_H_
#define VAF_EXECUTOR_H_

#include "vaf/logging.h"
#include "vaf/container_types.h"

#include <atomic>
#include <chrono>
#include <functional>
#include <memory>
#include <thread>
#include <utility>

namespace vaf {

    class TaskHandle {
    public:
        TaskHandle(vaf::String name, uint64_t period, std::function<void(void)> task, const vaf::String &owner,
                       const vaf::Vector<vaf::String> &run_after, uint64_t offset, std::chrono::nanoseconds budget);

        const vaf::String &Name() const;

        bool IsActive() const;

        void Execute() const;

        uint64_t Period() const;

        void Start();

        void Stop();

        const vaf::String &Owner();

        const vaf::Vector<vaf::String> &RunAfter();

        uint64_t Offset() const;

        std::chrono::nanoseconds Budget() const;

    private:
        vaf::String name_;
        bool is_active_{false};
        uint64_t period_;
        std::function<void(void)> task_;
        vaf::String owner_;
        vaf::Vector<vaf::String> run_after_;
        uint64_t offset_;
        std::chrono::nanoseconds budget_;
    };

    class Executor {
    public:
        explicit Executor(std::chrono::milliseconds running_period);

        ~Executor();

        Executor(const Executor &) = delete;

        Executor(Executor &&) = delete;

        Executor &operator=(const Executor &) = delete;

        Executor &operator=(Executor &&) = delete;

        template<typename T>
        std::shared_ptr<TaskHandle> RunPeriodic(std::chrono::milliseconds period,
                                                    T &&task,
                                                    const vaf::String &owner,
                                                    const vaf::Vector<vaf::String> &run_after,
                                                    uint64_t offset = 0,
                                                    std::chrono::nanoseconds budget = std::chrono::nanoseconds{0}) {

            return RunPeriodic("", period, std::move(task), owner, run_after, {}, offset, budget);
        }

        template<typename T>
        std::shared_ptr<TaskHandle> RunPeriodic(const vaf::String &name,
                                                    std::chrono::milliseconds period,
                                                    T &&task,
                                                    const vaf::String &owner,
                                                    const vaf::Vector<vaf::String> &run_after,
                                                    const vaf::Vector<vaf::String> &run_after_tasks = {},
                                                    uint64_t offset = 0,
                                                    std::chrono::nanoseconds budget = std::chrono::nanoseconds{0}) {
            auto check_can_run = [this, &run_after, &run_after_tasks](
                    vaf::Vector<std::shared_ptr<TaskHandle>>::iterator current_position) {
                auto pos{std::next(current_position)};
                bool can_run{true};
                for (; pos != tasks_.end(); ++pos) {
                    if (std::any_of(run_after.begin(), run_after.end(), [&pos](const vaf::String &run_after_element) {
                        return pos->get()->Owner() == run_after_element;
                    })) {
                        can_run = false;
                        break;
                    }
                    if (current_position->get()->Owner() == pos->get()->Owner()) {
                        if (std::any_of(run_after_tasks.begin(), run_after_tasks.end(),
                                        [&pos](const vaf::String &run_after_element) {
                                            return pos->get()->Name() == run_after_element;
                                        })) {
                            can_run = false;
                            break;
                        }
                    }
                }

                return can_run;
            };

            auto search_pos{tasks_.begin()};
            for (; search_pos != tasks_.end(); ++search_pos) {
                if (check_can_run(search_pos)) {
                    break;
                }
            }

            // TODO implement run_after_tasks

            auto insert_pos = tasks_.insert(search_pos,
                                                std::make_unique<TaskHandle>(name, period / running_period_,
                                                                                 std::forward<T>(task), owner,
                                                                                 run_after, offset, budget));
            return *insert_pos;
        }

    private:
        void ExecutorThread();

        void ExecuteTask(TaskHandle &task);

        std::chrono::milliseconds running_period_;
        vaf::Vector<std::shared_ptr<TaskHandle>> tasks_{};
        std::atomic<bool> exit_requested_{false};
        std::thread thread_;
        vaf::Logger &logger_;
    };

    class ModuleExecutor {
    public:
        ModuleExecutor(Executor &executor, vaf::String name, vaf::Vector<vaf::String> dependencies);

        template<typename T>
        void RunPeriodic(std::chrono::milliseconds period, T &&task, uint64_t offset = 0,
                         std::chrono::nanoseconds budget = std::chrono::nanoseconds{0}) {
            handles_.emplace_back(
                    executor_.RunPeriodic(period, std::move(task), name_, dependencies_, offset, budget));

            if (started_) {
                handles_.back()->Start();
            }
        }

        template<typename T>
        void RunPeriodic(const vaf::String &name, std::chrono::milliseconds period, T &&task,
                         vaf::Vector<vaf::String> task_dependencies = {}, uint64_t offset = 0,
                         std::chrono::nanoseconds budget = std::chrono::nanoseconds{0}) {
            handles_.emplace_back(executor_.RunPeriodic(name, period, std::move(task), name_, dependencies_,
                                                        std::move(task_dependencies), offset, budget));

            if (started_) {
                handles_.back()->Start();
            }
        }

        void Start();

        void Stop();

    private:
        Executor &executor_;
        vaf::Vector<std::shared_ptr<TaskHandle>> handles_;
        bool started_;
        vaf::String name_;
        vaf::Vector<vaf::String> dependencies_;
    };

} // namespace vaf

#endif // VAF_EXECUTOR_H_
