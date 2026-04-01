student_scores = {
    "Anna": 78,
    "Ben": 92,
    "Chloe": 88,
    "Dylan": 92,
}

top_score = max(student_scores.items(), key=lambda x: x[1])[0]
print(top_score)

