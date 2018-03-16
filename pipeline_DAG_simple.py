class Pipeline:
    def __init__(self):
        self.tasks = DAG()
        
    def task(self, depends_on=None):
        def inner(f):
            self.tasks.add(f)
            if depends_on:
                self.tasks.add(depends_on, f)
            return f
        return inner
    
    def run(self):
        scheduled = self.tasks.sort()
        completed = {}
        
        for task in scheduled:
            for node, values in self.tasks.graph.items():
                if task in values:
                    completed[task] = task(completed[node])
            if task not in completed:
                completed[task] = task()
        return completed

pipeline = Pipeline()

@pipeline.task()
def first():
    return 20

@pipeline.task(depends_on=first)
def second(x):
    return x * 2

@pipeline.task(depends_on=second)
def third(x):
    return x // 3

@pipeline.task(depends_on=second)
def fourth(x):
    return x // 4

outputs = pipeline.run()
print(outputs)