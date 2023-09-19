# -*- coding: utf-8 -*-
"""
toylang lib function define
"""
from  toyvalue import *

class ToyLib:
    @staticmethod
    def print_(argv: list[Value]) -> list[Value]:
        for v in argv:
            print(v, end=' ')
        print()

    @staticmethod
    def input_(argv: list[Value]) -> list[Value]:
        prompt = ''
        if len(argv) > 0:
            prompt = argv[0]._val
        s = input(prompt)
        result = [StringValue(s)]
        return result

    @staticmethod
    def register(table):
        table['print'] = HostFunctionValue('print', ToyLib.print_)
        table['input'] = HostFunctionValue('input', ToyLib.input_)
