/*!********************************************************************************************************************
 *  COPYRIGHT
 *  -------------------------------------------------------------------------------------------------------------------
 *
 *  Copyright (c) 2025 by Vector Informatik GmbH. All rights reserved.
 *
 *                This software is copyright protected and proprietary to Vector Informatik GmbH.
 *                Vector Informatik GmbH grants to you only those rights as set out in the license conditions.
 *                All other rights remain with Vector Informatik GmbH.
 *
 *  -------------------------------------------------------------------------------------------------------------------
 *  FILE DESCRIPTION
 *  -----------------------------------------------------------------------------------------------------------------*/
/*!        file  controller_interface.h
 *         brief
 *
 *********************************************************************************************************************/
#ifndef INCLUDE_VAF_DATA_PTR_H
#define INCLUDE_VAF_DATA_PTR_H

#include "vaf/logging.h"

#include <memory>
#include <type_traits>

namespace vaf {

    namespace internal {
        template<typename T>
        class DataPtrHelper;
    }  // namespace internal

    template<typename T>
    class DataPtr {
        friend internal::DataPtrHelper<T>;

    private:
        enum class Contains {
            Empty, RawPtr
        };

        struct Container {
            std::unique_ptr<T> raw_ptr_;
        };

    public:
        DataPtr() : contains_{Contains::Empty}, container_{std::make_shared<Container>()} {}

        DataPtr (const DataPtr& other) {
          this->container_= other.container_;
          this->contains_= other.contains_;
        }

        DataPtr (DataPtr&& other) {
          this->container_= std::move(other.container_);
          this->contains_= std::move(other.contains_);
        }

        DataPtr(std::unique_ptr<T> &&ptr) : contains_{Contains::RawPtr}, container_{std::make_shared<Container>()} {
            container_->raw_ptr_ = std::move(ptr);
        }

        T &operator*() noexcept { return *(this->operator->()); }

        T *operator->() const noexcept {
            if (contains_ == Contains::RawPtr) {
                return container_->raw_ptr_.get();
            }
            vaf::LoggerSingleton::getInstance()->default_logger_.LogFatal() << "DataPtr is empty";
            std::abort();
        }

        DataPtr& operator=(const DataPtr& other) {
          this->container_= other.container_;
          this->contains_= other.contains_;
          return *this;
        }

        DataPtr& operator=(DataPtr&& other) {
          this->container_= std::move(other.container_);
          this->contains_= std::move(other.contains_);
          return *this;
        }

        explicit operator bool() const { return contains_ != Contains::Empty; }

    private:
        Contains contains_;
        std::shared_ptr<Container> container_;
    };

    template<typename T>
    class ConstDataPtr {
    private:
        enum class Contains {
            Empty, SamplePtr, RawPtr
        };

        struct Container {
            std::unique_ptr<T> raw_ptr_{};
        };

    public:
        ConstDataPtr() : contains_{Contains::Empty}, container_{std::make_shared<Container>()} {}

        ConstDataPtr (const ConstDataPtr& other) {
          this->container_= other.container_;
          this->contains_= other.contains_;
        }

        ConstDataPtr (ConstDataPtr&& other) {
          this->container_= std::move(other.container_);
          this->contains_= std::move(other.contains_);
        }

        ConstDataPtr(std::unique_ptr<T> &&ptr) : contains_{Contains::RawPtr},
                                                 container_{std::make_shared<Container>()} {
            container_->raw_ptr_ = std::move(ptr);
        }

        const T &operator*() const noexcept { return *(this->operator->()); }

        const T *operator->() const noexcept {
            if (contains_ == Contains::RawPtr) {
                return container_->raw_ptr_.get();
            }
            vaf::LoggerSingleton::getInstance()->default_logger_.LogFatal() << "DataPtr is empty";
            std::abort();
        }

        ConstDataPtr& operator=(const ConstDataPtr& other) {
          this->container_= other.container_;
          this->contains_= other.contains_;
          return *this;
        }

        ConstDataPtr& operator=(ConstDataPtr&& other) {
          this->container_= std::move(other.container_);
          this->contains_= std::move(other.contains_);
          return *this;
        }

        explicit operator bool() const { return contains_ != Contains::Empty; }

        std::unique_ptr<T> getRawPtr() { return std::move(container_->raw_ptr_); };

    private:
        Contains contains_;
        std::shared_ptr<Container> container_;
    };

}  // namespace vaf

#endif  // INCLUDE_VAF_DATA_PTR_H

