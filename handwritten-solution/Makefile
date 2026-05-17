PYTHON     ?= python3
SKILLS_DST := $(HOME)/.claude/skills/handwritten-solution

.PHONY: help install install-skill uninstall-skill

help:
	@echo "Targets:"
	@echo "  make install         — установить Python-зависимости (Pillow, numpy, python-docx)"
	@echo "  make install-skill   — симлинк скилла в ~/.claude/skills/"
	@echo "  make uninstall-skill — удалить симлинк скилла"

install:
	$(PYTHON) -m pip install --user Pillow numpy python-docx

install-skill:
	@mkdir -p $(HOME)/.claude/skills
	@ln -sfn $(CURDIR) $(SKILLS_DST)
	@echo "Linked: $(SKILLS_DST) -> $(CURDIR)"

uninstall-skill:
	@rm -f $(SKILLS_DST)
	@echo "Removed: $(SKILLS_DST)"
