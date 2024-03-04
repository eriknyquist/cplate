import os
from cplate import spec


HEADER_COMMENT = """
/**
 * @file    {}
 * @author  Your Name Here
 * @brief   Description of file here
 */
"""


def _default_returnval(func_spec, config):
    try:
        return spec.DEFAULT_VALS[func_spec.return_type]
    except KeyError:
        raise ValueError(f"Invalid function return type '{func_spec.return_type}'")


def _c_file_contents(filename, func_specs, config, h_filename=None):
    ret = ""

    if config.header_comment:
        ret += config.header_comment + ("\n" * config.blank_line_count)

    ret += HEADER_COMMENT.format(filename).lstrip() + ("\n" * config.blank_line_count)

    impls = []

    for func_spec in func_specs:
        impl = ""
        if h_filename:
            impl += f"/**\n * @see #{h_filename}\n */\n"

        impl += func_spec.signature() + "\n{\n"
        if func_spec.return_type != 'void':
            if func_spec.returns_pointer:
                retval = "NULL"
            else:
                retval = spec.DEFAULT_VALS[func_spec.return_type]

            impl += f"    return {retval};\n"

        impl += "}\n"
        impls.append(impl)

    ret += '\n\n'.join(impls)
    return ret


def _doxygen_docs(func_spec, config):
    ret = "/**\n * Function description\n"

    longest_argname_len = 0

    if func_spec.args[0].arg_type != "void":
        ret += " *\n"
        argname_lens = []

        for arg_spec in func_spec.args:
            length = len(arg_spec.arg_name_alpha)
            argname_lens.append((arg_spec, length))
            if length > longest_argname_len:
                longest_argname_len = length

        for arg_spec, length in argname_lens:
            spaces = " " * ((longest_argname_len - length) + 2)
            ret += f" * @param {arg_spec.arg_name.lstrip('*')}" + spaces + "Parameter description\n"

    if func_spec.return_type != "void":
        ret += " *\n"
        ret += " * @return  Return description\n"

    ret += " */"

    return ret

def _h_file_contents(filename, func_specs, config):
    ret = ""

    if config.header_comment:
        ret += config.header_comment + ("\n" * config.blank_line_count)

    ret += HEADER_COMMENT.format(filename).lstrip() + "\n\n"

    guard_name = filename.replace('.', '_').upper()
    ret += f'#ifndef {guard_name}\n'
    ret += f'#define {guard_name}\n\n\n'

    impls = []

    for func_spec in func_specs:
        impl = _doxygen_docs(func_spec, config) + "\n" + func_spec.signature() + ";\n\n"
        impls.append(impl)

    ret += '\n'.join(impls)
    ret += f'\n#endif // {guard_name}'
    return ret


def generate_c_module(c_filename, h_filename, config, spec_lines=[''], root_dir='.'):
    func_specs = [spec.FunctionSpec.from_string(line) for line in spec_lines]

    if c_filename:
        c_filepath = os.path.join(root_dir, c_filename)
        with open(c_filepath, 'w') as fh:
            fh.write(_c_file_contents(c_filename, func_specs, config, h_filename))

    if h_filename:
        h_filepath = os.path.join(root_dir, h_filename)
        with open(h_filepath, 'w') as fh:
            fh.write(_h_file_contents(h_filename, func_specs, config))


if __name__ == "__main__":
    spec_lines = [
        "long double *my_cool_func  ( bool **flagsybagsy, unsigned short int* * *data  )",
        "bool my_cool_func2  (void)",
        "void my_cool_func3  (void)",
        "unsigned long * **my_cool_func4(bool huh)",
    ]

    generate_c_module('testfile.c', 'testfile.h', spec_lines)
