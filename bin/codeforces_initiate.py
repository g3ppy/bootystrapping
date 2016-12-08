#!/usr/bin/env python2

from lxml import html, etree
from slugify import slugify
import argparse
import requests
import os
import errno

def create_folder(name):
    if not args.write: return
    try:
        os.makedirs(name)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def create_folders(names):
    for name in names:
        create_folder(name)

def download_page(url):
    page = requests.get(url)
    tree = html.fromstring(page.text)
    return tree

def node_to_string(node):
    return u''.join([node.text] + map(etree.tostring, node.getchildren())).encode('utf-8').strip();

def parse_title(tree):
    page_title_node = tree.xpath('.//div[@class="title"]')[0]
    page_title = node_to_string(page_title_node)[3:]
    sluggy_title = slugify(page_title)

    if not args.quiet:
        print "Problem Name: {} ({})\n".format(page_title, sluggy_title)

    return sluggy_title

def parse_examples(tree):
    examples = []
    for (input_node, output_node) in zip(
        tree.xpath('.//div[contains(@class, "input")]/pre'),
        tree.xpath('.//div[contains(@class, "output")]/pre')):
        # Using ".text_content()" instead of just "text" for multiple line tests
        examples.append({"in": node_to_string(input_node).replace("<br/>", "\n"),
                        "out": node_to_string(output_node).replace("<br/>", "\n")})

        if examples[-1]["out"][-1] != '\n':
            examples[-1]["out"] += '\n'

    return examples

def write_examples(filename, examples):
    for i, example in enumerate(examples):
        in_file_name = '{}-{}.in'.format(filename, i)
        ok_file_name = '{}-{}.ok'.format(filename, i)

        if not args.quiet:
            print "Example {}:".format(i)
            print "Input ({}):\n{}".format(in_file_name, example["in"]),
            print "Output ({}):\n{}".format(ok_file_name, example["out"]),
            print

        if args.write:
            open(in_file_name, 'w').write(example["in"])
            open(ok_file_name, 'w').write(example["out"])

def initialize_cpp_file(cpp_filename):
    if not args.write: return
    if os.path.exists(cpp_filename):
        print "File {} already exists, not initiated".format(cpp_filename)
    else:
        os.system("init_template_codejam {}".format(cpp_filename))

def main():
    url = "http://codeforces.com/problemset/problem/{}/{}".format(args.contest, args.problem)
    problem_folder_name = "{}{}".format(args.contest, args.problem)
    tests_folder_name = os.path.join(problem_folder_name, "tests")

    create_folders([problem_folder_name, tests_folder_name])

    tree = download_page(url)
    examples = parse_examples(tree)
    problem_title = parse_title(tree)

    example_filename_prefix = os.path.join(tests_folder_name, problem_title)
    write_examples(example_filename_prefix, examples)

    cpp_filename = os.path.join(problem_folder_name, "{}.cpp".format(problem_title))
    initialize_cpp_file(cpp_filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Magic")
    parser.add_argument('--problem', '-p', required=True, help='problem letter, ex: A')
    parser.add_argument('--contest', '-c', required=True, help='contest number, ex: 281')
    parser.add_argument('--quiet', '-q', action='store_true', help='do not show examples on stdout')
    parser.add_argument('--write', '-w', default=False, action='store_true', help='write to file instead of just printing')
    args = parser.parse_args()
    main()
