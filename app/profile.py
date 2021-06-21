import json
from pathlib import Path


class Profile:
    def __init__(self, user: str, level: int = 1, words: dict = None):
        self._name = user  # Can only be set when creating a profile
        self._path = user.lower().replace(" ", "_") + ".profile"
        self.level = level
        self.words = dict(words) if words else {}

    def __str__(self):
        return f"{self.display_name} @ level {self.level}"

    def __len__(self):
        """Returns the number of words "seen" by this profile"""
        return len(self.words)

    def __capitalise_string(self, input_object: str) -> str:
        return " ".join(w.capitalize() for w in input_object.split())

    def dumps(self) -> str:
        """Returns a JSON-formatted rendering of the profile"""
        return json.dumps(self, indent=4, default=lambda o: o.__dict__)

    def load(self, data: dict):
        """Loads data from a dictionary containing 'level' and 'words'"""
        self.level = data["level"]
        self.words = data["words"]

    def load_profile(self, path: str = None):
        """Loads profile data from a JSON file.

        If a path is provided AND we are able to open the file, then we update
        the default path with the provided value.
        """
        if not path:
            path = str(Path(self._path).resolve())

        with open(path) as profile_file:
            data = json.load(profile_file)
        self.load(data)
        self._path = str(Path(path).resolve())

    def profile_file_exists(self) -> bool:
        return Path(self._path).exists()

    @property
    def display_name(self):
        """Capitalizes the initial letter of each word in the name"""
        display_name = self.__capitalise_string(self._name)
        return display_name

    @property
    def path(self) -> str:
        return str(Path(self._path).resolve())


if __name__ == "__main__":
    user = Profile("test user")

    print("Profile as str:", user)
    print("Display Name:", user.display_name)
    print("Level: ", user.level)
    print("Words seen:", len(user))
    print("Profile path:", user.path)