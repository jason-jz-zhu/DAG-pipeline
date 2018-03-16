log = open('example_log.txt')
class Pipeline:
    def __init__(self):
        self.tasks = []
        
    def task(self, depends_on=None):
        idx = 0
        if depends_on:
            idx = self.tasks.index(depends_on) + 1
        def inner(f):
            self.tasks.insert(idx, f)
            return f
        return inner
    
    def run(self, input_):
        output = input_
        for task in self.tasks:
            output = task(output)
        return output
    
pipeline = Pipeline()

@pipeline.task()
def parse_logs(logs):
    return parse_log(logs)

@pipeline.task(depends_on=parse_logs)
def build_raw_csv(lines):
    return build_csv(lines, header=[
        'ip', 'time_local', 'request_type',
        'request_path', 'status', 'bytes_sent',
        'http_referrer', 'http_user_agent'
    ],
    file=io.StringIO())

@pipeline.task(depends_on=build_raw_csv)
def count_uniques(csv_file):
    return count_unique_request(csv_file)

@pipeline.task(depends_on=count_uniques)
def summarize_csv(lines):
    return build_csv(lines, header=['request_type', 'count'], file=io.StringIO())

log = open('example_log.txt')
summarized_file = pipeline.run(log)
print(summarized_file.readlines())