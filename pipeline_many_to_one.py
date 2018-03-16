from collections import deque


class DAG:
    def __init__(self):
        self.graph = {}

    def in_degrees(self):
        in_degrees = {}
        for node in self.graph:
            if node not in in_degrees:
                in_degrees[node] = 0
            for pointed in self.graph[node]:
                if pointed not in in_degrees:
                    in_degrees[pointed] = 0
                in_degrees[pointed] += 1
        return in_degrees

    def sort(self):
        in_degrees = self.in_degrees()
        to_visit = deque()
        for node in self.graph:
            if in_degrees[node] == 0:
                to_visit.append(node)

        searched = []
        while to_visit:
            node = to_visit.popleft()
            for pointer in self.graph[node]:
                in_degrees[pointer] -= 1
                if in_degrees[pointer] == 0:
                    to_visit.append(pointer)
            searched.append(node)
        return searched

    def add(self, node, to=None):
        if node not in self.graph:
            self.graph[node] = []
        if to:
            if to not in self.graph:
                self.graph[to] = []
            self.graph[node].append(to)
        if len(self.sort()) != len(self.graph):
            raise Exception


class Pipeline:
    def __init__(self):
        self.tasks = DAG()

    def task(self, depends_on=None):
        def inner(f):
            self.tasks.add(f)
            if depends_on and isinstance(depends_on, list):
                for depend_on in depends_on:
                    self.tasks.add(depend_on, f)
            elif depends_on:
                self.tasks.add(depends_on, f)
            return f
        return inner

    def run(self):
        scheduled = self.tasks.sort()
        completed = {}
        #print(scheduled)
        for task in scheduled:
            args = []
            for node, values in self.tasks.graph.items():
                if task in values:
                    args.append(completed[node])
            if len(args) == 1:
                completed[task] = task(args[0])
            elif len(args) > 1:
                completed[task] = task(args)
            if task not in completed:
                completed[task] = task()
        return completed
