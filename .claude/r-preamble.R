# Shared bootstrap for direct Rscript invocations.
#
# Agents call R directly -- every Rscript call is a fresh process, so source
# this first to load the project library and configure jaspTools:
#
#   Rscript --no-init-file -e 'source(".claude/r-preamble.R"); agentTestAll()'
#
# Run .claude/session_startup.R once first to install the module and jaspTools.
# In the JASP container, setupJaspTools() needs explicit paths -- see
# .claude/rules/testing-instructions.md.

renv::load()
library(jaspTools)
setupJaspTools(quiet = TRUE)
setPkgOption("module.dirs", ".")
setPkgOption("reinstall.modules", FALSE)
