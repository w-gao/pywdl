from antlr4 import InputStream, CommonTokenStream, FileStream

from pywdl.antlr.WdlLexer import WdlLexer
from pywdl.antlr.WdlParser import WdlParser

# A simple workflow that takes in some input and calls a task.
from pywdl.antlr2wf import AntlrToWorkflow

wf_1 = """
version development

workflow wf_1 {

}
"""


def test_wf_1():
    # lexer = WdlLexer(InputStream(wf_1))
    lexer = WdlLexer(FileStream('./workflow_1.wdl', 'utf-8'))
    stream = CommonTokenStream(lexer)
    parser = WdlParser(input=stream)
    tree = parser.document()

    visitor = AntlrToWorkflow()
    visitor.visit(tree)

    print('--- workflow dictionary ---')
    print(visitor.workflows_dictionary)

    print('--- tasks dictionary ---')
    print(visitor.tasks_dictionary)


if __name__ == '__main__':
    test_wf_1()
