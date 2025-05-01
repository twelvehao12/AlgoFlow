import os
import sys
import glob
import subprocess
import platform
import argparse
import difflib
import shutil
import re

TOOLS_DIR = 'tools'
SRC_DIR = 'src'
BUILD_DIR = 'build'
TEST_CASES_DIR = 'test_cases'

CXX = os.getenv('CXX', 'g++')
STD = 11
CXXFLAGS_DEBUG = [f'-std=c++{STD}', '-Wall', '-I', TOOLS_DIR, '-g']
CXXFLAGS_RELEASE = [f'-std=c++{STD}', '-Wall', '-I', TOOLS_DIR, '-O2']
LINKFLAGS = []


def log(msg):
    print(f"[Build Script] {msg}")


def get_output_path(problem_number):
    output_name = problem_number
    if platform.system() == 'Windows':
        output_name += '.exe'
    return os.path.join(BUILD_DIR, output_name)


def get_test_output_path(problem_number):
    test_dir = os.path.join(TEST_CASES_DIR, problem_number)
    if not os.path.exists(test_dir):
        log(f"No test cases found for problem {problem_number}.")
        return

    input_files = sorted(glob.glob(os.path.join(test_dir, 'input_*.txt')))
    if not input_files:
        log(f"No test cases found for problem {problem_number}.")
        return

    output_files = []
    for input_file in input_files:
        idx = os.path.basename(input_file).replace(
            'input_', '').replace('.txt', '')
        output_file = os.path.join(
            BUILD_DIR, f'test_output_{problem_number}_{idx}.txt')
        output_files.append(output_file)
    return output_files


def is_valid_problem_number(problem_number):
    if not problem_number:
        return False
    invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'
    if re.search(invalid_chars, problem_number):
        return False
    return True


def is_valid_util_name(name):
    if not name:
        return False
    invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'
    if re.search(invalid_chars, name):
        return False
    return True


def clean(problem_number=None):
    if problem_number is not None:
        exe_file = get_output_path(problem_number)
        if os.path.exists(exe_file):
            os.remove(exe_file)
            log(f"Deleted executable: {exe_file}")
        test_output_files = get_test_output_path(problem_number)
        if test_output_files:
            for output_file in test_output_files:
                if os.path.exists(output_file):
                    os.remove(output_file)
                    log(f"Deleted test output file: {output_file}")
        else:
            log(f"No test cases found for problem {problem_number}.")
    else:
        if os.path.exists(BUILD_DIR):
            shutil.rmtree(BUILD_DIR)
        os.makedirs(BUILD_DIR, exist_ok=True)
        log("Build directory cleaned.")


def find_source(problem_number):
    source_file = os.path.join(SRC_DIR, f"{problem_number}.cpp")
    if not os.path.exists(source_file):
        log(f"Source file for problem {problem_number} not found in {SRC_DIR}.")
        sys.exit(1)
    return source_file


def compile(problem_number, mode='debug'):
    source_file = find_source(problem_number)
    tool_sources = glob.glob(os.path.join(
        TOOLS_DIR, '**', '*.cpp'), recursive=True)

    os.makedirs(BUILD_DIR, exist_ok=True)
    output_exe = get_output_path(problem_number)

    cmd = [CXX]
    if mode == 'debug':
        cmd += CXXFLAGS_DEBUG
    else:
        cmd += CXXFLAGS_RELEASE
    cmd += ['-o', output_exe, source_file] + tool_sources + LINKFLAGS

    log(f"Compiling problem {problem_number} ({mode} mode)...")
    log("Running command: " + ' '.join(cmd))

    result = subprocess.run(cmd)
    if result.returncode != 0:
        log("Compilation failed.")
        sys.exit(1)
    else:
        log("Compilation successful.")


def run_executable(problem_number):
    output_exe = get_output_path(problem_number)
    if not os.path.exists(output_exe):
        log("Executable not found. Please compile first.")
        sys.exit(1)

    log(f"Running {output_exe}...")
    result = subprocess.run([output_exe], text=True)
    return result.returncode


def gdb_run(problem_number):
    output_exe = get_output_path(problem_number)
    if not os.path.exists(output_exe):
        log("Executable not found. Please compile first.")
        sys.exit(1)

    log(f"Starting gdb for {output_exe}...")
    subprocess.run(['gdb', '-ex', 'start', '--args', output_exe])


def record_test_case(problem_number):
    test_dir = os.path.join(TEST_CASES_DIR, problem_number)
    os.makedirs(test_dir, exist_ok=True)

    existing_inputs = glob.glob(os.path.join(test_dir, 'input_*.txt'))
    index = len(existing_inputs)
    input_file = os.path.join(test_dir, f'input_{index}.txt')
    output_file = os.path.join(test_dir, f'output_{index}.txt')

    log(f"Recording test case to {input_file} and {output_file}...")

    print("Enter input (Ctrl+Z to end):")
    user_input = sys.stdin.read()

    with open(input_file, 'w') as f:
        f.write(user_input)

    print("Enter expected output (Ctrl+Z to end):")
    result = sys.stdin.read()
    with open(output_file, 'w') as f:
        f.write(result)

    log("Test case recorded.")


def run_tests(problem_number):
    output_exe = get_output_path(problem_number)
    if not os.path.exists(output_exe):
        log("Executable not found. Please compile first.")
        sys.exit(1)

    test_dir = os.path.join(TEST_CASES_DIR, problem_number)
    if not os.path.exists(test_dir):
        log(f"No test cases found for problem {problem_number}.")
        return

    input_files = sorted(glob.glob(os.path.join(test_dir, 'input_*.txt')))
    if not input_files:
        log(f"No test cases found for problem {problem_number}.")
        return

    for input_file in input_files:
        idx = os.path.basename(input_file).replace(
            'input_', '').replace('.txt', '')
        output_file = os.path.join(test_dir, f'output_{idx}.txt')

        log(f"Running test case {idx}...")

        with open(input_file, 'r') as f:
            user_input = f.read()

        result = subprocess.run(
            [get_output_path(problem_number)],
            input=user_input,
            text=True,
            capture_output=True
        )

        temp_output = os.path.join(
            BUILD_DIR, f'test_output_{problem_number}_{idx}.txt')
        with open(temp_output, 'w') as f:
            f.write(result.stdout)

        with open(temp_output, 'r') as f:
            out_lines = f.readlines()
        with open(output_file, 'r') as f:
            exp_lines = f.readlines()

        if out_lines == exp_lines:
            log(f"Test case {idx} passed.")
        else:
            log(f"Test case {idx} failed. Differences:")
            d = difflib.ndiff(exp_lines, out_lines)
            for line in d:
                if line.startswith('+ '):
                    print(f"\033[91m{line}\033[0m", end='')
                elif line.startswith('- '):
                    print(f"\033[91m{line}\033[0m", end='')
                else:
                    print(line, end='')


def init_project():
    dirs_to_create = [SRC_DIR, TOOLS_DIR, BUILD_DIR, TEST_CASES_DIR]
    for d in dirs_to_create:
        os.makedirs(d, exist_ok=True)
    log("Project directories initialized.")

    utils_h = os.path.join(TOOLS_DIR, "utils.h")
    utils_cpp = os.path.join(TOOLS_DIR, "utils.cpp")

    if not os.path.exists(utils_h):
        with open(utils_h, 'w') as f:
            f.write(
                '#ifndef __TOOLS_UTILS_H\n#define __TOOLS_UTILS_H\n\nvoid say_hello();\n#endif\n')
        log("Created tools/utils.h")

    if not os.path.exists(utils_cpp):
        with open(utils_cpp, 'w') as f:
            f.write(
                '#include "utils.h"\n#include <iostream>\n\nvoid say_hello() {\n    std::cout << "Hello from utils!" << std::endl;\n}\n')
        log("Created tools/utils.cpp")


def create_new_problem(problem_number):
    if not is_valid_problem_number(problem_number):
        log("Problem number is invalid. It must not be empty and cannot contain invalid characters.")
        sys.exit(1)

    src_file = os.path.join(SRC_DIR, f"{problem_number}.cpp")
    if os.path.exists(src_file):
        log(f"Source file {src_file} already exists.")
        sys.exit(1)

    with open(src_file, 'w') as f:
        f.write(
            f'#include <iostream>\n#include "utils.h"\n\nint main() {{\n    say_hello();\n\n    // Add your code here\n    return 0;\n}}\n')
    log(f"Created {src_file}")

    test_dir = os.path.join(TEST_CASES_DIR, problem_number)
    os.makedirs(test_dir, exist_ok=True)
    log(f"Created test directory {test_dir}")


def delete_problem(problem_number):
    if not is_valid_problem_number(problem_number):
        log("Problem number is invalid. It must not be empty and cannot contain invalid characters.")
        sys.exit(1)

    src_file = os.path.join(SRC_DIR, f"{problem_number}.cpp")
    test_dir = os.path.join(TEST_CASES_DIR, problem_number)

    deleted = False

    clean(problem_number)

    if os.path.exists(src_file):
        os.remove(src_file)
        log(f"Deleted source file: {src_file}")
        deleted = True

    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        log(f"Deleted test directory: {test_dir}")
        deleted = True

    if not deleted:
        log(f"Problem {problem_number} does not exist. Nothing to delete.")


def add_util(util_name):
    if not is_valid_util_name(util_name):
        log("Util name is invalid. It must not be empty and cannot contain invalid characters.")
        sys.exit(1)

    h_file = os.path.join(TOOLS_DIR, f"{util_name}.h")
    cpp_file = os.path.join(TOOLS_DIR, f"{util_name}.cpp")
    utils_h_file = os.path.join(TOOLS_DIR, "utils.h")

    if os.path.exists(h_file) or os.path.exists(cpp_file):
        log(f"Util {util_name} already exists.")
        sys.exit(1)

    with open(h_file, 'w') as f:
        f.write(
            f'#ifndef __TOOLS_{util_name.upper()}_H\n#define __TOOLS_{util_name.upper()}_H\n#endif\n\n// Function declarations for {util_name}\nvoid {util_name}_init();\n')
    log(f"Created {h_file}")

    with open(h_file, 'w') as f:
        f.write(
            f'#ifndef __TOOLS_{util_name.upper()}_H\n#define __TOOLS_{util_name.upper()}_H\n\n// Function declarations for {util_name}\nvoid {util_name}_init();\n#endif\n')
    log(f"Created {h_file}")

    with open(utils_h_file, 'a') as f:
        f.write(f'\n#include "{util_name}.h"\n')
    log(f"Added #include to {utils_h_file}")


def remove_util(util_name):
    if not is_valid_util_name(util_name):
        log("Util name is invalid. It must not be empty and cannot contain invalid characters.")
        sys.exit(1)

    h_file = os.path.join(TOOLS_DIR, f"{util_name}.h")
    cpp_file = os.path.join(TOOLS_DIR, f"{util_name}.cpp")
    utils_h_file = os.path.join(TOOLS_DIR, "utils.h")

    deleted = False

    if os.path.exists(h_file):
        os.remove(h_file)
        log(f"Deleted {h_file}")
        deleted = True

    if os.path.exists(cpp_file):
        os.remove(cpp_file)
        log(f"Deleted {cpp_file}")
        deleted = True

    if not deleted:
        log(f"Util {util_name} does not exist. Nothing to delete.")
        return

    temp_file = utils_h_file + ".tmp"
    target_line = f'#include "{util_name}.h"'

    with open(utils_h_file, 'r') as fin, open(temp_file, 'w') as fout:
        for line in fin:
            if line.strip() != target_line.strip():
                fout.write(line)

    os.replace(temp_file, utils_h_file)
    log(f"Removed #include from {utils_h_file}")


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    subparsers.add_parser(
        'init',
        help='Initialize the base structure.',
    )

    new_parser = subparsers.add_parser(
        'new',
        help='Create a new problem template.',
        aliases=['n']
    )
    new_parser.add_argument('problem_number', type=str)

    compile_parser = subparsers.add_parser(
        'compile',
        help='Compile the source code.',
        aliases=['c', 'build', 'b']
    )
    compile_parser.add_argument('problem_number', type=str)
    compile_parser.add_argument(
        '--mode', choices=['debug', 'release'], default='debug')
    compile_parser.add_argument(
        '--run', action='store_true',
        help='Run the executable after compilation.'
    )
    compile_parser.add_argument(
        '--gdb', action='store_true',
        help='Run the executable in gdb after compilation.'
    )

    run_parser = subparsers.add_parser(
        'run',
        help='Run the compiled executable.',
        aliases=['r']
    )
    run_parser.add_argument('problem_number', type=str)

    gdb_parser = subparsers.add_parser(
        'gdb',
        help='Run the executable in gdb.',
        aliases=['g']
    )
    gdb_parser.add_argument('problem_number', type=str)

    test_parser = subparsers.add_parser(
        'test',
        help='Run test cases.',
        aliases=['t']
    )
    test_parser.add_argument('problem_number', type=str)
    test_parser.add_argument(
        '--record', action='store_true',
        help='Record a new test case.'
    )

    delete_parser = subparsers.add_parser(
        'delete',
        help='Delete the problem files.',
        aliases=['d', 'rm', 'remove']
    )
    delete_parser.add_argument('problem_number', type=str)

    clean_parser = subparsers.add_parser(
        'clean',
        help='Clean the build directory.',
    )
    clean_parser.add_argument('problem_number', type=str)

    util_parser = subparsers.add_parser(
        'util',
        help='Manage utility files.',
        aliases=['u']
    )
    util_parser.add_argument('util_name', type=str)
    util_parser.add_argument(
        '--add', action='store_true',
        help='Add a new utility.'
    )
    util_parser.add_argument(
        '--remove', action='store_true',
        help='Remove an existing utility.'
    )

    args = parser.parse_args()

    if args.command == 'init':
        init_project()
    elif args.command == 'new' or args.command in ['n']:
        create_new_problem(args.problem_number)
    elif args.command == 'compile' or args.command in ['c', 'build', 'b']:
        compile(args.problem_number, mode=args.mode)
        if args.run:
            run_executable(args.problem_number)
        if args.gdb:
            gdb_run(args.problem_number)
    elif args.command == 'run' or args.command in ['r']:
        run_executable(args.problem_number)
    elif args.command == 'gdb' or args.command in ['g']:
        gdb_run(args.problem_number)
    elif args.command == 'test' or args.command in ['t']:
        if args.record:
            record_test_case(args.problem_number)
        else:
            run_tests(args.problem_number)
    elif args.command == 'delete' or args.command in ['d', 'rm', 'remove']:
        delete_problem(args.problem_number)
    elif args.command == 'clean':
        if args.problem_number == 'all':
            clean()
        else:
            clean(args.problem_number)
    elif args.command == 'util' or args.command in ['u']:
        if args.add:
            add_util(args.util_name)
        elif args.remove:
            remove_util(args.util_name)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
