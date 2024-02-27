from dataclasses import dataclass
from typing import List


DEFAULT_VALS = {
    'char': '"\\0"',
    'signed char': '"\\0"',
    'unsigned char': '"\\0"',
    'int': '0',
    'signed int': '0',
    'signed': '0',
    'short': '0',
    'short int': '0',
    'signed short': '0',
    'signed short int': '0',
    'unsigned short int': '0',
    'signed short': '0',
    'long': '0',
    'long int': '0',
    'signed long int': '0',
    'signed long': '0',
    'long long': '0',
    'long long int': '0',
    'signed long long int': '0',
    'signed long long': '0',
    'int8_t': '0',
    'int16_t': '0',
    'int32_t': '0',
    'int64_t': '0',
    'int128_t': '0',
    'unsigned' : '0u',
    'unsigned int' : '0u',
    'unsigned long' : '0u',
    'unsigned long int' : '0u',
    'unsigned long long' : '0u',
    'unsigned long long int' : '0u',
    'uint8_t' : '0u',
    'uint16_t' : '0u',
    'uint32_t' : '0u',
    'uint64_t' : '0u',
    'uint128_t' : '0u',
    'float' : '0.0f',
    'double': '0.0',
    'long double': '0.0l',
    'bool': 'true'
}


def _contains_non_asterisks(s: str):
    for c in s:
        if c != '*':
            return True

    return False


@dataclass
class FunctionArgSpec:
    arg_type: str
    arg_name: str
    arg_name_alpha: str
    is_pointer: bool

    @classmethod
    def from_string(cls, spec: str):
        arg_fields = [x.strip() for x in spec.split()]

        arg_type = None
        arg_name = None

        if (len(arg_fields) == 1) and (arg_fields[0] == 'void'):
            return FunctionArgSpec(arg_type='void', arg_name=None, arg_name_alpha=None, is_pointer=False)

        if len(arg_fields) < 2:
            raise ValueError(f"Invalid function argument '{arglist_field}'")

        arg_name = arg_fields[-1]

        asterisks = ''
        asterisk_free_ix = None
        for i in range(len(arg_fields) - 2, -1, -1):
            if _contains_non_asterisks(arg_fields[i]):
                asterisk_free_ix = i
                break
            else:
                asterisks += arg_fields[i]

        if asterisk_free_ix is None:
            RuntimeError(f'Internal error when parsing function arguments {spec}')

        arg_type = ' '.join(arg_fields[:asterisk_free_ix + 1])
        old_type_len = len(arg_type)
        arg_type = arg_type.rstrip('*')
        type_trailing_asterisks = old_type_len - len(arg_type)

        asterisks += '*' * type_trailing_asterisks
        arg_name = asterisks + arg_name

        isptr = '*' in arg_name or asterisks

        return FunctionArgSpec(arg_type=arg_type, arg_name=arg_name,
                               arg_name_alpha=arg_name.strip('*'), is_pointer=isptr)


@dataclass
class FunctionSpec:
    return_type: str
    func_name: str
    args: List[FunctionArgSpec]

    @classmethod
    def from_string(cls, spec: str):
        stripped = spec.strip()
        if not stripped.endswith(')'):
            raise ValueError(f"Invalid spec (unterminated argument list): {spec}")

        stripped.rstrip(')')

        arglist_fields = stripped.split('(', maxsplit=1)
        if len(arglist_fields) != 2:
            raise ValueError(f"Invalid spec (unrecognized argument list): {spec}")

        arg_specs = []
        for arg_spec in arglist_fields[1].split(','):
            arg_specs.append(FunctionArgSpec.from_string(arg_spec))

    @classmethod
    def from_string(cls, spec: str):
        ret_fields = spec.split(maxsplit=1)
        if len(ret_fields) != 2:
            raise ValueError("Invalid spec (missing return type)")

        ret_type = ret_fields[0].strip()

        fname_fields = ret_fields[1].split('(', maxsplit=1)

        if len(fname_fields) != 2:
            raise ValueError("Invalid spec (missing argument list)")

        fname = fname_fields[0].strip()

        arglist_stripped = fname_fields[1].strip()

        if not arglist_stripped.endswith(')'):
            raise ValueError("Invalid spec (unterminated argument list)")

        arglist_fields = [x.strip() for x in arglist_stripped.rstrip(')').split(',')]

        arg_specs = []
        for arglist_field in arglist_fields:
            arg_specs.append(FunctionArgSpec.from_string(arglist_field))

        return FunctionSpec(return_type=ret_type, func_name=fname, args=arg_specs)

    def signature(self):
        if (len(self.args) == 1) and (self.args[0].arg_type == 'void'):
            arglist = 'void'
        else:
            arglist = ", ".join([f"{a.arg_type} {a.arg_name}" for a in self.args])

        return f"{self.return_type} {self.func_name}({arglist})"


if __name__ == "__main__":
    TEST_STR = "uint32_t my_cool_func  ( bool **flag, uint16_t* * *data  )"
    print(FunctionSpec.from_string(TEST_STR))
