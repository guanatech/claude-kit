PYTHON     ?= python3
SKILLS_DST := $(HOME)/.claude/skills/handwritten-solution

DEMO_DIR   ?= /tmp/handwritten_demo

.PHONY: help install install-skill uninstall-skill demo clean clean-all

help:
	@echo "Targets:"
	@echo "  make install         — установить Python-зависимости (Pillow, numpy, python-docx)"
	@echo "  make install-skill   — симлинк скилла в ~/.claude/skills/"
	@echo "  make uninstall-skill — удалить симлинк скилла"
	@echo "  make demo            — сгенерировать демо-страницу в $(DEMO_DIR)"
	@echo "  make clean           — удалить $(DEMO_DIR)"
	@echo "  make clean-all       — clean + __pycache__ + симлинк + Python-зависимости"

install:
	$(PYTHON) -m pip install --user Pillow numpy python-docx

install-skill:
	@mkdir -p $(HOME)/.claude/skills
	@ln -sfn $(CURDIR) $(SKILLS_DST)
	@echo "Linked: $(SKILLS_DST) -> $(CURDIR)"

uninstall-skill:
	@rm -f $(SKILLS_DST)
	@echo "Removed: $(SKILLS_DST)"

demo:
	$(PYTHON) handwritten_generator.py

clean:
	@rm -rf $(DEMO_DIR)
	@echo "Cleaned: $(DEMO_DIR)"

clean-all: clean uninstall-skill
	@find . -type d -name __pycache__ -prune -exec rm -rf {} +
	@echo "Cleaned: __pycache__"
	$(PYTHON) -m pip uninstall -y Pillow numpy python-docx
