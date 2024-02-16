import os
from cplate import spec


HEADER_COMMENT = """
/**
 * @file {}
 * @author  Your Name Here
 * @brief   Description of file here
 */
"""


def _default_returnval(func_spec):
    try:
        return spec.DEFAULT_VALS[func_spec.return_type]
    except KeyError:
        raise ValueError(f"Invalid function return type '{func_spec.return_type}'")


def _c_file_contents(filename, func_specs):
    ret = HEADER_COMMENT.format(filename).lstrip() + "\n\n\n"

    impls = []

    for func_spec in func_specs:
        impl = func_spec.signature() + "\n{\n"
        if func_spec.return_type != 'void':
            retval = spec.DEFAULT_VALS[func_spec.return_type]
            impl += f"    return {retval};\n"

        impl += "}\n"
        impls.append(impl)

    ret += '\n'.join(impls)
    return ret


def generate_c_module(c_filename, h_filename, spec_lines=[''], root_dir='.'):
    func_specs = [spec.FunctionSpec.from_string(line) for line in spec_lines]

    if c_filename:
        c_filepath = os.path.join(root_dir, c_filename)
        with open(c_filepath, 'w') as fh:
            fh.write(_c_file_contents(c_filename, func_specs))

    if h_filename:
        h_filepath = os.path.join(root_dir, h_filename)
        with open(h_filepath, 'w') as fh:
            fh.write(_h_file_contents(h_filename, func_specs))


if __name__ == "__main__":
    spec_lines = [
        "uint32_t my_cool_func  ( bool **flag, unsigned short int* * *data  )",
        "bool my_cool_func2  (void)",
    ]

    generate_c_module('testfile.c', None, spec_lines)
