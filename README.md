# pywdl

## Checklist

- Top priority denoted as "**(!!)**".

#### WDL -> Python string Transforms

Compilation design; expressions are stored as Python code as strings in collections.

- Types
  * [X] Primitives (String, Int, Float, Boolean, File)
    - [ ] Directory
  * [X] Compound (Array, Pair, Map)
  * [ ] Struct
- Expression
  * [X] LOR, LAND
  * [ ] ==, !==, <=, >=, <, > **(!!)**
  * [ ] +, - **(!!)**
  * [ ] *, /, % **(!!)**
  * [ ] <=, <, =, >, >= **(!!)**
  * [X] apply (function call)
    - [ ] allow user to hook into this to modify how arguments are parsed. **(!!)**
  * [X] array_literal
  * [X] pair_literal
  * [ ] map_literal
  * [ ] struct_literal
  * [X] ifthenelse
  * [X] expression_group
  * [ ] get_name **(!!)**
  * [ ] negate **(!!)**
  * [ ] unirarysigned
  * [X] primitives (including None and variables)
  * [ ] left_name
- Document
  * [ ] import
  * [ ] meta
- Workflow
  * [X] input
  * [X] call
  * [X] scatter
  * [X] conditional
  * [X] output
- Task
  * [ ] input **(!!)**
  * [ ] runtime **(!!)**
  * [ ] command **(!!)**
  * [ ] output **(!!)**

#### Antlr4 to objects Transforms

- [ ] ?

## License

The following files come from [openwdl/wdl](https://github.com/openwdl/wdl/tree/main/versions/development/parsers/antlr4) under the [BSD 3-Clause "New" or "Revised" License](https://github.com/openwdl/wdl/blob/main/LICENSE).

- [pywdl/antlr/WdlLexer.g4](pywdl/antlr/WdlLexer.g4)
- [pywdl/antlr/WdlParser.g4](pywdl/antlr/WdlParser.g4)

The following file is modified from [DataBiosphere/toil](https://github.com/DataBiosphere/toil/) under the [Apache License, v2.0](https://github.com/DataBiosphere/toil/blob/master/LICENSE).

- [pywdl/types.py](pywdl/types.py)
