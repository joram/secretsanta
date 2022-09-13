#!/usr/bin/env python3

import csv
import io
import pprint
import random
from typing import List, Dict, Optional


class Person:
    name: str = ""
    shipping_address: str = ""
    email_address: str = ""
    hints: str = ""
    target_names: List[str] = []

    def __init__(
        self,
        name: str = "",
        clan: str = "",
        shipping_address: str = "",
        email_address: str = "",
        hints: str = "",
        num_presents: int = 1,
    ):
        self.name = name
        self.clan = clan
        self.shipping_address = shipping_address
        self.email_address = email_address
        self.hints = hints
        self.num_presents = num_presents
        self.target_names = []
        self.receive_from_names = []

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    @property
    def num_gifts_owed(self) -> int:
        return self.num_presents - len(self.receive_from_names)

    @property
    def num_gifts_needed(self) -> int:
        return self.num_presents - len(self.target_names)

    def targets(self, people: List["Person"]) -> List["Person"]:
        for person in people:
            if person.name in self.target_names:
                yield person

    def blacklist(self, people: List["Person"]) -> List["Person"]:
        for person in people:
            if person.clan == self.clan:
                yield person
            if person.name in self.receive_from_names:
                yield person

    def get_another_target(self, people: List["Person"]) -> Optional["Person"]:
        possible_receivers = [person for person in people if person not in list(self.blacklist(people))]  # not a target already
        possible_receivers = [person for person in possible_receivers if person.num_gifts_owed > 0]  # not already full
        if len(possible_receivers) == 0:
            print("no valid receivers for", self)
            return None

        target = random.choice(possible_receivers)
        self.target_names.append(target.name)
        target.receive_from_names.append(self.name)
        return target


def parse(filepath: str = "data.csv", presents: int = 1):
    people = []
    with open(filepath) as f:
        data = csv.DictReader(f)
        for row in data:
            people.append(Person(
                name=row["Name"],
                shipping_address=row["Mailing Address"],
                email_address=row["Email"],
                hints=row["Gift Suggestions/Ideas"],
                num_presents=presents,
                clan=row["Clan"],
            ))
    return people


def assign(seed, presents, filename):
    global people

    done = False
    while not done:
        seed += 1
        random.seed(seed)
        people = parse(filename, presents)
        print(f"people {people}")
        # assign targets
        while not done:
            people_owing_gifts = [person for person in people if person.num_gifts_needed > 0]
            if len(people_owing_gifts) == 0:
                done = True
                break

            for giver in people_owing_gifts:
                target = giver.get_another_target(people)
                if target is None:
                    print("no valid target for", giver)
                    continue
    return people


if __name__ == "__main__":
    people = assign(seed=1, presents=1, filename="./csvs/clans_2022.csv")

    # show results
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(["Giver", "Receiver", "Shipping Address", "Email Address", "Suggestions/Hints"])
    for person in people:
        for target in person.targets(people):
            writer.writerow([person.name, target.name, target.shipping_address, target.email_address, target.hints])
    print(output.getvalue())
