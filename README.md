# pywdl

## Road map

Antlr4 to Python compilation string Transforms

- [ ] Types
  * [X] Primitives (String, Int, Float, Boolean, File)
    - [ ] Directory
  * [X] Compound (Array, Pair, Map)
  * [ ] Struct **(!!)**
- [ ] Expression
  * [X] LOR, LAND
  * [ ] ==, !==, <=, >=, <, >
  * [ ] +, -
  * [ ] *, /, %
  * [ ] <=, <, =, >, >=
  * [ ] apply
  * [X] array_literal
  * [X] pair_literal
  * [ ] map_literal
  * [ ] struct_literal
  * [ ] ifthenelse
  * [X] expression_group
  * [ ] get_name
  * [ ] negate
  * [ ] unirarysigned
  * [ ] primitives
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
  * [ ] input
  * [ ] runtime
  * [ ] command
  * [ ] output

Antlr4 to Python objects Transforms?


## Credits

The following files come from [openwdl](https://github.com/openwdl/wdl/tree/main/versions/development/parsers/antlr4) with license: https://github.com/openwdl/wdl/blob/main/LICENSE. 

- [WdlLexer.g4](pywdl/antlr/WdlLexer.g4)
- [WdlParser.g4](pywdl/antlr/WdlParser.g4)

The following file is modified from [Toil](https://github.com/DataBiosphere/toil/) with license: https://github.com/DataBiosphere/toil/blob/master/LICENSE

- [wdl_parser.py](https://github.com/DataBiosphere/toil/blob/master/src/toil/wdl/wdl_types.py)
