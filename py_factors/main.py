import ast
import re
from factor import Factorize
from pprint import pprint

TRUTHY_STRINGS = ['true', 't', 'y', 'yes', '1']

def is_true(s):
    return s.lower().strip() in TRUTHY_STRINGS

if __name__ == '__main__':
    use_cache = is_true(raw_input('Do you want to use caching [Y/N] (Default: Y)? ') or 'true')
    if use_cache:
        use_file_cache = is_true(raw_input('Do you want to use file caching [Y/N] (Default: Y)? ') or 'true')
    else:
        use_file_cache = False

    verbose = is_true(raw_input('Do you want verbose output [Y/N] (Default: N)? '))

    factorizer = Factorize(use_cache=use_cache, use_file_cache=use_file_cache, verbose=verbose)
    range_pattern = '(x|)range\([0-9]+,\s*[0-9]+(,\s*[0-9]+|)\)'

    while True:
        inp = raw_input('Please enter a comma-separated list of integers (Enter to exit program): ')
        if not inp:
            exit(0)
        # I strongly believe in parsing input to allow the user flexibility.
        if inp[0] == '[' and inp[-1] == ']':
            numbers = ast.literal_eval(inp)
        elif re.match(range_pattern, inp):
            # we are matching on a very specific pattern so in thi8s case eval is safe
            numbers = eval(inp)
        else:
            try:
                numbers = [int(i.strip()) for i in inp.split(',')]
            except Exception as e:
                print 'Unable to parse the list of numbers: %s' % e
                continue

        if not all(isinstance(i, int) for i in numbers):
            print "Unable to parse the list of numbers. Please make sure all numbers are integers."

        print "*** FACTORS OF ***"
        pprint(factorizer.get_factors_of(numbers))

        print "*** FACTORS FOR ***"
        pprint(factorizer.get_factors_for(numbers))