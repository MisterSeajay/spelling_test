#!/usr/bin/python3
import argparse, os, pathlib, random, sys
import json, jsonpath
import pygame
from gtts import gTTS
from itertools import chain

MP3_PATH = pathlib.Path.cwd().joinpath("mp3_cache")
DIC_PATH = pathlib.Path.cwd().joinpath("dictionary.json").absolute().as_posix()


class Profile:
    def __init__(self, user):
        self.name = user
        self.level = 1
        self.words = {}

    def __str__(self):
        return f"{self.name}"

    def load(self, data):
        self.level = data["level"]
        self.words = data["words"]

    def dumps(self):
        return json.dumps(self, indent=4, default=lambda o: o.__dict__)


def main(user, list_level, list_name, questions):
    os.system("cls")
    create_path(MP3_PATH)
    dictionary = get_dictionary(DIC_PATH)
    definitions = get_definitions(dictionary)

    if not user:
        user = input("Please enter your name: ")

    profile = get_profile(str.lower(user))

    if not list_level:
        list_level = profile.level

    if list_name == "*":
        print(
            "Hello, %s. Today's test will be %d questions at level %d"
            % (profile.name, questions, list_level)
        )
    else:
        print(
            "Hello, %s. Today's test will be %d questions from the %s list(s)"
            % (profile.name, questions, list_name)
        )

    words = get_random_words(list_level, list_name, questions, dictionary, profile)

    count = 0

    for word in words:

        if not word in profile.words:
            profile.words[word] = 0

        count = count + 1
        mp3_file = get_mp3(word, MP3_PATH)

        pygame.mixer.init()
        pygame.mixer.music.load(mp3_file)

        attempts = 0
        attempt = ""
        while attempt != word:
            attempts = attempts + 1
            pygame.mixer.music.play()
            if word in definitions:
                print("Word %02d, attempt %02d: " % (count, attempts))
                attempt = input('Definition is "%s": ' % (definitions[word]))
            else:
                attempt = input("Word %02d, attempt %02d: " % (count, attempts))

        # A **lower** score is better (i.e. fewer attempts); getting a word
        # correct first time is the only way to reduce the score for that word.
        profile.words[word] = profile.words[word] + (attempts - 2)

    print("Well done, you've completed the test!\n")

    for word in words:
        print("Word: %s, score %02d" % (word, profile.words[word]))

    save_profile(profile)


def create_path(path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def get_profile(user):
    profile = Profile(user)
    path = pathlib.Path.cwd().joinpath("%s.profile" % (user)).absolute()
    if path.exists():
        with open(path) as profile_file:
            data = json.load(profile_file)
        profile.load(data)

    return profile


def save_profile(profile):
    path = pathlib.Path.cwd().joinpath("%s.profile" % (profile.name)).absolute()

    with open(path, "w") as profile_file:
        profile_file.writelines(profile.dumps())


def join_dict(*args):
    return dict(chain.from_iterable(d.items() for d in args))


def get_dictionary(path):
    with open(path) as json_file:
        return json.load(json_file)


def get_definitions(dictionary):
    definitions = {}
    jsonpath_filter = "$.dictionary[*].definitions"
    item_list = jsonpath.jsonpath(dictionary, jsonpath_filter)
    for item in item_list:
        definitions = join_dict(definitions, item)
    return definitions


def get_random_words(level, name, questions, dictionary, profile):

    if name == "*":
        jsonpath_filter = "$.dictionary[?(@.level==%d || @.level==%d)].words" % (
            level,
            level - 1,
        )
    else:
        jsonpath_filter = '$.dictionary[?(@.name == "%s")].words' % (name)

    words = jsonpath.jsonpath(dictionary, jsonpath_filter)

    if not words:
        print(jsonpath_filter)
        raise ValueError("No words returned")

    # flatten these dictionaries into one word list, skipping words that have
    # a negative score
    word_list = []
    for sublist in words:
        for item in sublist:
            if not item in profile.words:
                word_list.append(item)
            elif profile.words[item] > -1:
                word_list.append(item)

    # return a random sample of these words
    return (word_list[i] for i in random.sample(range(len(word_list)), questions))


def get_mp3(word, mp3_path):
    mp3_file = mp3_path.joinpath("%s.mp3" % word)
    if not mp3_file.exists():
        phrase = "Please spell the word: %s" % word
        tts = gTTS(phrase, lang="en-gb")
        tts.save(mp3_file.absolute().as_posix())
    return mp3_file.absolute().as_posix()


if __name__ == "__main__":
    # Read command line arguments
    parser = argparse.ArgumentParser(description="A simple spelling test!")
    parser.add_argument("--user", help="The name of the profile to use for the test")
    parser.add_argument(
        "--level", help="The level (school year) to test at", dest="list_level"
    )
    parser.add_argument(
        "--test",
        help="The named list of words you want to be tested on",
        default="*",
        dest="list_name",
    )
    parser.add_argument(
        "--questions", help="The number of words to test (Default 10)", default=10
    )
    args = parser.parse_args()

    main(**vars(args))