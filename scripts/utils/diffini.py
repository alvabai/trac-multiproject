#!/usr/bin/env python

"""
Quick script to print differences between two trac configuration files, supports inhert as well.
"""

import os
import sys
from trac.config import Configuration


def diff(file1, file2, ignored_sections=None, ignore_absent=False):
    """
    :param file1: Filename
    :param file2: Filename
    :param list ignored_sections: List of ignored sections
    :param bool ignore_absent: Disables absent key reporting
    """
    if ignored_sections is None:
        ignored_sections = []

    if not os.path.exists(file1):
        raise ValueError('file %s does not exists' % file1)
    if not os.path.exists(file2):
        raise ValueError('file %s does not exists' % file2)

    conf1 = Configuration(file1)
    conf2 = Configuration(file2)

    fn1 = os.path.split(file1)[1]
    fn2 = os.path.split(file2)[1]

    conf1_sections = set(conf1.sections()) - set(ignored_sections)
    conf2_sections = set(conf2.sections()) - set(ignored_sections)

    for section in conf1.sections():
        if section not in conf2_sections:
            print 'SECTION: %s not in %s' % (section, fn2)

    default = object()
    for section in conf1_sections:
        for key, value1 in conf1.options(section):
            if not conf2.has_option(section, key):
                if not ignore_absent:
                    print '[%s] %s = %s is ABSENT from %s (but exists in %s)' % (section, key, value1, fn2, fn1)
            else:
                value2 = conf2.get(section, key, default)
                if value2 != value1 and value2 is not default:
                    print '[%s] %s = %s -> %s (%s -> %s)' % (section, key, value1, value2, fn1, fn2)


def main():
    if len(sys.argv) < 3:
        print 'Usage: diffini.py <file.ini> <file.ini> [-i IGNORE ABSENT] [IGNORED SECTIIONS]'
        print '       Displays differences from first file against second'
    ignore_absent = False
    ignored_sections = sys.argv[2:]
    if '-i' in ignored_sections:
        ignored_sections.remove('-i')
        ignore_absent = True
    diff(sys.argv[1], sys.argv[2], ignored_sections, ignore_absent)


if __name__ == '__main__':
    main()
