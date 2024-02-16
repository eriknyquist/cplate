from dataclasses import dataclass
from typing import List


def _contains_non_asterisks(s: str):
    for c in s:
        if c != '*':
            return True

    return False


@dataclass
class FunctionArgSpec:
    arg_type: str
    arg_name: str

    @classmethod
    def from_string(cls, spec: str):
        import pdb
        pdb.set_trace()

        arg_fields = spec.split()

        arg_type = None
        arg_name = None

        if len(arg_fields) < 2:
            raise ValueError(f"Invalid function argument '{arglist_field}'")

        arg_type = arg_fields[0]
        old_type_len = len(arg_type)
        arg_type = arg_type.rstrip('*')
        type_trailing_asterisks = old_type_len - len(arg_type)

        arg_name = arg_fields[-1]

        asterisks = '*' * type_trailing_asterisks

        if len(arg_fields) > 2:
            for field in arg_fields[1:-1]:
                stripped = field.strip()
                if _contains_non_asterisks(stripped):
                    raise ValueError(f"Invalid character(s) '{stripped}' in function argument")

                asterisks += stripped

        arg_name = asterisks + arg_name
        return FunctionArgSpec(arg_type=arg_type, arg_name=arg_name)


@dataclass
class FunctionSpec:
    return_type: str
    func_name: str
    args: List[FunctionArgSpec]

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

TEST_STR = "uint32_t my_cool_func  ( bool **flag, uint16_t* * *data  )"
print(FunctionSpec.from_string(TEST_STR))
