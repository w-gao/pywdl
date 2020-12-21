# wf_1 output

wf_1_wf_dict = {
    'wf_1': {
        'wf_declarations': {
            'in_str': {
                'name': 'in_str',
                'type': 'String',
                'value': '"hi"'
            },
            'in_str_opt': {
                'name': 'in_str_opt',
                'type': 'String',
                'value': None
            },
            'in_int': {
                'name': 'in_int',
                'type': 'Int',
                'value': None
            },
            'in_bool': {
                'name': 'in_bool',
                'type': 'Boolean',
                'value': 'True'
            },
            'in_arr': {
                'name': 'in_arr',
                'type': 'Array[String]',
                'value': None
            },
            'in_pair': {
                'name': 'in_pair',
                'type': 'Pair[String, Int]',
                'value': None
            },
            'ternary_str': {
                'name': 'ternary_str',
                'type': 'String',
                'value': '("yes!" if in_int > 19 else "no :(")'
            },
            'scatters': {
                'name': 'scatters',
                'type': 'Array[Int]',
                'value': '[1, 2, 3, 4, 5]'
            }
        },
        'if0': {
            'expression': 'in_bool',
            'body': {
            }
        },
        'if1': {
            'expression': 'in_bool',
            'body': {
                'wf_declarations': {
                    'temp': {
                        'name': 'temp',
                        'type': 'String',
                        'value': '"Test"'
                    }
                }
            }
        },
        'call0': {
            'task': 't1',
            'alias': 't1',
            'io': {
                'in_str': 'temp'
            }
        },
        'scatter0': {
            'item': 'i',
            'collection': 'scatters',
            'body': {
                'call1': {
                    'task': 't2',
                    'alias': 'bar',
                    'io': {
                    }
                }
            }
        },
        'wf_outputs': {
            'wf_out': {
                'name': 'wf_out',
                'type': 'Array[Int]',
                'value': None
            }
        }
    }
}

wf_1_tasks_dict = {
    't1': {
        'inputs': [
            (
                'in_str',
                'String',
                None
            ),
            (
                'in_int',
                'Int',
                '20'
            ),
            (
                'in_float',
                'Float',
                '3.14'
            ),
            (
                'non_input_str',
                'String',
                '"yes"'
            )
        ],
        'raw_commandline': [
            "r'''\n  '''"
        ]
    },
    't2': {
        'raw_commandline': [
        ],
        'outputs': [
            (
                'num',
                'Int',
                '3'
            )
        ]
    },
    't3': {
        'raw_commandline': [
            'r\'\'\'\n    echo "line 1"\n    echo "line 2"\n    echo "line 3"\n  \'\'\''
        ],
        'runtime': {
            'container': '"ubuntu:latest"',
            'cpu': '1',
            'memory': '"3GB"'
        },
        'outputs': [
        ]
    },
    't4': {
        'inputs': [
            (
                'var1',
                'String',
                '"hello"'
            ),
            (
                'var2',
                'String',
                '"hello"'
            ),
            (
                'num',
                'Float',
                '1.9'
            )
        ],
        'raw_commandline': [
            "r'''\n    echo '''",
            'var1',
            "r''' '''",
            'var2',
            "r''' > output_file.txt\n  '''"
        ]
    }
}
