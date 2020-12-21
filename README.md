# pywdl

## Checklist

- Top priority denoted as "**(!!)**".

#### WDL -> Python objects Transformation

Compilation design; expressions are stored as Python code as strings in collections.

- Types
  * [X] Primitives (String, Int, Float, Boolean, File)
    - [ ] Directory
    - [ ] allow user to hook into this to modify how this is parsed. **(!!)**
  * [X] Compound (Array, Pair, Map)
  * [ ] Struct
- Expression
  * [X] LOR, LAND
  * [X] ==, !=, <=, >=, <, >
  * [X] +, -
  * [X] *, /, %
  * [X] apply (function call)
  * [X] array_literal
  * [X] pair_literal
  * [ ] map_literal
  * [ ] struct_literal
  * [X] ifthenelse
  * [X] expression_group
  * [ ] get_name **(!!)**
    - [ ] allow user to hook into this to modify how this is parsed. **(!!)**
  * [ ] negate **(!!)**
  * [ ] unirarysigned
  * [X] primitives (including None and variables)
  * [ ] left_name
- Document
  * [ ] import
  * [ ] struct
  * [X] task
  * [X] workflow
- Workflow
  * [X] input
  * [X] output
  * [X] bound_decls (non-input declarations)
  * [X] call
  * [X] scatter
  * [X] conditional
  * [ ] parameter_meta
  * [ ] meta
- Task
  * [X] input
  * [X] output
  * [X] command
  * [X] runtime
  * [ ] hints
  * [X] bound_decls (non-input declarations)
  * [ ] parameter_meta
  * [ ] meta


## License

The following files come from [openwdl/wdl](https://github.com/openwdl/wdl/tree/main/versions/development/parsers/antlr4) under the [BSD 3-Clause "New" or "Revised" License](https://github.com/openwdl/wdl/blob/main/LICENSE).

- [pywdl/antlr/WdlLexer.g4](pywdl/antlr/WdlLexer.g4)
- [pywdl/antlr/WdlParser.g4](pywdl/antlr/WdlParser.g4)

The following file is modified from [DataBiosphere/toil](https://github.com/DataBiosphere/toil/) under the [Apache License, v2.0](https://github.com/DataBiosphere/toil/blob/master/LICENSE).

- [pywdl/types.py](pywdl/types.py)
