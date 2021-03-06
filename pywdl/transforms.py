from collections import OrderedDict

from pywdl.antlr.WdlParser import WdlParser
from pywdl.antlr.WdlParserVisitor import WdlParserVisitor
from antlr4.tree.Tree import TerminalNodeImpl

from pywdl.types import WDLBooleanType
from pywdl.utils import parse_wdl_type_from_context


class TransformHandler:
    """
    Implement this class to adjust how a WDL document is parsed.
    """

    def handle_type(self):
        """
        Calls when a WDL type is encountered.
        """
        #
        pass

    def handle_expr_apply(self, identifier: str, args: list):
        """
        Calls when a function call expression is encountered.
        """
        return f'{identifier}({", ".join(args)})'


class WdlTransformer(WdlParserVisitor):
    """
    Follow the syntax tree generated by Antlr4 and convert them to Python objects.
    """

    def __init__(self, handler: TransformHandler = None):
        """
        :param handler: Provide a custom handler to change the default behavior.
        """
        if not handler:
            handler = TransformHandler()

        self.handler = handler

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
        element = ctx.children[0]

        # workflow
        if isinstance(element, WdlParser.WorkflowContext):
            return self.visitWorkflow(element)
        # task
        elif isinstance(element, WdlParser.TaskContext):
            return self.visitTask(element)
        # struct
        elif isinstance(element, WdlParser.StructContext):
            # TODO: add support for structs.
            raise NotImplementedError('Struct is not supported.')
        # import_doc
        elif isinstance(element, WdlParser.Import_docContext):
            # TODO: add support for imports.
            raise NotImplementedError('Import other WDL files is not supported.')
        else:
            raise RuntimeError(f'Unrecognized document element in visitDocument(): {type(element)}')

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

            # input
            if isinstance(section, WdlParser.Workflow_inputContext):
                wf.setdefault('wf_declarations', OrderedDict()).update(self.visitWorkflow_input(section))
            # output
            elif isinstance(section, WdlParser.Workflow_outputContext):
                wf['wf_outputs'] = self.visitWorkflow_output(section)
            # inner_element (i.e.: non-input declarations, scatters, calls, and conditionals)
            elif isinstance(section, WdlParser.Inner_workflow_elementContext):
                wf_key, contents = self.visitInner_workflow_element(section)
                wf.setdefault(wf_key, {}).update(contents)
            # parameter_meta and meta (unsupported)
            elif isinstance(section, (
                    WdlParser.Parameter_meta_elementContext,
                    WdlParser.Meta_elementContext)):
                print('[Warning] `parameter_meta` and `meta` are not supported.')
            else:
                raise RuntimeError(f'Unrecognized workflow element in visitWorkflow(): {type(section)}')

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
        return dict(self.visitAny_decls(decl) for decl in ctx.any_decls())

    def visitWorkflow_output(self, ctx: WdlParser.Workflow_outputContext):
        """
        Contains an array of 'bound_decls' (unbound_decls not allowed).

        Example:
            output {
              String out_str = "output"
            }

        Returns a dict={name: decl}.
        """
        return dict(self.visitBound_decls(decl) for decl in ctx.bound_decls())

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
            return self.visitConditional(element)
        else:
            raise RuntimeError(f'Unrecognized workflow element in visitInner_workflow_element(): {type(element)}')

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
            body_key, contents = self.visitInner_workflow_element(element)
            body.setdefault(body_key, OrderedDict()).update(contents)

        self.scatter_number += 1
        return f'scatter{self.scatter_number}', {
            'item': item,
            'collection': expr,
            'body': body
        }

    def visitConditional(self, ctx: WdlParser.ConditionalContext):
        """
        Pattern: IF LPAREN expr RPAREN LBRACE inner_workflow_element* RBRACE
        Example WDL syntax: if (condition) { ... }

        Returns a tuple=(if_id, dict={expression, body})
        """
        # see https://github.com/openwdl/wdl/blob/main/versions/development/SPEC.md#conditionals

        expr = self.visitExpr(ctx.expr())

        body = OrderedDict()
        for element in ctx.inner_workflow_element():
            body_key, contents = self.visitInner_workflow_element(element)
            body.setdefault(body_key, OrderedDict()).update(contents)

        self.if_number += 1
        return f'if{self.if_number}', {
            'expression': expr,
            'body': body
        }

    # Task section

    def visitTask(self, ctx: WdlParser.TaskContext):
        """
        Root of a task definition. Contains an `identifier` and an array of
        `task_element`s.
        """
        identifier = ctx.Identifier().getText()
        task = self.tasks_dictionary.setdefault(identifier, OrderedDict())
        print(f'Visiting task: {identifier}')

        for element in ctx.task_element():
            section = element.children[0]

            # input
            if isinstance(section, WdlParser.Task_inputContext):
                task.setdefault('inputs', []).extend(self.visitTask_input(section))
            # output
            elif isinstance(section, WdlParser.Task_outputContext):
                task['outputs'] = self.visitTask_output(section)
            # command
            elif isinstance(section, WdlParser.Task_commandContext):
                task['raw_commandline'] = self.visitTask_command(section)
            # runtime
            elif isinstance(section, WdlParser.Task_runtimeContext):
                task['runtime'] = self.visitTask_runtime(section)
            # bound_decls
            elif isinstance(section, WdlParser.Bound_declsContext):
                # append to inputs, for Toil. These should be different from inputs, however.
                name, decl = self.visitBound_decls(section)
                task.setdefault('inputs', []).append(tuple(decl.values()))
            # hints, parameter_meta, and meta (unsupported)
            elif isinstance(section, (
                    WdlParser.Task_hintsContext,
                    WdlParser.Parameter_meta_elementContext,
                    WdlParser.Meta_elementContext)):
                print('[Warning] `hints`, `parameter_meta`, and `meta` are not supported.')
            else:
                raise RuntimeError(f'Unrecognized workflow element in visitWorkflow(): {type(section)}')

    def visitTask_input(self, ctx: WdlParser.Task_inputContext):
        """
        Contains an array of 'any_decls', which can be unbounded or bounded declarations.

        Example:
            input {
              String in_str = "twenty"
              Int in_int
            }

        Returns an array of tuple=(name, type, value)
        """
        inputs = []
        for decl in ctx.any_decls():
            name, decl = self.visitAny_decls(decl)
            inputs.append(tuple(decl.values()))
        return inputs

    def visitTask_output(self, ctx: WdlParser.Task_outputContext):
        """
        Contains an array of 'bound_decls' (unbound_decls not allowed).

        Example:
            output {
              String out_str = read_string(stdout())
            }

        Returns an array of tuple=(name, type, value)
        """
        inputs = []
        for decl in ctx.bound_decls():
            name, decl = self.visitBound_decls(decl)
            inputs.append(tuple(decl.values()))
        return inputs

    def visitTask_command(self, ctx: WdlParser.Task_commandContext):
        """
        Parses the command section of the WDL task.
        Contains a `string_part` plus any number of `expr_with_string`s.

        The following example command:
            'echo ${var1} ${var2} > output_file.txt'
        Has 3 parts:
                string_part: 'echo '
                expr_with_string, which has two parts:
                        expr_part: 'var1'
                        string_part: ' '
                expr_with_string, which has two parts:
                        expr_part: 'var2'
                        string_part: ' > output_file.txt'

        :return: A list=[] of strings representing the parts of the command:
            e.g. [string_part, expr_part, string_part, ...]
        """
        parts = []

        # add the first part
        str_part = self.visitTask_command_string_part(ctx.task_command_string_part())
        if str_part:
            parts.append(f"r'''{str_part}'''")

        for group in ctx.task_command_expr_with_string():
            expr_part, str_part = self.visitTask_command_expr_with_string(group)
            parts.append(expr_part)
            if str_part:
                parts.append(f"r'''{str_part}'''")

        return parts

    def visitTask_command_string_part(self, ctx: WdlParser.Task_command_string_partContext):
        """
        Returns a string representing the string_part.
        """
        # join here because a string that contains $, {, or } is split
        return ''.join(part.getText() for part in ctx.CommandStringPart())

    def visitTask_command_expr_with_string(self, ctx: WdlParser.Task_command_expr_with_stringContext):
        """
        Returns a tuple=(`expr_part`, `string_part`).
        """
        return (self.visitTask_command_expr_part(ctx.task_command_expr_part()),
                self.visitTask_command_string_part(ctx.task_command_string_part()))

    def visitTask_command_expr_part(self, ctx: WdlParser.Task_command_expr_partContext):
        """
        Contains an expression inside ~{expr}.

        Returns the expression.
        """
        return self.visitExpr(ctx.expr())

    def visitTask_runtime(self, ctx: WdlParser.Task_runtimeContext):
        """
        Contains an array of `task_runtime_kv`s.

        Returns a dict={key: value} where key can be 'container', 'cpu',
        'memory', 'cores', 'disks', etc.
        """
        pairs = OrderedDict()
        for kv in ctx.task_runtime_kv():
            key = kv.children[0].getText()
            pairs[key] = self.visitExpr(kv.expr())
        return pairs

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
        expr = self.visitExpr(ctx.expr())

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
        if isinstance(ctx.children[0], (TerminalNodeImpl,  # variables, most likely
                                        WdlParser.StringContext,
                                        WdlParser.NumberContext)):
            return ctx.children[0].getText()
        else:
            raise RuntimeError(f'Primitive literal has unknown child: {type(ctx.children[0])}.')

    def visitInfix0(self, ctx: WdlParser.Infix0Context):
        """
        Expression infix0 (LOR).
        """
        infix = ctx.expr_infix0()
        if isinstance(infix, WdlParser.LorContext):
            return self.visitLor(infix)
        return self.visitInfix1(infix)

    def visitLor(self, ctx: WdlParser.LorContext):
        """
        Logical OR expression.
        """
        lhs = self.visitInfix0(ctx)
        rhs = self.visitInfix1(ctx)
        return f'{lhs} or {rhs}'

    def visitInfix1(self, ctx: WdlParser.Infix1Context):
        """
        Expression infix1 (LAND).
        """
        infix = ctx.expr_infix1()
        if isinstance(infix, WdlParser.LandContext):
            return self.visitLand(infix)
        return self.visitInfix2(infix)

    def visitLand(self, ctx: WdlParser.LandContext):
        """
        Logical AND expresion.
        """
        lhs = self.visitInfix1(ctx)
        rhs = self.visitInfix2(ctx)
        return f'{lhs} and {rhs}'

    def visitInfix2(self, ctx: WdlParser.Infix2Context):
        """
        Expression infix2 (comparisons).
        """
        infix = ctx.expr_infix2()
        if isinstance(infix, WdlParser.EqeqContext):
            return self._visitInfix2(infix, '==')
        elif isinstance(infix, WdlParser.NeqContext):
            return self._visitInfix2(infix, '!=')
        elif isinstance(infix, WdlParser.LteContext):
            return self._visitInfix2(infix, '<=')
        elif isinstance(infix, WdlParser.GteContext):
            return self._visitInfix2(infix, '>=')
        elif isinstance(infix, WdlParser.LtContext):
            return self._visitInfix2(infix, '<')
        elif isinstance(infix, WdlParser.GtContext):
            return self._visitInfix2(infix, '>')
        # continue down our path
        return self.visitInfix3(infix)

    def _visitInfix2(self, ctx, operation: str):
        """
        :param operation: Operation as a string.
        """
        lhs = self.visitInfix2(ctx)
        rhs = self.visitInfix3(ctx)
        return f'{lhs} {operation} {rhs}'

    def visitInfix3(self, ctx: WdlParser.Infix3Context):
        """
        Expression infix3 (add/subtract).
        """
        infix = ctx.expr_infix3()
        if isinstance(infix, WdlParser.AddContext):
            return self._visitInfix3(infix, '+')
        elif isinstance(infix, WdlParser.SubContext):
            return self._visitInfix3(infix, '-')
        # continue down our path
        return self.visitInfix4(infix)

    def _visitInfix3(self, ctx, operation: str):
        """
        :param operation: Operation as a string.
        """
        lhs = self.visitInfix3(ctx)
        rhs = self.visitInfix4(ctx)
        return f'{lhs} {operation} {rhs}'

    def visitInfix4(self, ctx: WdlParser.Infix4Context):
        """
        Expression infix4 (multiply/divide/modulo).
        """
        infix = ctx.expr_infix4()
        if isinstance(infix, WdlParser.MulContext):
            return self._visitInfix4(infix, '*')
        elif isinstance(infix, WdlParser.DivideContext):
            return self._visitInfix4(infix, '/')
        elif isinstance(infix, WdlParser.ModContext):
            return self._visitInfix4(infix, '%')
        # continue down our path
        return self.visitInfix5(infix)

    def _visitInfix4(self, ctx, operation: str):
        """
        :param operation: Operation as a string.
        """
        lhs = self.visitInfix4(ctx)
        rhs = self.visitInfix5(ctx)
        return f'{lhs} {operation} {rhs}'

    # expr_core
    # see: https://github.com/w-gao/wdl/blob/main/versions/development/parsers/antlr4/WdlParser.g4#L121

    def visitApply(self, ctx: WdlParser.ApplyContext):
        """
        A function call expression.

        Pattern: Identifier LPAREN (expr (COMMA expr)*)? RPAREN
        """

        return self.handler.handle_expr_apply(
            identifier=ctx.Identifier().getText(),
            args=[self.visitExpr(arg) for arg in ctx.expr()]
        )

    def visitArray_literal(self, ctx: WdlParser.Array_literalContext):
        """
        Pattern: LBRACK (expr (COMMA expr)*)* RBRACK
        """
        return f"[{', '.join(self.visitExpr(expr) for expr in ctx.expr())}]"

    def visitPair_literal(self, ctx: WdlParser.Pair_literalContext):
        """
        Pattern: LPAREN expr COMMA expr RPAREN
        """
        return f"({self.visitExpr(ctx.expr(0))}, {self.visitExpr(ctx.expr(1))})"

    def visitMap_literal(self, ctx: WdlParser.Map_literalContext):
        """
        Pattern: LBRACE (expr COLON expr (COMMA expr COLON expr)*)* RBRACE
        """
        # return f"{{{', '.join()}}}"
        pass

    def visitStruct_literal(self, ctx: WdlParser.Struct_literalContext):
        """
        Pattern: Identifier LBRACE (Identifier COLON expr (COMMA Identifier COLON expr)*)* RBRACE
        """
        raise NotImplementedError(f'Structs are not implemented yet :(')

    def visitIfthenelse(self, ctx: WdlParser.IfthenelseContext):
        """
        Ternary expression.

        Pattern: IF expr THEN expr ELSE expr
        """
        if_true = self.visitExpr(ctx.expr(0))
        condition = self.visitExpr(ctx.expr(1))
        if_false = self.visitExpr(ctx.expr(2))

        # this should also work without parenthesis
        return f'({condition} if {if_true} else {if_false})'

    def visitExpression_group(self, ctx: WdlParser.Expression_groupContext):
        """
        Pattern: LPAREN expr RPAREN
        """
        return f'({self.visitExpr(ctx.expr())})'

    # TODO
