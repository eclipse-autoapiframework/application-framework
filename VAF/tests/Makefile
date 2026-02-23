PYTHON_VERSION ?= 3.12

# GENERAL UNIT TESTS

UNIT_TESTS = core vafgeneration vafmodel vafvssimport vafifextojson
define make-unit-test-target
  	test-unit-$(subst _,-,$1):
		uv run --python ${PYTHON_VERSION} pytest --junitxml=tests/unit/results/$1_report.xml \
		--cov-report=xml:tests/unit/results/$1_cov.xml \
		--cov --cov-branch \
		-vv tests/unit/$1/ $(PYTEST_FLAGS)
  	test-unit:: test-unit-$(subst _,-,$1)
endef

$(foreach element,$(UNIT_TESTS),$(eval $(call make-unit-test-target,$(element))))

# vafpy UNIT TESTS

## Example in test_example.py ##
test-unit-vafpy::
	uv run --python ${PYTHON_VERSION} pytest --junitxml=tests/unit/results/vafpy_report.xml \
	--cov-report=xml:tests/unit/results/vafpy_cov.xml \
	--cov --cov-branch \
	tests/unit/vafpy/test_example.py $(PYTEST_FLAGS)

## CaC UT: Run every test in test_cac.py separately so ModelRuntime() will be not polluted ##
CAC_UT = test_generate_vss_model \
		test_bug_remove_unused_artifacts \
		test_consolidation_fixed_size_array_vector \
		test_consolidation_fixed_size_array_vector_reference \
		test_bug_cleanup_vss_model \
		test_bug_cleanup_vaf_422 \
		test_validation_empty_interfaces \
		test_bug_vaf_553 \
		test_adapt_persistency_cleanup \
		test_vaf_577_string_base_type

define make-vafpy-cac-unit-test
  	vafpy-cac-unit-$(subst _,-,$1):
		uv run --python ${PYTHON_VERSION} pytest --junitxml=tests/unit/results/vafpy_report.xml \
		--cov-report=xml:tests/unit/results/vafpy_cov.xml \
		--cov --cov-branch \
		tests/unit/vafpy/test_cac.py::$1 $(PYTEST_FLAGS)
  	test-unit-vafpy:: vafpy-cac-unit-$(subst _,-,$1)
endef
$(foreach element,$(CAC_UT),$(eval $(call make-vafpy-cac-unit-test,$(element))))

# update test unit with vafpy
test-unit:: test-unit-vafpy

# COMPONENT TESTS

COMP_TEST = cli scenario
define make-component-test-target
  	test-component-$(subst _,-,$1):
		uv run --python ${PYTHON_VERSION} pytest -rA -l --junitxml=tests/component/results/$1_report.xml \
		--cov-report=xml:tests/component/results/$1_cov.xml \
		--cov --cov-branch \
		-vv tests/component/$1/ $(PYTEST_FLAGS)
  	test-component:: test-component-$(subst _,-,$1)
endef

$(foreach element,$(COMP_TEST),$(eval $(call make-component-test-target,$(element))))

# all TESTS
test: test-unit test-component
