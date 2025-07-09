#ifndef INCLUDE_VAF_RUNTIME_H_
#define INCLUDE_VAF_RUNTIME_H_

namespace vaf {
  class Runtime {
    public:
      Runtime();
      ~Runtime();

      Runtime(const Runtime&) = delete;
      Runtime(Runtime&&) = delete;
      Runtime& operator=(const Runtime&) = delete;
      Runtime& operator=(Runtime&&) = delete;
  };

} // namespace vaf

#endif // INCLUDE_VAF_RUNTIME_H_