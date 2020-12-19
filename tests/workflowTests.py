import unittest
import textwrap
from antlr4 import InputStream, CommonTokenStream, FileStream
from pywdl.antlr.WdlLexer import WdlLexer
from pywdl.antlr.WdlParser import WdlParser
from pywdl.antlr2wf import AntlrToWorkflow
from pywdl.types import WDLStringType


def heredoc(template, indent=''):
    template = textwrap.dedent(template)
    return template.replace('\n', '\n' + indent) + '\n'


def parse(stream):
    lexer = WdlLexer(stream)
    stream = CommonTokenStream(lexer)
    parser = WdlParser(input=stream)
    tree = parser.document()

    visitor = AntlrToWorkflow()
    visitor.visit(tree)

    return visitor.workflows_dictionary, visitor.tasks_dictionary


def test_wf_1():
    wf, tasks = parse(FileStream('./wf_1.wdl', 'utf-8'))

    print('--- workflow dictionary ---')
    print(wf)

    print('--- tasks dictionary ---')
    print(tasks)


class WorkflowTests(unittest.TestCase):

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

        wf, tasks = parse(InputStream(wf_input_1))

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
        self.assertEqual(tasks, {})

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

        wf, tasks = parse(InputStream(wf_input_1))

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
        self.assertEqual(tasks, {})

    def test_expr_infix(self):
        wf_expr_infix_1 = heredoc("""
            version development

            workflow wf_expr_infix_1 {
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

                  # Array[Int] arr = [1, 2, 3]
              }            
            }
        """)

        wf, tasks = parse(InputStream(wf_expr_infix_1))
        print(wf.get('wf_expr_infix_1').get('wf_declarations')[3][1]['value'])  # bool_or
        print(wf.get('wf_expr_infix_1').get('wf_declarations')[4][1]['value'])  # bool_and
        print(wf.get('wf_expr_infix_1').get('wf_declarations')[5][1]['value'])  # bool_or_and_1
        print(wf.get('wf_expr_infix_1').get('wf_declarations')[6][1]['value'])  # bool_or_and_2
        print(wf.get('wf_expr_infix_1').get('wf_declarations')[7][1]['value'])  #
        print(wf.get('wf_expr_infix_1').get('wf_declarations')[8][1]['value'])  #
        print(wf.get('wf_expr_infix_1').get('wf_declarations')[9][1]['value'])  #
        # print(wf.get('wf_expr_infix_1').get('wf_declarations')[10][1]['value'])  # arr


if __name__ == '__main__':
    unittest.main()
    # test_wf_1()
