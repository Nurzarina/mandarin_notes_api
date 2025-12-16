from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import csv

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Model
class Note(BaseModel):
    pinyin: str
    hanzi: str
    english: str
    malay:str

# JSON Save Function
def save_to_json(note: Note):
    data_file = "notes.json"

    if os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)

    else:
        data = []

    data.append(note.dict())

    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# CSV Save Function
def save_to_csv(note: Note):
    data_file = "notes.csv"

    file_exists = os.path.exists(data_file)

    with open(data_file, "a", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["pinyin", "hanzi", "english", "malay"])
        
        writer.writerow([note.pinyin, note.hanzi, note.english, note.malay])

# JSON read function
def read_notes_json():
    data_file = "notes.json"

    if not os.path.exists(data_file):
        return []
    
    with open(data_file, "r", encoding="utf-8") as f:
        return json.load(f)

# CSV read function
def read_notes_csv():
    data_file = "notes.csv"

    if not os.path.exits(data_file):
        return []

    results = []

    with open(data_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)

        return results

#  API Endpoint

# GET endpoint for JSON file
@app.get("/notes/json")
def get_notes_json():
    data = read_notes_json()
    return data

# GET endpoint for CSV file
@app.get("/notes/csv")
def get_notes_csv():
    data = read_notes_csv()
    return data

# POST endpoint
@app.post("/add-note")
def add_note(note: Note):
    #  Save in both JSON and CSV
    save_to_json(note)
    save_to_csv(note)

    return {"message" : "Note saved successfully!", "data": note}

# PUT endpoint
@app.put("/notes/{note_id}")
def edit_note(note_id: int, updated_note: Note):
    json_data = read_notes_json()
    csv_data = read_notes_csv()
    
    if note_id < 0 or note_id >=len(json_data):
        return {"error": "Note not found"}
    
    json_data[note_id] = updated_note.dict()
    csv_data[note_id] = updated_note.dict()

    save_to_json(json_data)
    save_to_csv(csv_data)

    return {
        "message": "Notes updated successfully",
        "id": note_id,
        "data": updated_note
    }

#DELETE endpoint
@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    json_data = get_notes_json()
    csv_data = get_notes_csv();

    if note_id < 0 or note_id >= len(json_data):
        return {"error": "Note not found"}

    json_deleted = json_data.pop(note_id)
    csv_deleted = csv_data.pop(note_id)

    get_notes_json(json_data)
    get_notes_csv(csv_data)

    return {
        "message": "Note deleted successfully",
        "deleted": json_deleted
    }
