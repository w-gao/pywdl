import textwrap
import unittest

from antlr4 import InputStream

from pywdl.antlr.WdlParser import WdlParser
from pywdl.antlr.WdlLexer import WdlLexer, CommonTokenStream
from pywdl.antlr2dict import AntlrToDict
from pywdl.types import WDLStringType


def heredoc(template, indent=''):
    template = textwrap.dedent(template)
    return template.replace('\n', '\n' + indent) + '\n'


def parse(stream):
    lexer = WdlLexer(stream)
    stream = CommonTokenStream(lexer)
    parser = WdlParser(input=stream)
    tree = parser.document()

    visitor = AntlrToDict()
    visitor.visit(tree)

    return visitor.workflows_dictionary, visitor.tasks_dictionary


class WdlTests(unittest.TestCase):
    pass


class WorkflowTests(WdlTests):
    """
    Unit tests related to the workflow section.
    """
    @unittest.skip
    def test_wf_input(self):
        """
        Test the workflow input section.
        """
        wf_input_1 = heredoc("""
            version development

            workflow wf_input_1 {
                input {
                  String in_str = "Hello"
                }
            }
        """)

        wf, _ = parse(InputStream(wf_input_1))

        expected_wf = {'wf_input_1': {
            'wf_declarations': [
                ('in_str', {
                    'name': 'in_str',
                    'type': WDLStringType(),
                    'value': '"Hello"'
                })
            ]
        }}

        self.assertEqual(wf, expected_wf)

    @unittest.skip
    def test_wf_output(self):
        """
        Test the workflow output section.
        """
        wf_input_1 = heredoc("""
            version development

            workflow wf_output_1 {
                output {
                  String in_str = "Hello"
                }
            }
        """)

        wf, _ = parse(InputStream(wf_input_1))

        expected_wf = {'wf_output_1': {
            'wf_outputs': [
                ('in_str', {
                    'name': 'in_str',
                    'type': WDLStringType(),
                    'value': '"Hello"'
                })
            ]
        }}

        self.assertEqual(wf, expected_wf)


class ExprTests(WdlTests):
    """
    Unit tests related to WDL expressions.
    """
    @staticmethod
    def get_wf_value(wf, wf_name, index: int):
        return wf.get(wf_name).get('wf_declarations')[index][1].get('value')

    def test_expr_infix_0(self):
        """
        Test expr_infix0, expr_infix1, and expression_group (logical OR, logical AND, and group).
        """
        wf_expr_infix_1 = heredoc("""
            version development

            workflow wf_expr_infix_0 {
              input {
                  Int n0 = 0
                  Int n5 = 5
                  Int n10 = 10
                  Boolean bool_or = n0 || n10
                  Boolean bool_and = n0 && n10
                  Boolean bool_or_and_1 = n0 || n10 && n5
                  Boolean bool_or_and_2 = (n0 || n10) && n5
                  Boolean bool_and_or_1 = n0 && n10 || n5
                  Boolean bool_and_or_2 = (n0 && n10) || n5  # no effect
                  Boolean bool_and_or_3 = n0 && (n10 || n5)
              }
            }
        """)

        wf, _ = parse(InputStream(wf_expr_infix_1))
        self.assertEqual(self.get_wf_value(wf, 'wf_expr_infix_0', 3), 'n0 or n10')  # bool_or
        self.assertEqual(self.get_wf_value(wf, 'wf_expr_infix_0', 4), 'n0 and n10')  # bool_and
        self.assertEqual(self.get_wf_value(wf, 'wf_expr_infix_0', 5), 'n0 or n10 and n5')  # bool_or_and_1
        self.assertEqual(self.get_wf_value(wf, 'wf_expr_infix_0', 6), '(n0 or n10) and n5')  # bool_or_and_2
        self.assertEqual(self.get_wf_value(wf, 'wf_expr_infix_0', 7), 'n0 and n10 or n5')  # bool_and_or_2
        self.assertEqual(self.get_wf_value(wf, 'wf_expr_infix_0', 8), '(n0 and n10) or n5')  # bool_and_or_1
        self.assertEqual(self.get_wf_value(wf, 'wf_expr_infix_0', 9), 'n0 and (n10 or n5)')  # bool_and_or_3

    def test_expr_array(self):
        wf_expr_array = heredoc("""
            version development

            workflow wf_expr_array {
              input {
                Array[Int] arr = [1, 2, 3, 4, 5]
              }
            }
        """)

        wf, _ = parse(InputStream(wf_expr_array))
        self.assertEqual(self.get_wf_value(wf, 'wf_expr_array', 0), '[1, 2, 3, 4, 5]')
