---
paths:
  - "**/tests/testthat/*.R"
---

# JASP Testing Instructions

## Test Framework

This module uses the `jaspTools` testing framework. Tests are **critical** and must always pass before committing code.

## Running Tests

**Full test suite:**
```r
Rscript -e "library(jaspTools); testAll()"
```

**Critical rules:**
- Tests take 70-300+ seconds to complete
- **NEVER CANCEL** tests - always let them run to completion
- Set timeout to at least 300 seconds (5 minutes)
- Some deprecation warnings are expected and can be ignored
- ALL tests must pass before proceeding

**Single analysis tests:**
```r
Rscript -e "library(jaspTools); testAnalysis('AnalysisName')"
```

## Test File Structure

Each test file in `tests/testthat/` corresponds to an R analysis file:
- `test-equivalenceonesamplettest.R` → `R/equivalenceonesamplettest.R`
- Test file name pattern: `test-<analysisname>.R`

## Writing Tests

### Basic test structure:
```r
# 1. Set up analysis options
options <- jaspTools::analysisOptions("EquivalenceOneSampleTTest")
options$variables <- "contGamma"
options$descriptives <- TRUE
options$equivalenceboundsplot <- TRUE

# 2. Set seed for reproducibility
set.seed(1)

# 3. Run the analysis
results <- jaspTools::runAnalysis("EquivalenceOneSampleTTest", "test.csv", options)

# 4. Test tables
test_that("Table name matches", {
  table <- results[["results"]][["tableName"]][["data"]]
  jaspTools::expect_equal_tables(table, list(...expected values...))
})

# 5. Test plots
test_that("Plot name matches", {
  plotName <- results[["results"]][["containerName"]][["collection"]][["plotId"]][["data"]]
  testPlot <- results[["state"]][["figures"]][[plotName]][["obj"]]
  jaspTools::expect_equal_plots(testPlot, "plotname", dir="AnalysisName")
})
```

### Key testing functions:
- `jaspTools::analysisOptions(name)` - Get default options for an analysis
- `jaspTools::runAnalysis(name, dataset, options)` - Run analysis with options
- `jaspTools::expect_equal_tables(actual, expected)` - Compare table output
- `jaspTools::expect_equal_plots(plot, name, dir)` - Compare plot output

## Test Data

- Test datasets located in `jaspTools` package (e.g., "test.csv")
- Use `set.seed()` before running analyses for reproducibility
- Tests use snapshot testing - expected values stored in `tests/testthat/_snaps/`

## When to Update Tests

### Always update tests when:
1. Adding new analysis outputs (tables, plots, text)
2. Modifying existing output structure or values
3. Adding new QML options that affect results
4. Changing analysis calculations

### How to update test expectations:
1. Run tests and capture new output
2. Verify the new output is correct
3. Update expected values in test file
4. Re-run tests to confirm they pass

## Test Workflow

### Before making code changes:
```bash
Rscript -e "library(jaspTools); testAll()"
```
Establish baseline - all tests should pass.

### After making code changes:
```bash
Rscript -e "library(jaspTools); testAll()"
```
Verify your changes don't break existing functionality.

### If tests fail:
1. Review the failure messages carefully
2. Check if failure is expected (due to your intentional changes)
3. If expected: update test expectations
4. If unexpected: fix your code
5. Re-run tests until all pass

## Adding New Tests

When adding a new analysis:

1. Create test file: `tests/testthat/test-<analysisname>.R`
2. Set up options with all default values explicitly set
3. Test all output tables and plots
4. Test edge cases and error conditions
5. Use meaningful variable names and test data
6. Add comments explaining complex test setups

## Best Practices

- **One test per output element** - separate `test_that()` blocks for each table/plot
- **Descriptive test names** - clearly state what is being tested
- **Reproducible** - always use `set.seed()` for analyses with randomness
- **Complete option coverage** - test with various option combinations
- **Document expected behavior** - add comments for non-obvious test expectations
- **Keep tests focused** - each test should verify one specific aspect
