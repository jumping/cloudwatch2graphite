import argparse
import os
import json
from version import __version__
from fetcher import Fetcher
#import lock

def main():
    parser = argparse.ArgumentParser(description="cloudwatch2graphite will output graphite counters for a list of AWS Cloudwatch metrics")
    parser.add_argument('--version', action='version', version='%(prog)s '+__version__)
    parser.add_argument("--region",required=False)
    parser.add_argument("--aws",required=False)
    parser.add_argument("--metrics",required=True)
    parser.add_argument("--start_time",required=False,help="start time of metrics like as: 2015-12-17 19:06:00")
    parser.add_argument("--end_time",required=False,help="end time of metrics like as: 2015-12-18 11:59:59")

    args = parser.parse_args()
    #if not os.path.exists(args.aws) or not os.path.exists(args.metrics):
    if not os.path.exists(args.metrics):
        print "aws file or metrics file not found"
        return 

    config = {}
    if args.aws:
        with open(args.aws) as f:
            config['aws'] = json.loads(f.read())
    #with open(args.aws) as f:
    #    config['aws'] = json.loads(f.read())
    with open(args.metrics) as f:
        config['metrics'] = json.loads(f.read())

    if args.region:
        config['aws']['region'] = args.region

    #lock.ProcessLock().lock()
    fetcher = Fetcher(config)
    if args.start_time and args.end_time:
        fetcher(start_time, end_time)
    else:
        fetcher()
    #lock.ProcessLock().unlock()

    return

if __name__ == '__main__':
    main()
