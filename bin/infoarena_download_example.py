#!/usr/bin/python

from lxml import html
import argparse
import requests
import sys

def main():
    file_name = args.url.split('/')[-1]

    examples = []
    try:
        page = requests.get(args.url)
        tree = html.fromstring(page.text)
        for table in tree.xpath("//*[contains(@class, 'example')]"):
            for line in table[1:]:
                #print html.tostring(line, pretty_print=True)
                # Using ".text_content()" instead of just "text" for multiple line tests
                examples.append({"in": line[0].text_content(), "out":line[1].text_content()})

        for i, example in enumerate(examples):
            open('%d-%s.in' % (i, file_name), 'w').write(example["in"])
            open('%d-%s.out' % (i, file_name), 'w').write(example["out"])

            if not args.quiet:
                print "Example %d:" % i
                print "IN:"
                print example["in"],
                print "OUT:"
                print example["out"]
    except:
        print(sys.exc_info())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Magic")
    parser.add_argument('--url', '-u', help='example url: "http://www.infoarena.ro/problema/cristale"' )
    parser.add_argument('--quiet', '-q', action='store_true', help='do not show examples on stdout')
    args = parser.parse_args()
    main()
