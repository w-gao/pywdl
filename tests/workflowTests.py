import unittest
import textwrap
from antlr4 import InputStream, CommonTokenStream, FileStream
from pywdl.antlr.WdlLexer import WdlLexer
from pywdl.antlr.WdlParser import WdlParser
from pywdl.antlr2wf import AntlrToWorkflow
from pywdl.types import WDLStringType


def heredoc(template, args=None, indent=''):
    if args is None:
        args = {}
    template = textwrap.dedent(template).format(**args)
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

    def test_wf_input(self):
        """
        Test the workflow input section.
        """
        wf_input_1 = heredoc("""
            version development
            
            workflow wf_input_1 {{
                input {{
                  String in_str = "Hello"
                }}
            }}
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

    def test_wf_output(self):
        """
        Test the workflow output section.
        """
        wf_input_1 = heredoc("""
            version development
            
            workflow wf_output_1 {{
                output {{
                  String in_str = "Hello"
                }}
            }}
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


if __name__ == '__main__':
    # unittest.main()
    test_wf_1()
