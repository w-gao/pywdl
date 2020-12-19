from antlr4.tree.Tree import TerminalNodeImpl
from pywdl.antlr.WdlParser import WdlParser
from pywdl.types import (
    WDLStringType,
    WDLIntType,
    WDLFloatType,
    WDLBooleanType,
    WDLFileType,
    WDLArrayType,
    WDLPairType,
    WDLMapType
)


primitive_types = {
    'String': WDLStringType,
    'Int': WDLIntType,
    'Float': WDLFloatType,
    'Boolean': WDLBooleanType,
    'File': WDLFileType,
    'Directory': None,  # to be implemented.
}


def parse_wdl_type_from_context(ctx):
    """
    Returns a WDLType instance.
    """
    identifier = ctx.type_base().children[0]
    optional = ctx.OPTIONAL() is not None

    # primitives
    if isinstance(identifier, TerminalNodeImpl):
        type_ = primitive_types.get(identifier.getText())
        if type_:
            return type_(optional=optional)
        else:
            raise RuntimeError(f'Unsupported primitive type: {identifier.getText()}')
    # Array[element]
    elif isinstance(identifier, WdlParser.Array_typeContext):
        return WDLArrayType(element=parse_wdl_type_from_context(identifier.wdl_type()), optional=optional)
    # Pair[left, right]
    elif isinstance(identifier, WdlParser.Pair_typeContext):
        return WDLPairType(
            left=parse_wdl_type_from_context(identifier.wdl_type(0)),
            right=parse_wdl_type_from_context(identifier.wdl_type(1)),
            optional=optional)
    # Map[left, right]
    elif isinstance(identifier, WdlParser.Map_typeContext):
        return WDLMapType(
            key=parse_wdl_type_from_context(identifier.wdl_type(0)),
            value=parse_wdl_type_from_context(identifier.wdl_type(1)),
            optional=optional)
    else:
        raise RuntimeError(f'Unsupported type: {identifier.getText()}')
