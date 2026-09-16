# JASP Module - one-time R setup
# Installs the module and jaspTools into the project library.
#
# Run once per checkout, in an interactive R session or directly:
#   Rscript --no-init-file -e 'source(".claude/session_startup.R")'
#
# Afterwards agents call R directly, sourcing .claude/r-preamble.R for the
# per-call bootstrap.

# Fix locale issue with renv.lock files created on non-English systems
if (.Platform$OS.type == "windows") {
  Sys.setlocale("LC_ALL", "English_United States.utf8")
} else {
  Sys.setlocale("LC_ALL", "C.UTF-8")
}

# renv::restore() first so lockfile-pinned versions win for shared deps,
# then the module + jaspTools.
renv::restore(prompt = FALSE)
renv::install(c(".", "jasp-stats/jaspTools"), prompt = FALSE)
library(jaspTools)
setupJaspTools()
setPkgOption("module.dirs", ".")
setPkgOption("reinstall.modules", FALSE)
