from datetime import datetime
import json
import io
import string

from pipeline import build_csv, Pipeline
from stop_words import stop_words

pipeline = Pipeline()

@pipeline.task()
def file_to_json():
    with open('hn_stories_2014.json', 'r') as f:
        data = json.load(f)
        stories = data['stories']
    return stories

@pipeline.task(depends_on=file_to_json)
def filter_stories(stories):
    def is_popular(story):
        return story['points'] > 50 and story['num_comments'] > 1 and not story['title'].startswith('Ask HN')
    
    return (
        story for story in stories
        if is_popular(story)
    )

@pipeline.task(depends_on=filter_stories)
def json_to_csv(stories):
    lines = []
    for story in stories:
        lines.append(
            (story['objectID'], datetime.strptime(story['created_at'], "%Y-%m-%dT%H:%M:%SZ"), story['url'], story['points'], story['title'])
        )
    return build_csv(lines, header=['objectID', 'created_at', 'url', 'points', 'title'], file=io.StringIO())

@pipeline.task(depends_on=json_to_csv)
def extract_titles(csv_file):
    reader = csv.reader(csv_file)
    header = next(reader)
    idx = header.index('title')
    
    return (line[idx] for line in reader)

@pipeline.task(depends_on=extract_titles)
def clean_title(titles):
    for title in titles:
        title = title.lower()
        title = ''.join(c for c in title if c not in string.punctuation)
        yield title

@pipeline.task(depends_on=clean_title)
def build_keyword_dictionary(titles):
    word_freq = {}
    for title in titles:
        for word in title.split(' '):
            if word and word not in stop_words:
                if word not in word_freq:
                    word_freq[word] = 1
                word_freq[word] += 1
    return word_freq

@pipeline.task(depends_on=build_keyword_dictionary)
def top_keywords(word_freq):
    freq_tuple = [
        (word, word_freq[word])
        for word in sorted(word_freq, key=word_freq.get, reverse=True)
    ]
    return freq_tuple[:100]

ran = pipeline.run()
print(ran[top_keywords])