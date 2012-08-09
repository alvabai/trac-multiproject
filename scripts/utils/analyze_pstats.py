#!/usr/bin/env python
"""
Utility script to read cProfiler data, with pstats.

Example of use::
>>> analyze_pstats.py /var/www/trac/logs/requests-2012-*

This will print combined results, 100 top cumulative time results.

To see more use cases::
>>> analyze_pstats.py -h

Same can be obtained with interactive pstats run though::
>>> python -m pstats /var/www/trac/logs/requests-2012-*
>>> sort cumulative
>>> stats 100

"""
import pstats
import argparse

def main():
    parser = argparse.ArgumentParser(description="Analyze cProfiler dump files")
    parser.add_argument('files', metavar='files', nargs='+',
                        help='profiler file(s) to process')
    parser.add_argument('-s', '--sort', default='time',
                        choices=['stdname', 'nfl', 'pcalls', 'file', 'calls', 'time',
                                 'line', 'cumulative', 'module', 'name'],
                        help='sort by')
    parser.add_argument('-l', '--limit', default=100, type=int, help='limit to X results')
    args = parser.parse_args()

    stats = pstats.Stats(args.files[0])
    for f in args.files[1:]:
        stats.add(f)

    stats.sort_stats(args.sort)
    stats.print_stats(args.limit)


if __name__ == '__main__':
    main()
