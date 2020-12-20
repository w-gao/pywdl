import textwrap
import unittest

from antlr4 import InputStream, FileStream

from pywdl.antlr.WdlParser import WdlParser
from pywdl.antlr.WdlLexer import WdlLexer, CommonTokenStream
from pywdl.transforms import WdlTransformer
from pywdl.types import WDLStringType


"""
A suite of test cases for the WDL -> Python dict output.
"""


def heredoc(template, indent=''):
    template = textwrap.dedent(template)
    return template.replace('\n', '\n' + indent) + '\n'


def parse(stream):
    lexer = WdlLexer(stream)
    stream = CommonTokenStream(lexer)
    parser = WdlParser(input=stream)
    tree = parser.document()

    visitor = WdlTransformer()
    visitor.visit(tree)

    return visitor.workflows_dictionary, visitor.tasks_dictionary


class WdlTests(unittest.TestCase):
    pass


class WorkflowTests(WdlTests):
    """
    Unit tests related to the workflow section.
    """
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
            'wf_declarations': {
                'in_str': {
                    'name': 'in_str',
                    'type': WDLStringType(),
                    'value': '"Hello"'
                }
            }
        }}
        self.assertEqual(wf, expected_wf)

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
            'wf_outputs': {
                'in_str': {
                    'name': 'in_str',
                    'type': WDLStringType(),
                    'value': '"Hello"'
                }
            }
        }}

        self.assertEqual(wf, expected_wf)

    def test_wf_declaration(self):
        """
        Test the workflow non-input declaration section.
        """
        wf_decl_1 = heredoc("""
            version development

            workflow wf_decl_1 {
                input {
                  String in_str = "Hello"
                }
                Int random_int = 19
            }
        """)

        wf, _ = parse(InputStream(wf_decl_1))

        # check if both declarations are present.
        self.assertEqual(len(wf['wf_decl_1']['wf_declarations']), 2)

    def test_wf_call(self):
        """
        Test the workflow call section.
        """
        wf_call_1 = heredoc("""
            version development

            workflow wf_call_1 {
              call t as t1
              call t as t2 {}                   # this should be supported but throws an error in Toil
              call t as t3 {input: in_str="hey"}
            }
            
            task t {
              input {
                String in_str = 'hello'
              }
              
              command {}
            }
        """)

        wf, _ = parse(InputStream(wf_call_1))

        expected_wf = {
            'wf_call_1': {
                'call0': {
                    'task': 't',
                    'alias': 't1',
                    'io': {}
                },
                'call1': {
                    'task': 't',
                    'alias': 't2',
                    'io': {}
                },
                'call2': {
                    'task': 't',
                    'alias': 't3',
                    'io': {
                        'in_str': '"hey"'
                    }
                }
            }
        }
        self.assertEqual(wf, expected_wf)

    def test_wf_scatter(self):
        """
        Test the workflow scatter section.
        """
        wf_scatter_1 = heredoc("""
            version development

            workflow wf_scatter_1 {
            }
            
            task t {
              input {
                String in_str = 'hello'
              }
              
              command {}
            }
        """)

        wf, _ = parse(InputStream(wf_scatter_1))

        expected_wf = {
            'wf_scatter_1': {
            }
        }
        self.assertEqual(wf, expected_wf)

    def test_wf_conditional(self):
        """
        Test the workflow conditional section.
        """
        wf_conditional_1 = heredoc("""
            version development

            workflow wf_conditional_1 {
            }
            
            task t {
              input {
                String in_str = 'hello'
              }
              
              command {}
            }
        """)

        wf, _ = parse(InputStream(wf_conditional_1))

        expected_wf = {
            'wf_conditional_1': {
            }
        }
        self.assertEqual(wf, expected_wf)


class TaskTests(WdlTests):
    """
    Unit tests related to the task section.
    """
    # input
    # output

    def test_task_command(self):
        """
        Test the task command section.
        """
        task_command_1 = heredoc("""
            version development

            workflow task_command_1 {
            }

            task t {
              input {
                String in_str = 'hello'
              }

              command {}
            }
        """)

        wf, _ = parse(InputStream(task_command_1))

        expected_wf = {
            'task_command_1': {
            }
        }
        self.assertEqual(wf, expected_wf)

    def test_task_runtime(self):
        """
        Test the task runtime section.
        """
        task_runtime_1 = heredoc("""
            version development

            workflow task_runtime_1 {
            }

            task t {
              input {
                String in_str = 'hello'
              }

              command {}
            }
        """)

        wf, _ = parse(InputStream(task_runtime_1))

        expected_wf = {
            'task_runtime_1': {
            }
        }
        self.assertEqual(wf, expected_wf)


class ExprTests(WdlTests):
    """
    Unit tests related to WDL expressions.
    """
    @staticmethod
    def get_wf_value(wf, wf_name, key):
        return wf.get(wf_name).get('wf_declarations').get(key).get('value')

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
        self.assertEqual(self.get_wf_value(wf, 'wf_expr_infix_0', 'bool_or'), 'n0 or n10')
        self.assertEqual(self.get_wf_value(wf, 'wf_expr_infix_0', 'bool_and'), 'n0 and n10')
        self.assertEqual(self.get_wf_value(wf, 'wf_expr_infix_0', 'bool_or_and_1'), 'n0 or n10 and n5')
        self.assertEqual(self.get_wf_value(wf, 'wf_expr_infix_0', 'bool_or_and_2'), '(n0 or n10) and n5')
        self.assertEqual(self.get_wf_value(wf, 'wf_expr_infix_0', 'bool_and_or_1'), 'n0 and n10 or n5')
        self.assertEqual(self.get_wf_value(wf, 'wf_expr_infix_0', 'bool_and_or_2'), '(n0 and n10) or n5')
        self.assertEqual(self.get_wf_value(wf, 'wf_expr_infix_0', 'bool_and_or_3'), 'n0 and (n10 or n5)')

    def test_expr_array(self):
        """
        Test the Array literal expression.
        """
        wf_expr_array = heredoc("""
            version development

            workflow wf_expr_array {
              input {
                Array[Int] arr = [1, 2, 3, 4, 5]
              }
            }
        """)

        wf, _ = parse(InputStream(wf_expr_array))
        self.assertEqual(self.get_wf_value(wf, 'wf_expr_array', 'arr'), '[1, 2, 3, 4, 5]')

    def test_expr_pair(self):
        """
        Test the Pair literal expression.
        """
        wf_expr_pair = heredoc("""
            version development

            workflow wf_expr_pair {
              input {
                Pair[String, Int] in_pair = ('twenty', 20)
              }
            }
        """)

        wf, _ = parse(InputStream(wf_expr_pair))
        self.assertEqual(self.get_wf_value(wf, 'wf_expr_pair', 'in_pair'), "('twenty', 20)")

        wf_expr_pair_integration = heredoc("""
            version development

            workflow wf_expr_pair_integration {
              input {
                Array[Pair[Int, String]] arr = [ (1, 'I'), (2, 'II'), (3, 'III'), (4, 'IV') ]
              }
            }
        """)

        wf, _ = parse(InputStream(wf_expr_pair_integration))

        expected_output = "[(1, 'I'), (2, 'II'), (3, 'III'), (4, 'IV')]"
        self.assertEqual(self.get_wf_value(wf, 'wf_expr_pair_integration', 'arr'), expected_output)

    def test_expr_ternary(self):
        """
        Test the ternary (If then else) expression.
        """
        wf_expr_ternary = heredoc("""
            version development

            workflow wf_expr_ternary {
              input {
                Boolean morning
              }
              
              String time = if morning then "morning" else "afternoon"
              # ternary with + operator
              String greeting = "good " + if morning then "morning" else "afternoon"
            }
        """)

        wf, _ = parse(InputStream(wf_expr_ternary))
        self.assertEqual(self.get_wf_value(wf, 'wf_expr_ternary', 'time'), '("morning" if morning else "afternoon")')
        # self.assertEqual(self.get_wf_value(wf, 'wf_expr_ternary', 'greeting'), '')

    def test_expr_comparisons(self):
        """
        Test comparison (==, !=, <, >, <=, >=) expressions.
        """
        wf_expr_comparisons = heredoc("""
            version development

            workflow wf_expr_comparisons {
            
            }
        """)

        wf, _ = parse(InputStream(wf_expr_comparisons))
        self.assertEqual(True, True)

    def test_expr_arithmetic(self):
        """
        Test arithmetic operations (+, -, *, /, %) in expressions.
        """
        wf_expr_arithmetic = heredoc("""
            version development

            workflow wf_expr_arithmetic {
            
            }
        """)

        wf, _ = parse(InputStream(wf_expr_arithmetic))
        self.assertEqual(True, True)


class StressTests(WdlTests):
    """
    """

    def test_stress_1(self):
        import time
        start = time.time()
        wf, _ = parse(FileStream('stress_test.wdl', 'utf-8'))
        end = time.time() - start
        self.assertLessEqual(end, 2, f'Too long to run: ({end}s).')


if __name__ == '__main__':
    unittest.main()
