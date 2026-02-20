namespace :dev do

  desc "DEV: Initialize Project"
  namespace :init do
    task_name = ["start", "format", "lint"]
    descriptions = ["Initializing" "Formatting", "Running Linters"]

    task_name.each_with_index do |dev_task, index|
      desc "DEV: #{descriptions[index]} VAF Python Project"
      task dev_task.split("-")[0] do
        Dir.chdir("VAF") do
          sh "make #{dev_task}"
        end
      end
    end

    desc "DEV: #{descriptions[1]} and #{descriptions[2]} VAF Python Project"
    task precommit: %i[format lint]
  end

  desc "DEV: Run test suites in Project"
  namespace :test do

    namespace :unit do
      unit_tests = ["cli-core", "vafgeneration", "vafmodel", "vafpy", "vafvssimport"]
      unit_tests.each do |ut|
        desc "DEV: Run Unit Test for #{ut} in Project"
        task ut do
          Dir.chdir("VAF") do
            sh "make test-unit-#{ut}"
          end
        end
      end

      desc "DEV: Run ALL Unit Test in Project"
      task :all do
        Dir.chdir("VAF") do
          sh "make test-unit"
        end
      end
    end

    namespace :component do
      comp_tests = ["cli", "scenario"]
      comp_tests.each do |ct|
        desc "DEV: Run Component Test for #{ct} in Project"
        task ct do
          Dir.chdir("VAF") do
            sh "make test-component-#{ct}"
          end
        end
      end

      desc "DEV: Run ALL Component Test in Project"
      task :all do
        Dir.chdir("VAF") do
          sh "make test-component"
        end
      end
    end

    desc "DEV: Run ALL test suites in Project"
    task all: %i[unit:all component:all]
  end

  desc "DEV: Rake job for Pipeline"
  task pipeline: %i[init:precommit test:all]
end

namespace :prod do
  namespace :install do
    desc 'PROD: Install vaf wheel with uv'
    task :vafcli do
      path_to_vafinstall = "_vafinstall"
      FileUtils.rm_rf(path_to_vafinstall)
      FileUtils.mkdir_p(path_to_vafinstall)

      Dir.chdir("VAF") do
        sh 'make clean build'
        sh 'make install'
      end
    end

  end
end
