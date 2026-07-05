import json
import statistics

with open("q-calculate-variance.json") as f:
    data = json.load(f)

answer = statistics.variance(data)

print(round(answer, 2))
