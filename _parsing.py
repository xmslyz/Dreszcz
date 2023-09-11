import json
import re

import requests
from bs4 import BeautifulSoup


def step1():
    url = f'http://www.dudziarz.net/dreszcz/index_white.html#calibre_link-25'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    txt = ''
    for text in soup.find_all(string=True):
        if text.parent.name not in ['style', 'script', 'head', 'title', 'meta',
                                    '[document]']:
            txt += text

    with open("book/dreszcz1.txt", "w", encoding='utf-8') as f:
        f.write(txt)


def step2():
    with open("book/dreszcz1.txt", encoding='utf-8') as f:
        old_txt = f.readlines()

    txt = ''
    for i, line in enumerate(old_txt):
        try:
            if line != "\n":
                txt += line
            else:
                pass
        except Exception:
                pass

    with open("book/dreszcz2.txt", "w", encoding='utf-8') as f:
        f.write(txt)


def step3():
    with open("book/dreszcz2.txt", encoding='utf-8') as f:
        old_txt = f.readlines()

    txt = ''
    for i, line in enumerate(old_txt):
        try:
            if re.match(r'^.*atrz\s*$', line):
                txt += line.strip("\n")
            else:
                txt += line
        except Exception:
            pass

    with open("book/dreszcz3.txt", "w", encoding='utf-8') as f:
        f.write(txt)


def step4():
    with open("book/dreszcz3.txt", encoding='utf-8') as f:
        old_txt = f.readlines()

    txt = ''
    numbers = []
    for i, line in enumerate(old_txt):
        try:
            if re.match(r'^[0-9]{1,3}.\s$', line):
                print(line)
                txt += line.strip("\n")
                numbers.append(int(line.strip('.\n')))
            else:
                txt += line
        except:
            pass

    non_sequential_numbers = []

    for i in range(len(numbers) - 1):
        if numbers[i] + 1 != numbers[i + 1]:
            non_sequential_numbers.append(numbers[i + 1])

    print(non_sequential_numbers)


def step5():
    with open("book/dreszcz3.txt", encoding='utf-8') as f:
        old_txt = f.readlines()

    txt = ''
    for i, line in enumerate(old_txt):
        try:
            if re.match(r'^[0-9]{1,3}.\s$', line):
                txt += "[" + line.strip(".\n") + "] "
            else:
                txt += line

        except:
            pass

    with open("book/dreszcz4.txt", "w", encoding='utf-8') as f:
        f.write(txt)


def step6():
    with open("book/dreszcz4.txt", encoding='utf-8') as f:
        old_txt = f.readlines()

    txt = ''
    for i, line in enumerate(old_txt):
        try:
            if re.match(r'^\[.*$', old_txt[i + 1]):
                txt += line
            else:
                txt += line.replace("\n", ' ')
        except:
            pass

    with open("book/dreszcz5.txt", "w", encoding='utf-8') as f:
        f.write(txt)


def step7():
    with open("book/dreszcz5.txt", encoding='utf-8') as f:
        old_txt = f.readlines()

    txt = ''
    for line in old_txt:
        try:
            txt += line.replace("  ", " ")
        except:
            pass

    with open("book/dreszcz6.txt", "w", encoding='utf-8') as f:
        f.write(txt)


def step8():
    with open("book/dreszcz6.txt", encoding='utf-8') as f:
        txt = f.readlines()

    dreszcz = {}

    for line in txt:
        num, partxt = line.split(']')
        dreszcz[num.strip('[')] = partxt.strip()

    with open("dreszcz.json", "w") as f:
        json.dump(dreszcz, f, indent=4)


def step9():
    # Open the text file
    with open('book/dreszcz6.txt', 'r', encoding='utf-8') as file:
        text = file.read()

    # Create a dictionary to store the creature information
    creature_dict = {}

    # Use regular expressions to extract the name, paragraph number, Z value, and W value for each creature
    matches = re.findall(r'\[(\d+)\].*?([A-Z]+)\sZ:(\d+)\sW:(\d+)', text)

    # Extract the information and add it to the dictionary
    for paragraph_number, name, z_value, w_value in matches:
        if name in creature_dict:
            creature_dict[name]["Paragraphs"].append(int(paragraph_number))
            creature_dict[name]["Z_values"].append(int(z_value))
            creature_dict[name]["W_values"].append(int(w_value))
        else:
            creature_dict[name] = {
                "Name": name,
                "Paragraphs": [int(paragraph_number)],
                "Z_values": [int(z_value)],
                "W_values": [int(w_value)]
            }

    # Print the extracted information for each creature
    for creature in creature_dict.values():
        print(f"Name: {creature['Name']}")
        for i in range(len(creature['Paragraphs'])):
            print(
                f"Paragraph: {creature['Paragraphs'][i]}, Z: {creature['Z_values'][i]}, W: {creature['W_values'][i]}")

    # Save the creature_dict as a JSON file
    with open('creature_data.json', 'w') as json_file:
        json.dump(creature_dict, json_file, indent=4)

    print("Creature data saved as JSON file.")