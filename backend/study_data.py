import json
import os

class StudyData:
    """
    A class to manage study data with support for future storage in a file or database.
    """

    def __init__(self, config=None):
        """
        Initializes the StudyData object.

        Args:
            config (dict): Configuration for storage options (e.g., file or database).
        """
        self.data = {}
        self.config = config or {"storage_location": "memory"}  # Default to in-memory storage
        self.card_name = "study_data"  # Default card name for file storage
        self.location_path = os.path.join(os.getcwd(), "data/study_data.json")  # Default file path

    def __getitem__(self, key):
        """
        Retrieves the value associated with the given key.

        Args:
            key (str): The key to retrieve.

        Returns:
            The value associated with the key, or None if the key does not exist.
        """
        return self.data.get(key)

    def __setitem__(self, key, value):
        """
        Sets the value for the given key and stores it based on the configuration.

        Args:
            key (str): The key to set.
            value: The value to associate with the key.
        """
        self.set_study_data(key, value)

    def set_study_data(self, key, value):
        """
        Sets the value for the given key and stores it based on the configuration.

        Args:
            key (str): The key to set.
            value: The value to associate with the key.
        """
        self.data[key] = value
        if self.config["storage_location"] == "file":
            self.store_key_value_in_file(self.card_name, self.location_path, key, value)

    def store_key_value_in_file(self, card_name, file_path, key, value):
        """
        Stores the key-value pair in a JSON file.

        Args:
            card_name (str): The name of the card or section.
            file_path (str): The path to the file.
            key (str): The key to store.
            value: The value to store.
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    data = json.load(file)
            else:
                data = {}

            if card_name not in data:
                data[card_name] = {}

            data[card_name][key] = value

            with open(file_path, "w") as file:
                json.dump(data, file, indent=2)

            print(f"✅ Successfully stored {key}: {value} in {file_path}")
        except Exception as e:
            print(f"❌ Failed to store {key}: {value} in {file_path}: {e}")

    def load_from_file(self, file_path):
        """
        Loads study data from a JSON file.

        Args:
            file_path (str): The path to the file.
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    self.data = json.load(file).get(self.card_name, {})
                print(f"✅ Successfully loaded study data from {file_path}")
            else:
                print(f"⚠️ File {file_path} does not exist. Starting with empty data.")
        except Exception as e:
            print(f"❌ Failed to load study data from {file_path}: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def get_all_data(self):
        """
        Retrieves all stored study data.

        Returns:
            dict: The entire study data dictionary.
        """
        return self.data