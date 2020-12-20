from collections import OrderedDict  # TODO: switch to dict.
# from builtins import dict as OrderedDict

from pywdl.antlr.WdlParser import WdlParser
from pywdl.antlr.WdlParserVisitor import WdlParserVisitor
from antlr4.tree.Tree import TerminalNodeImpl

from pywdl.types import WDLBooleanType
from pywdl.utils import parse_wdl_type_from_context


class TransformHandler:
    pass


class WdlTransformer(WdlParserVisitor):
    """
    Follow the syntax tree generated by Antlr4 and convert them to working
    Python code as strings stored in Python collections.
    """

    def __init__(self):
        # holds workflow structure from WDL workflow objects
        self.workflows_dictionary = OrderedDict()

        # holds task skeletons from WDL task objects
        self.tasks_dictionary = OrderedDict()

        # unique iterator to add to cmd names
        self.command_number = -1

        # unique iterator to add to call names
        self.call_number = -1

        # unique iterator to add to scatter names
        self.scatter_number = -1

        # unique iterator to add to if names
        self.if_number = -1

    def visitDocument(self, ctx: WdlParser.DocumentContext):
        """
        Root of tree. Contains `version` followed by any number of `document_element`s.
        """
        self.visitVersion(ctx.version())
        for element in ctx.document_element():
            self.visitDocument_element(element)

    def visitVersion(self, ctx: WdlParser.VersionContext):
        assert str(ctx.RELEASE_VERSION()) in ('1.0', 'development'), \
            f'Unsupported version: {str(ctx.RELEASE_VERSION())}.'

    def visitDocument_element(self, ctx: WdlParser.Document_elementContext):
        """
        Contains one of the following: 'import_doc', 'struct', 'workflow', or 'task'.
        """
        # TODO: add support for imports.
        assert isinstance(ctx.children[0], (WdlParser.WorkflowContext,
                                            WdlParser.TaskContext,
                                            WdlParser.ScatterContext)), \
            'Import is not supported.'

        return self.visitChildren(ctx)

    # Workflow section

    def visitWorkflow(self, ctx: WdlParser.WorkflowContext):
        """
        Contains an 'identifier' and an array of `workflow_element`s.
        """
        identifier = ctx.Identifier().getText()
        wf = self.workflows_dictionary.setdefault(identifier, OrderedDict())
        print(f'Visiting workflow: {identifier}')

        for element in ctx.workflow_element():
            section = element.children[0]

            # inputs
            if isinstance(section, WdlParser.Workflow_inputContext):
                wf.setdefault('wf_declarations', {}).update(self.visitWorkflow_input(section))

            # non-input declarations, scatters, calls, and conditionals
            elif isinstance(section, WdlParser.Inner_workflow_elementContext):
                wf_key, contents = self.visitInner_workflow_element(section)
                wf.setdefault(wf_key, {}).update(contents)

            # outputs
            elif isinstance(section, WdlParser.Workflow_outputContext):
                wf['wf_outputs'] = self.visitWorkflow_output(section)

            # O.o
            else:
                raise RuntimeError(f'Unsupported workflow element in visitWorkflow(): {type(section)}')

    def visitWorkflow_input(self, ctx: WdlParser.Workflow_inputContext):
        """
        Contains an array of 'any_decls', which can be unbounded or bounded declarations.

        Example:
            input {
              String in_str = "twenty"
              Int in_int
            }

        Returns a dict={name: decl}.
        """
        return OrderedDict(self.visitAny_decls(decl) for decl in ctx.any_decls())

    def visitWorkflow_output(self, ctx: WdlParser.Workflow_outputContext):
        """
        Contains an array of 'bound_decls' (unbound_decls not allowed).

        Example:
            output {
              String out_str = read_string(stdout())
            }

        Returns an array of tuples=(name, decl).
        """
        return OrderedDict(self.visitBound_decls(decl) for decl in ctx.bound_decls())

    def visitInner_workflow_element(self, ctx: WdlParser.Inner_workflow_elementContext):
        """
        Returns a tuple=(wf_key, contents)
        """
        element = ctx.children[0]

        # bound_decls (e.g.: declarations declared outside of input section)
        if isinstance(element, WdlParser.Bound_declsContext):
            # append this to `wf_declarations` for Toil.
            name, decl = self.visitBound_decls(element)
            return 'wf_declarations', {name: decl}
        # call
        elif isinstance(element, WdlParser.CallContext):
            return self.visitCall(element)
        # scatter
        elif isinstance(element, WdlParser.ScatterContext):
            return self.visitScatter(element)
        # conditional
        elif isinstance(element, WdlParser.ConditionalContext):
            return 'UNIMPLEMENTED', {}
        else:
            raise RuntimeError(f'Unsupported workflow element in visitInner_workflow_element(): {type(element)}')

    def visitCall(self, ctx: WdlParser.CallContext):
        """
        Pattern: CALL call_name call_alias? (call_afters)*  call_body?
        Example WDL syntax: call task_1 {input: arr=arr}

        Returns a tuple=(call_id, dict={task, alias, io}).
        """

        name = '.'.join(identifier.getText() for identifier in ctx.call_name().Identifier())
        alias = ctx.call_alias().Identifier().getText() if ctx.call_alias() else name
        afters = None  # Newly added feature. To be implemented by Toil.

        body = OrderedDict({  # kvp generator
            input_.Identifier().getText(): self.visitExpr(input_.expr())
            for input_ in ctx.call_body().call_inputs().call_input()

            # check if {} and {input: ...} are provided
        }) if ctx.call_body() and ctx.call_body().call_inputs() else OrderedDict()

        self.call_number += 1
        return f'call{self.call_number}', {
            'task': name,
            'alias': alias,
            'io': body
        }

    def visitScatter(self, ctx: WdlParser.ScatterContext):
        """
        Pattern: SCATTER LPAREN Identifier In expr RPAREN LBRACE inner_workflow_element* RBRACE
        Example WDL syntax: scatter ( i in items) { ... }

        Returns a tuple=(scatter_id, dict={item, collection, body})
        """
        item = ctx.Identifier().getText()
        expr = self.visitExpr(ctx.expr())
        body = OrderedDict()
        for element in ctx.inner_workflow_element():
            name, contents = self.visitInner_workflow_element(element)
            body[name] = contents

        self.scatter_number += 1
        return f'scatter{self.scatter_number}', {
            'item': item,
            'collection': expr,
            'body': body
        }

    def visitConditional(self, ctx: WdlParser.ConditionalContext):
        """

        """
        # TODO
        # return self.visitChildren(ctx)

    # Task section

    def visitTask(self, ctx: WdlParser.TaskContext):
        print('visitTask')
        # return super().visitChildren(ctx)

    #

    # Shared

    def visitUnbound_decls(self, ctx: WdlParser.Unbound_declsContext):
        """
        Contains an unbounded input declaration. E.g.: `String in_str`.

        Returns a tuple=(`name`, dict={`name`, `type`, `value`}), where `value` is None.
        """
        name = ctx.Identifier().getText()
        type_ = self.visitWdl_type(ctx.wdl_type())
        return name, OrderedDict({'name': name, 'type': type_, 'value': None})

    def visitBound_decls(self, ctx: WdlParser.Bound_declsContext):
        """
        Contains a bounded input declaration. E.g.: `String in_str = "some string"`.

        Returns a tuple=(`name`, dict={`name`, `type`, `value`}).
        """
        name = ctx.Identifier().getText()
        type_ = self.visitWdl_type(ctx.wdl_type())
        expr = self.visitChildren(ctx.expr())

        if isinstance(type_, WDLBooleanType) and expr in ('true', 'false'):
            expr = expr.capitalize()

        return name, OrderedDict({'name': name, 'type': type_, 'value': expr})

    def visitWdl_type(self, ctx: WdlParser.Wdl_typeContext):
        """
        Returns a WDLType instance.
        """
        return parse_wdl_type_from_context(ctx)

    def visitPrimitive_literal(self, ctx: WdlParser.Primitive_literalContext):
        """
        Returns the primitive literal as a string.
        """
        if isinstance(ctx.children[0], (TerminalNodeImpl,
                                        WdlParser.StringContext,
                                        WdlParser.NumberContext)):
            return ctx.children[0].getText()
        else:
            raise RuntimeError(f'Primitive literal has unknown child: {type(ctx.children[0])}.')

    # expr_infix0
    def visitLor(self, ctx: WdlParser.LorContext):
        """
        Logical OR infix.
        """
        lhs = self.visitInfix0(ctx.expr_infix0())
        if isinstance(ctx.expr_infix1(), WdlParser.LandContext):
            rhs = self.visitLand(ctx.expr_infix1())
        else:
            rhs = self.visitInfix1(ctx.expr_infix1())
        return f'{lhs} or {rhs}'

    # expr_infix1
    def visitLand(self, ctx: WdlParser.LandContext):
        """
        Logical AND infix.
        """
        lhs = self.visitInfix1(ctx.expr_infix1())
        rhs = self.visitInfix2(ctx.expr_infix2())
        return f'{lhs} and {rhs}'

    # expr_infix2
    def visitEqeq(self, ctx: WdlParser.EqeqContext):
        """
        Equality (==) expression.
        """
        pass

    # expr_infix2
    def visitNeq(self, ctx: WdlParser.NeqContext):
        """
        Inequality (!=) expression.
        """
        pass

    # expr_infix2
    def visitLte(self, ctx: WdlParser.LteContext):
        """
        Less than or equal to (<=) expression.
        """
        pass

    # expr_infix2
    def visitGte(self, ctx: WdlParser.GteContext):
        """
        Greater or equal to (>=) expression.
        """
        pass

    # expr_infix2
    def visitLt(self, ctx: WdlParser.LtContext):
        """
        Less than (<) expression.
        """
        pass

    # expr_infix2
    def visitGt(self, ctx: WdlParser.GtContext):
        """
        Greater than (>) expression.
        """
        pass

    # expr_infix3
    def visitAdd(self, ctx: WdlParser.AddContext):
        """
        Addition (+) expression.
        """
        pass

    # expr_infix3
    def visitSub(self, ctx: WdlParser.SubContext):
        """
        Subtraction (-) expression.
        """
        pass

    # expr_infix4
    def visitMul(self, ctx: WdlParser.MulContext):
        """
        Multiply (*) expression.
        """
        pass

    # expr_infix4
    def visitDivide(self, ctx: WdlParser.DivideContext):
        """
        Divide (/) expression.
        """
        pass

    # expr_infix4
    def visitMod(self, ctx: WdlParser.ModContext):
        """
        Modulo (%) expression.
        """
        pass

    # expr_core
    # see: https://github.com/w-gao/wdl/blob/main/versions/development/parsers/antlr4/WdlParser.g4#L121

    def visitApply(self, ctx: WdlParser.ApplyContext):
        # TODO
        pass

    # expr_core
    def visitArray_literal(self, ctx: WdlParser.Array_literalContext):
        """
        Pattern: LBRACK (expr (COMMA expr)*)* RBRACK
        """
        return f"[{', '.join(self.visitExpr(expr) for expr in ctx.expr())}]"

    # expr_core
    def visitPair_literal(self, ctx: WdlParser.Pair_literalContext):
        """
        Pattern: LPAREN expr COMMA expr RPAREN
        """
        return f"({self.visitExpr(ctx.expr(0))}, {self.visitExpr(ctx.expr(1))})"

    # expr_core
    def visitMap_literal(self, ctx: WdlParser.Map_literalContext):
        """
        Pattern: LBRACE (expr COLON expr (COMMA expr COLON expr)*)* RBRACE
        """
        # return f"{{{', '.join()}}}"
        pass

    # expr_core
    def visitStruct_literal(self, ctx: WdlParser.Struct_literalContext):
        """
        Pattern: Identifier LBRACE (Identifier COLON expr (COMMA Identifier COLON expr)*)* RBRACE
        """
        raise NotImplementedError(f'Structs are not implemented yet :(')

    # expr_core
    def visitIfthenelse(self, ctx: WdlParser.IfthenelseContext):
        """
        Ternary expression.

        Pattern: IF expr THEN expr ELSE expr
        """
        if_ = self.visitExpr(ctx.expr(0))
        condition = self.visitExpr(ctx.expr(1))
        else_ = self.visitExpr(ctx.expr(2))

        return f'({condition} if {if_} else {else_})'

    # expr_core
    def visitExpression_group(self, ctx: WdlParser.Expression_groupContext):
        """
        Pattern: LPAREN expr RPAREN
        """
        return f'({self.visitExpr(ctx.expr())})'

    # TODO
