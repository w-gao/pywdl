from antlr4 import FileStream
from tests.parserTests import parse


"""
Manual test. To be removed.
"""


def test_wf_1():
    wf, tasks = parse(FileStream('./wf_1.wdl', 'utf-8'))

    print('--- workflow dictionary ---')
    print(wf)

    print('--- tasks dictionary ---')
    print(tasks)


if __name__ == '__main__':
    test_wf_1()
