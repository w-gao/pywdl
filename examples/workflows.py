
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
                'value': None
            },
            'scatters': {
                'name': 'scatters',
                'type': 'Array[Int]',
                'value': '[1, 2, 3, 4, 5]'
            }
        },
        'UNIMPLEMENTED': {
        },
        'call0': {
            'task': 'task_1',
            'alias': 'task_1',
            'io': {
                'in_str': 'in_str'
            }
        },
        'scatter0': {
            'item': 'i',
            'collection': 'scatters',
            'body': {
                'call1': {
                    'task': 'task_2',
                    'alias': 'bar',
                    'io': {
                        'in_int': 'i'
                    }
                }
            }
        },
        'wf_outputs': [
            (
                'wf_out',
                {
                    'name': 'wf_out',
                    'type': 'Array[String]',
                    'value': None
                }
            )
        ]
    }
}
