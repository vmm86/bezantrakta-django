# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXPROJ  = bezantrakta-django
SOURCEDIR   = ../../
# SPHINXBUILD = python -msphinx
SPHINXBUILD = sphinx-build
SPHINXOPTS  = -t dev
BUILDDIR    = .

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(DEV_SOURCEDIR)" "$(DEV_BUILDDIR)" $(SPHINXOPTS)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new "make mode" option.
# $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@echo "Удаляется предыдущая версия документации..."
	@rm -rf "$(BUILDDIR)/doctrees" "$(BUILDDIR)/html"
	@echo "Генерация новой версии документации..."
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)
