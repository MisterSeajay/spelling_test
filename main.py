#!/usr/bin/python3
import argparse, os, pathlib, random, sys
import json, jsonpath
import pygame
from gtts import gTTS

MP3_PATH = pathlib.Path.cwd().joinpath('mp3_cache')
DIC_PATH = pathlib.Path.cwd().joinpath('dictionary.json').absolute().as_posix()

def main(list_level=6, list_name="*", tests=10):
    create_path(MP3_PATH)

    count = 0
    words = get_random_words(list_level, list_name, tests, DIC_PATH)

    os.system('cls')

    for word in words:
        count = count + 1
        mp3_file = get_mp3(word, MP3_PATH)

        pygame.mixer.init()
        pygame.mixer.music.load(mp3_file)

        attempts = 0
        attempt = ''
        while attempt != word:
            attempts = attempts + 1
            pygame.mixer.music.play()
            attempt = input('Word %02d, attempt %02d: ' % (count, attempts))

    print('Well done, you\'ve completed the test!')


def create_path(path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def get_random_words(list_level, list_name, tests, path):
    with open(path) as json_file:
        json_data = json.load(json_file)
        json_file.close()
    
    # Find all word lists of the appropriate list_level
    # jsonpath_filter = '$.dictionary[?(@.name =~ /^%s$/i && (@.level==%d || @.level==%d))].words' % (list_name, list_level, list_level-1)
    if list_name == "*":
        jsonpath_filter = '$.dictionary[?(@.level==%d || @.level==%d)].words' % (list_level, list_level-1)
    else:
        jsonpath_filter = '$.dictionary[?(@.name == "%s")].words' % (list_name)
    
    words = jsonpath.jsonpath(json_data, jsonpath_filter)

    if not words:
        print(jsonpath_filter)
        raise ValueError("No words returned")

    # flatten these dictionaries into one word list
    word_list = []
    for sublist in words:
        for item in sublist:
            word_list.append(item)

    # return a random sample of these words
    return(word_list[i] for i in random.sample(range(len(word_list)), tests))


def get_mp3(word, mp3_path):
    mp3_file = mp3_path.joinpath('%s.mp3' % word)
    if not mp3_file.exists():
        phrase = ('Please spell the word: %s' % word)
        tts = gTTS(phrase, lang='en-gb')
        tts.save(mp3_file.absolute().as_posix())
    return mp3_file.absolute().as_posix()


if __name__ == "__main__":
    # Read command line arguments
    parser=argparse.ArgumentParser()
    parser.add_argument('--level', help='What (school year) list_level to test at? (Default 6)')
    parser.add_argument('--name', help='What list of words do you want to use')
    parser.add_argument('--tests', help='How may spellings to test? (Default 10)')
    args=parser.parse_args()

    # Set default values for arguments
    if not args.level:
        args.level = 6
    else:
        args.level = int(args.level)
    
    if not args.name:
        args.name = "*"
        
    if not args.tests:
        args.tests = 10
    else:
        args.tests = int(args.tests)

    # Run the test
    main(list_level=args.level, list_name=args.name, tests=args.tests)