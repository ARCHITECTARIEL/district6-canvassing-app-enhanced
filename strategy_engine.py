# precinct_strategy_engine.py
import json
from datetime import datetime

class PrecinctStrategyEngine:
    def __init__(self, filepath):
        self.filepath = filepath
        self._load()

    def _load(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = []

    def _save(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2)

    def get_all_precincts(self):
        return self.data

    def get_precinct(self, precinct_id):
        return next((p for p in self.data if p['precinct_id'] == precinct_id), None)

    def update_precinct(self, precinct_id, updates):
        precinct = self.get_precinct(precinct_id)
        if precinct:
            precinct.update(updates)
            precinct['last_updated'] = datetime.now().isoformat()
            self._save()
            return True
        return False

    def add_precinct(self, precinct_entry):
        if self.get_precinct(precinct_entry['precinct_id']) is None:
            precinct_entry['last_updated'] = datetime.now().isoformat()
            self.data.append(precinct_entry)
            self._save()
            return True
        return False

    def delete_precinct(self, precinct_id):
        original_len = len(self.data)
        self.data = [p for p in self.data if p['precinct_id'] != precinct_id]
        if len(self.data) < original_len:
            self._save()
            return True
        return False
