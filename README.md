# Enhanced Classroom

- INCOMPLETE
- A desktop app aimed at faster browsing of classroom topics and search engine for classroom notes.
- An exercise to learn about apis and kivy
- Rename courses client side
- File structure

```
data
|- config.json
|- Folders with subject name
|- |- index.json
|- |- All materials
```

- config.json

```json
{
    "subjects": ["subject and its details as a dict"],
    "topics":[{"topicID":{"subjectID":..., "topicName":..., "topicDescription":...}}, ...]
}

```

- index.json

```json
{
    "subject": "subject name",
    "materials": [("material name","topicID"), ...]
}
```
