ANTLR_VERSION = antlr-4.8-complete
GENERATED_PATH = pywdl/antlr
FLAGS = -jar $(ANTLR_VERSION).jar -Dlanguage=Python3
GRAPH_PATH = graph

all: generate clean-extra

# Download antlr4 locally
antlr:
	if [ ! -f $(ANTLR_VERSION).jar ]; then \
		curl -O https://www.antlr.org/download/$(ANTLR_VERSION).jar; fi;

generate: antlr
	java $(FLAGS) $(GENERATED_PATH)/WdlLexer.g4
	java $(FLAGS) -listener -visitor $(GENERATED_PATH)/WdlParser.g4

clean-extra:
	cd $(GENERATED_PATH) && find . -type f \( -name '*.interp' -or -name '*.tokens' \) -delete

clean: clean-extra
	rm $(ANTLR_VERSION).jar
	# also rm generated files
