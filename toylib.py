# -*- coding: utf-8 -*-
"""
toylang lib function define
"""
from  toyvalue import *

class ToyLib:
    @staticmethod
    def print_(argv: list[Value]) -> list[Value]:
        if len(argv) > 0:
            for i in range(0, len(argv)-1):
                print(argv[i], end=' ')
            print(argv[-1], end='')

    @staticmethod
    def println_(argv: list[Value]) -> list[Value]:
        ToyLib.print_(argv)
        print()

    @staticmethod
    def input_(argv: list[Value]) -> list[Value]:
        prompt = ''
        if len(argv) > 0:
            prompt = argv[0]._val

        itype = 'str'
        if len(argv) > 1:
            itype = argv[1]
            if type(itype) is not TypeValue or itype._val not in ('int', 'float'):
                raise BaseError('arg[1] not `int` or `float`')
            itype = itype._val

        s = input(prompt)
        result = None
        try:
            if itype == 'str':
                result = StringValue(s)
            elif itype == 'int':
                result = NumValue(int(s), is_int=True)
            else:
                result = NumValue(float(s), is_int=False)
        except Exception:
            raise BaseError('pass input fail')
        return [result]

    @staticmethod
    def register(register_cb):
        BUILTIN_FUNCTIONS = [
            HostFunctionValue('print', ToyLib.print_),
            HostFunctionValue('println', ToyLib.println_),
            HostFunctionValue('input', ToyLib.input_),
        ]
        keys = [func.name for func in BUILTIN_FUNCTIONS]
        register_cb(keys, BUILTIN_FUNCTIONS, const=True)
