# ccai/nlp/primitives.py

import json
from pathlib import Path
from typing import Dict, Optional, Tuple

class PrimitiveManager:
    """
    Loads and manages the knowledge of primitive property categories,
    differentiating between mutually exclusive 'slots' and non-exclusive 'tags'.
    """
    def __init__(self, primitives_file: Path):
        self.primitives_file = primitives_file
        # This now stores: { 'red': ('color', 'slots'), 'alive': ('state', 'tags') }
        self._category_map: Dict[str, Tuple[str, str]] = {}
        self._load_primitives()

    def _load_primitives(self):
        """Loads the JSON file and builds a reverse map for quick lookups."""
        try:
            with open(self.primitives_file, 'r') as f:
                data = json.load(f)
            
            for category_type in ['slots', 'tags']:
                for major_category in data.get(category_type, {}).values():
                    for sub_category, words in major_category.items():
                        for word in words:
                            self._category_map[word] = (sub_category, category_type)
            
            print(f"✅ PrimitiveManager loaded {len(self._category_map)} primitives.")
        except FileNotFoundError:
            print(f"⚠️ Warning: {self.primitives_file} not found. Primitive categorization will be disabled.")
        except json.JSONDecodeError:
            print(f"⚠️ Error: Could not parse {self.primitives_file}.")

    def get_info(self, word: str) -> Optional[Tuple[str, str]]:
        """
        Finds the primitive category and its type (slot/tag) for a given word.
        e.g., get_info('red') -> ('color', 'slots')
        e.g., get_info('alive') -> ('state', 'tags')
        """
        return self._category_map.get(word)
