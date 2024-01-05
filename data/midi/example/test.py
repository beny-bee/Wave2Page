from bs4 import BeautifulSoup

with open("combined.musicxml", 'r') as f:
    data = f.read()
    
data = BeautifulSoup(data, "xml")
scoreData = data.find("score-partwise")
parts = scoreData.find_all("part")

for part in parts:
    measures = part.find_all("measure")
    
    for idxMeasure, measure in enumerate(measures):
        totalDuration = 0
        if idxMeasure == 0:
            attr = measure.find("attributes")
            div = int(attr.find("divisions").string)
        notes = measure.find_all("note")
        for note in notes:
            totalDuration += int(note.find("duration").string)
        backups = measure.find_all("backup")
        for backup in backups:
            totalDuration -= int(backup.find("duration").string)
        print(totalDuration,div)
    print("-----------------------")