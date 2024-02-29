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
    returns_pointer: bool
    func_name: str
    args: List[FunctionArgSpec]

    @classmethod
    def from_string(cls, spec: str):
        stripped = spec.strip()
        if not stripped.endswith(')'):
            raise ValueError(f"Invalid spec (unterminated argument list): {spec}")

        print(spec)
        stripped = stripped.rstrip(')')

        arglist_fields = stripped.split('(', maxsplit=1)
        if len(arglist_fields) != 2:
            raise ValueError(f"Invalid spec (unrecognized argument list): {spec}")

        arg_specs = []
        for arg_spec in arglist_fields[1].split(','):
            print(arg_spec)
            arg_specs.append(FunctionArgSpec.from_string(arg_spec))
            print(arg_specs[-1])

        before_params = arglist_fields[0].strip()
        funcname_start_i = None

        for c in reversed(range(len(before_params))):
            char = before_params[c]
            if (not char.isidentifier()) and (not char.isdigit()):
                break

            funcname_start_i = c

        if funcname_start_i is None:
            raise ValueError(f"Invalid spec (bad function name '{before_params}')")

        func_name = before_params[funcname_start_i:]
        if not func_name.isidentifier():
            raise ValueError(f"Invalid spec (invalid function name '{func_name}')")

        ret_type = before_params[:funcname_start_i].strip()
        ret_fields = ret_type.split('*')
        star_count = 0 if len(ret_fields) <= 1 else len(ret_fields) - 1
        ret_is_pointer = star_count > 0

        cleaned_ret_type = ret_fields[0].rstrip()
        if star_count > 0:
            cleaned_ret_type += ' ' + ('*' * star_count)

        return FunctionSpec(cleaned_ret_type, ret_is_pointer, func_name, arg_specs)

    def signature(self):
        if (len(self.args) == 1) and (self.args[0].arg_type == 'void'):
            arglist = 'void'
        else:
            arglist = ", ".join([f"{a.arg_type} {a.arg_name}" for a in self.args])

        space = "" if self.returns_pointer else " "
        return f"{self.return_type}{space}{self.func_name}({arglist})"


if __name__ == "__main__":
    TEST_STR = "uint32_t my_cool_func  ( bool **flag, uint16_t* * *data  )"
    print(FunctionSpec.from_string(TEST_STR))
