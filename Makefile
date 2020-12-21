ANTLR_VERSION = antlr-4.8-complete
GENERATED_PATH = pywdl/antlr
FLAGS = -jar $(ANTLR_VERSION).jar -Dlanguage=Python3

all: generate clean-extras

test:
	python -m pytest tests/parserTests.py

# Download antlr4 locally
antlr:
	if [ ! -f $(ANTLR_VERSION).jar ]; then \
		curl -O https://www.antlr.org/download/$(ANTLR_VERSION).jar; fi;

generate: antlr
	java $(FLAGS) $(GENERATED_PATH)/WdlLexer.g4
	java $(FLAGS) -listener -visitor $(GENERATED_PATH)/WdlParser.g4

clean-extras:
	cd $(GENERATED_PATH) && find . -type f \( -name '*.interp' -or -name '*.tokens' \) -delete

clean:
	rm $(ANTLR_VERSION).jar
	cd $(GENERATED_PATH) && find . -type f -not \( -name '.gitignore' -or -name '__init__.py' -or -name '*.g4' \) -delete
