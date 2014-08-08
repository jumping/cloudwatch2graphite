import copy
import boto
import boto.ec2.cloudwatch
import arrow

def fetcher(config):
    aws = config['aws']
    aws_access_key_id = aws['aws_access_key_id']
    aws_secret_access_key = aws['aws_secret_access_key']
    region = aws['region']

    c = boto.ec2.cloudwatch.connect_to_region(region,
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key)

    metrics = config['metrics']['metrics']

    for metric in metrics:
        metric_result = fetch_metric(c,metric)
        print_metric(metric_result,metric,aws)

def print_metric(metric_result,metric_config,aws):
    metric_name = [] 
    if "carbonNameSpacePrefix" in metric_config:
        metric_name.append(metric_config["carbonNameSpacePrefix"])
    metric_name.append(metric_config["Namespace"].replace("/","."))
    metric_name.append(aws['region'])
    for name,value in metric_config["Dimensions"].iteritems():
        metric_name.append(value)
    metric_name.append(metric_config["MetricName"])

    for stat in  metric_config["Statistics"]:
        _metric_name = copy.deepcopy(metric_name)
        _metric_name.append(stat)
        _metric_name = ".".join(_metric_name)
        for metric in metric_result:
            metric_timestamp = arrow.get(metric["Timestamp"]).timestamp
            message = "%s %s %s" % (_metric_name,metric[stat],metric_timestamp)
            print(message)

def fetch_metric(conn,metric_config):
    period = 60

    interval = 11
    utc_now = arrow.utcnow()
    start_time = utc_now.replace(minutes=-interval).datetime
    end_time = utc_now.datetime

    metric_name = metric_config["MetricName"]
    namespace = metric_config["Namespace"]
    statistics = metric_config["Statistics"]
    dimensions = metric_config["Dimensions"]
    unit = metric_config["Unit"]

    kwargs = {
        "period" :period,
        "start_time" : start_time,
        "end_time" : end_time,
        "metric_name" : metric_name,
        "namespace" : namespace,
        "statistics" : statistics,
        "dimensions" : dimensions,
        "unit" : unit,
    }
    metric_result = conn.get_metric_statistics(**kwargs)

    _list = [(x["Timestamp"],x) for x in metric_result ]
    _list.sort()
    metric_result = [x[1] for x in _list]

    # Very often in Cloudwtch the last aggregated point is inaccurate and might be updated 1 or 2 minutes later
    # this is not a problem if we choose to overwrite it into graphite, so we read the 3 last points.
    if 'numberOfOverlappingPoints' in metric_config:
        len_metric_result = len(metric_result)
        num_overlapping_points = metric_result['numberOfOverlappingPoints']
        if len_metric_result > num_overlapping_points:
            metric_result = metric_result[len_metric_result-num_overlapping_points:]

    return metric_result




