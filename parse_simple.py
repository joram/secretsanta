#!/usr/bin/env python3

import csv
import pprint
import random


def parse_people(filename:str) -> dict:
    people = {}
    with open(filename) as f:
        data = csv.DictReader(f)
        for person in data:
            name = person["Name"]
            people[name] = person
    return people


def assign(seed=2303, filename="blank_2021.csv"):
    random.seed(seed)
    people = parse_people(filename)
    assignments = {}
    remaining_givers = list(people.keys())
    remaining_targets = list(people.keys())
    while len(remaining_givers) > 0:
        giver = random.choice(remaining_givers)
        avoid_list = people[giver].get("Avoid List", "").split(",")
        avoid_list.append(giver)
        print(f"{giver} avoids {avoid_list}")
        possible_targets = [p for p in remaining_targets if p not in avoid_list]
        target = random.choice(possible_targets)
        assignments[giver] = target

        remaining_givers = [p for p in remaining_givers if p != giver]
        remaining_targets = [p for p in remaining_targets if p != target]
    pprint.pprint(assignments)

    for giver in assignments.keys():
        target = assignments[giver]
        print(f"### {giver} -> {target} ###")
        # Timestamp,Name,Email Address,Shipping Address,Avoid List,Message For Santa,Your Social Insurance Number
        print(f"Hey {giver},\nYour secret santa target is `{target}`. Here's all the info they gave me, if you want anything else I can be an intermediary and ask questions on your behalf.\n")
        for key in ["Email Address", "Shipping Address", "Message For Santa"]:
            val = people[target][key]
            print(f"{key}:\n{val}\n")
        print("\n\n\n\n\n")


assign(2304, "csvs/friends_2021.csv")

