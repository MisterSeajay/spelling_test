#!/usr/bin/python3
import argparse, os, pathlib, random, sys, re
import json, jsonpath
import pygame
from profile import Profile  # local module
from gtts import gTTS
from itertools import chain

MP3_PATH = pathlib.Path.cwd().joinpath("mp3_cache")
DIC_PATH = pathlib.Path.cwd().joinpath("dictionary.json").absolute().as_posix()


def main(user, list_level, list_name, questions):
    # os.system("cls")
    create_path(MP3_PATH)
    dictionary = get_dictionary(DIC_PATH)
    definitions = get_word_help(dictionary, "definitions")
    examples = get_word_help(dictionary, "examples")

    if not user:
        user = input("Please enter your name: ")

    profile = get_user_profile(str.lower(user))

    if not list_level:
        list_level = profile.level

    words = list(
        get_random_words(list_level, list_name, questions, dictionary, profile)
    )

    if list_name == "*":
        print(
            "Hello, {0}. Today's test will be {1} questions at level {2}".format(
                profile.display_name, len(words), list_level
            )
        )
    else:
        print(
            "Hello, {0}. Today's test will be {1} questions from the {2} list(s)".format(
                profile.display_name, len(words), list_name
            )
        )

    count = 0

    for word in words:

        if not word in profile.words:
            profile.words[word] = 0

        count = count + 1
        mp3_file = get_mp3(word, MP3_PATH)

        # pygame.mixer.pre_init(frequency=44100)
        # pygame.mixer.init(frequency=44100)
        pygame.mixer.init()
        pygame.mixer.music.load(mp3_file)

        attempts = 0
        attempt = ""
        while attempt != word:
            if not re.match(r"^\?", attempt):
                attempts = attempts + 1
            pygame.mixer.music.play()
            question = "Word {:02d}, attempt {:02d}: ".format(count, attempts)

            if word in definitions:
                question += '\nDefinition is "{0}": '.format(definitions[word])

            if word in examples:
                question += '\nExample is "{0}": '.format(examples[word])

            attempt = input(question)

            if attempt == "?show":
                print(word)

        # A **lower** score is better (i.e. fewer attempts); getting a word
        # correct first time is the only way to reduce the score for that word.
        profile.words[word] = profile.words[word] + (attempts - 2)

    print("Well done, you've completed the test!\n")

    for word in words:
        print("Word: {0}, score {1:02d}".format(word, profile.words[word]))

    save_profile(profile)


def create_path(path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def get_user_profile(user) -> Profile:
    # path = pathlib.Path.cwd().joinpath("{0}.profile".format(user)).absolute()
    user_profile = Profile(user)
    if user_profile.profile_file_exists():
        user_profile.load_profile()

    return user_profile


def save_profile(profile):
    path = (
        pathlib.Path.cwd()
        .joinpath("{0}.profile".format(profile.display_name))
        .absolute()
    )

    with open(path, "w") as profile_file:
        profile_file.writelines(profile.dumps())


def join_dict(*args) -> dict:
    return dict(chain.from_iterable(d.items() for d in args))


def get_dictionary(path) -> dict:
    with open(path) as json_file:
        return json.load(json_file)


def get_word_help(dictionary, help_type: str) -> dict:
    word_help = {}
    jsonpath_filter = f"$.dictionary[*].{help_type}"
    item_list = jsonpath.jsonpath(dictionary, jsonpath_filter)
    for item in item_list:
        word_help = join_dict(word_help, item)
    return word_help


def get_random_words(
    level: int, name: str, questions: int, dictionary: dict, profile: Profile
) -> list:

    word_list = set()

    while not word_list:
        if name == "*":
            jsonpath_filter = (
                "$.dictionary[?(@.level=={0} || @.level=={1})].words".format(
                    level,
                    int(level) - 1,
                )
            )
        else:
            jsonpath_filter = '$.dictionary[?(@.name == "{0}")].words'.format(name)

        words = jsonpath.jsonpath(dictionary, jsonpath_filter)

        if not words:
            print(jsonpath_filter)
            raise ValueError("No words returned")

        # Flatten these dictionaries into one set of distinct words, skipping words
        # that have a negative score in the user profile:

        for sublist in words:
            for item in sublist:
                if not item in profile.words:
                    word_list.add(item)
                elif profile.words[item] > -1:
                    word_list.add(item)

        # If we have filtered out all possible words then we need to move up a
        # level.
        if not word_list:
            level += 1

    word_list = list(word_list)

    # return a random sample of these words
    return (
        word_list[i]
        for i in random.sample(range(len(word_list)), min(len(word_list), questions))
    )


def get_mp3(word, mp3_path) -> str:
    mp3_file = mp3_path.joinpath(f"{word}.mp3")
    if not mp3_file.exists():
        phrase = f"Please spell the word: {word}"

        ve = None
        attempt = 0

        while not ve and attempt < 3:
            attempt += 1
            try:
                tts = gTTS(phrase, lang="en-gb")
            except ValueError as ve:
                print("Error getting question audio; retrying...")

        if ve:
            raise ValueError(ve)

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
        "--questions",
        help="The number of words to test (Default 10)",
        default=10,
        type=int,
    )
    args = parser.parse_args()

    main(**vars(args))