# -*- coding: utf-8 -*-
"""
toylang value define
NullValue    :
BoolValue    : _val
NumValue     : _val, is_int
StringValue  : _val
ListValue    :
MapValue     :
ObjectValue  :
TypeValue    : _val (type str)
HostFunction : f(argc, argv: list[Value]) -> list[Value]    # argc not need in py
"""

from toytoken import *
from toyerror import *


class Value:
    def __str__(self):
        pass

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self})'

    def type(self):
        return f'{self.__class__.__name__[:-5]}'


class NullValue(Value):
    def __str__(self):
        return 'null'


class BoolValue(Value):
    def __init__(self, _val):
        self._val = _val

    def __str__(self):
        return 'true' if self._val else 'false'


class NumValue(Value):
    def __init__(self, _val, is_int):
        self._val = _val
        self.is_int = is_int

    def __str__(self):
        return str(self._val)

    def type(self):
        return 'Int' if self.is_int else 'Float'

class StringValue(Value):
    def __init__(self, _val):
        self._val = _val

    def __str__(self):
        return self._val


class ListValue(Value):
    def __init__(self, _val):
        self._val = _val

    def __str__(self):
        return '[' + ', '.join(f'v' for v in self._val) + ']'


class MapValue(Value):
    def __init__(self, _val):
        self._val = _val

    def __str__(self):
        return '{' + ', '.join(f'{k}: {v}' for k, v in self._val.items()) + '}'


class ObjectValue(Value):
    def __init__(self, _val):
        self._val = _val

    def __str__(self):
        return '<object>'


class TypeValue(Value):
    def __init__(self, _val):
        self._val = _val

    def __str__(self):
        return self._val


class HostFunctionValue(Value):
    def __init__(self, name, _func):
        self.name = name
        self._func = _func

    def __str__(self):
        return f'{self.name}'


def init_builtin_typevalues(register_cb):
    BUILTIN_TYPEVALUES = [
        TypeValue('null'),
        TypeValue('bool'),
        TypeValue('int'),
        TypeValue('float'),
        TypeValue('string'),
        TypeValue('list'),
        TypeValue('map'),
        TypeValue('function'),
        TypeValue('object'),
    ]
    keys = [name._val for name in BUILTIN_TYPEVALUES]
    register_cb(keys, BUILTIN_TYPEVALUES, True)


class OpImpl:
    @staticmethod
    def eq(l, r):
        if type(l) != type(r):
            raise BaseError('operand not same type')
        return BoolValue(l._val == r._val)

    @staticmethod
    def lt(l, r):
        if type(l) != NumValue:
            raise BaseError('left operand not a number')
        if type(r) != NumValue:
            raise BaseError('right operand not a number')
        return BoolValue(l._val < r._val)

    @staticmethod
    def le(l, r):
        if type(l) != NumValue:
            raise BaseError('left operand not a number')
        if type(r) != NumValue:
            raise BaseError('right operand not a number')
        return BoolValue(l._val <= r._val)

    @staticmethod
    def add(l, r):
        if type(l) == NumValue:
            if type(r) != NumValue:
                raise BaseError('right operand not number')
            return NumValue(l._val + r._val, is_int=True if l.is_int and r.is_int else False)
        elif type(l) == StringValue:
            if type(r) not in (StringValue, NumValue):
                raise BaseError('right operand not number or string')
            return StringValue(l._val + str(r._val))
        else:
            raise BaseError('left operand not number or string')

    @staticmethod
    def sub(l, r):
        if type(l) != NumValue:
            raise BaseError('left operand not number')
        if type(r) != NumValue:
            raise BaseError('right operand not number')
        return NumValue(l._val - r._val, is_int=True if l.is_int and r.is_int else False)

    @staticmethod
    def mul(l, r):
        if type(l) != NumValue:
            raise BaseError('left operand not number')
        if type(r) != NumValue:
            raise BaseError('right operand not number')
        return NumValue(l._val * r._val, is_int=True if l.is_int and r.is_int else False)

    @staticmethod
    def div(l, r):
        if type(l) != NumValue:
            raise BaseError('left operand not number')
        if type(r) != NumValue:
            raise BaseError('right operand not number')
        if l.is_int and r.is_int:
            return NumValue(l._val // r._val, is_int=True)
        else:
            return NumValue(l._val / r._val, is_int=False)

    # @staticmethod
    # def pow_

    # @staticmethod
    # def mod

    # @staticmethod
    # def bshl

    # @staticmethod
    # def bshr

    # @staticmethod
    # def band

    # @staticmethod
    # def bxor

    # @staticmethod
    # def bor

    # @staticmethod
    # def and_

    # @staticmethod
    # def or_

    # @staticmethod
    # def is_

    # @staticmethod
    # def in_

    # @staticmethod
    def add_(v):
        if type(v) != NumValue:
            raise BaseError('operand not number')
        return v

    # @staticmethod
    def sub_(v):
        if type(v) != NumValue:
            raise BaseError('operand not number')
        return NumValue(-v._val, is_int=v.is_int)

    @staticmethod
    def not_(v):
        bvalue = OpImpl.value_to_bool(v)
        return BoolValue(not bvalue._val)

    # @staticmethod
    # def len_

    # @staticmethod
    # def bnot

    @staticmethod
    def value_to_bool(val):
        '''convert other value to bool
        '''
        if type(val) == NullValue:
            return BoolValue(False)
        elif type(val) == BoolValue:
            return val
        elif type(val) == NumValue:
            return BoolValue(val._val != 0)
        else:
            raise BaseError('cannot convert to bool')

    @staticmethod
    def is_num(val):
        return type(val) == NumValue


BINOP_IMPL_TABLE = {
    TokenType.EQ        : OpImpl.eq,        # TokenType.NE
    TokenType.LT        : OpImpl.lt,        # TokenType.GE
    TokenType.LE        : OpImpl.le,        # TokenType.GT
    TokenType.ADD       : OpImpl.add,
    TokenType.SUB       : OpImpl.sub,
    TokenType.MUL       : OpImpl.mul,
    TokenType.DIV       : OpImpl.div,
    # TokenType.POW       :
    # TokenType.MOD       :
    # TokenType.BSHL      :
    # TokenType.BSHR      :
    # TokenType.BAND      :
    # TokenType.BXOR      :
    # TokenType.BOR       :
    TokenType.SELF_ADD  : OpImpl.add,       # self_add is implemented by add
    TokenType.SELF_SUB  : OpImpl.sub,
    # TokenType.SELF_MUL  :
    # TokenType.SELF_DIV  :
    # TokenType.SELF_POW  :
    # TokenType.SELF_MOD  :
    # TokenType.SELF_BSHL :
    # TokenType.SELF_BSHR :
    # TokenType.SELF_BAND :
    # TokenType.SELF_BXOR :
    # TokenType.SELF_BOR  :
    # TokenType.AND       :
    # TokenType.OR        :
    # TokenType.IS        :
    # TokenType.IN        :
}


UNIOP_IMPL_TABLE = {
    TokenType.ADD       : OpImpl.add_,
    TokenType.SUB       : OpImpl.sub_,
    TokenType.NOT       : OpImpl.not_,
    # TokenType.LEN       :
    # TokenType.BNOT      :
}
