# Shared bootstrap for direct Rscript invocations.
#
# Agents call R directly -- every Rscript call is a fresh process, so source
# this first to load the project library and configure jaspTools:
#
#   Rscript --no-init-file -e 'source(".claude/r-preamble.R"); agentTestAll()'
#
# Run .claude/session_startup.R once first to install the module and jaspTools.
# In the JASP container, pass pathJaspDesktop explicitly -- see
# .claude/rules/testing-instructions.md.

renv::load()
library(jaspTools)
# installJaspCorePkgs = FALSE is load-bearing: it defaults to TRUE, and with
# force = TRUE (also the default) every call would reinstall jaspBase,
# jaspResults and jaspGraphs. Installing those is session_startup.R's job.
setupJaspTools(installJaspCorePkgs = FALSE, quiet = TRUE)
setPkgOption("module.dirs", ".")
setPkgOption("reinstall.modules", FALSE)
