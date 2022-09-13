#!/usr/bin/env python3

import csv
import io
import pprint
import random
from typing import List, Dict, Optional

clans = {}

# Alex sort into clans
# Spotcheck: jeannie/tom or betty/greg don't get Jody
# Alex/John memorize the seed number once good



class Family:
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
        num_presents: int = 3,
    ):
        self.name = name
        self.clan = clan
        self.shipping_address = shipping_address
        self.email_address = email_address
        self.hints = hints
        self.num_presents = num_presents
        self.target_names = []
        self.receive_from_names = []

    @property
    def num_gifts_owed(self) -> int:
        return self.num_presents - len(self.receive_from_names)

    @property
    def num_gifts_needed(self) -> int:
        return self.num_presents - len(self.target_names)

    @property
    def targets(self) -> List["Family"]:
        for clan in clans.values():
            for family in clan.families:
                if family.name in self.target_names:
                    yield family

class Clan:

    def __init__(self, name):
        self.name = name
        self.families = []

    @classmethod
    def get(cls, name) -> "Clan":
        if name not in clans:
            clans[name] = Clan(name)
        clans[name] = clans.get(name)
        return clans[name]

    def add_family(self, family: Family):
        self.families.append(family)

    @property
    def num_gifts_owed(self) -> int:
        return sum([family.num_gifts_owed for family in self.families])

    @property
    def num_gifts_needed(self) -> int:
        return sum([family.num_gifts_needed for family in self.families])

    def giver(self) -> Family:
        elected_giver = None
        for family in self.families:
            if elected_giver is None or len(family.target_names) < len(elected_giver.target_names):
                elected_giver = family
        return elected_giver

    def receiver(self, giver: Family) -> Optional[Family]:
        elected_receiver = None
        for family in self.families:
            if elected_receiver is None:
                elected_receiver = family
                continue
            if giver.name in family.receive_from_names:
                continue
            if len(family.receive_from_names) < len(elected_receiver.receive_from_names):
                elected_receiver = family
        if elected_receiver and elected_receiver.num_gifts_owed <= 0:
            return None
        return elected_receiver


def parse(filepath: str = "data.csv"):
    global families
    families = {}

    # load from CSV
    with open(filepath) as f:
        data = csv.DictReader(f)
        for row in data:
            name = row["Name"]
            Clan.get(row["Clan"]).add_family(Family(
                name=name,
                shipping_address=row["Shipping Address"],
                email_address=row["Email Address"],
                hints=row["Message for Santa"],
                num_presents=3,
            ))


def assign(seed=2303, num_targets=3, filename="blank_2021.csv"):
    random.seed(seed)
    parse(filename)
    while any([clan.num_gifts_owed>0 for clan in clans.values()]):
        clans_owing = [clan for clan in clans.values() if clan.num_gifts_needed > 0]
        max_clan_owing = max([clan.num_gifts_needed for clan in clans_owing])

        for clan in clans_owing:
            if clan.num_gifts_needed != max_clan_owing:
                continue
            giver = clan.giver()
            possible_receivers = [other_clan.receiver(giver) for other_clan in clans.values() if other_clan.name != clan.name]
            possible_receivers = [receiver for receiver in possible_receivers if receiver is not None]
            if len(possible_receivers) == 0:
                continue

            receiver = random.choice(possible_receivers)

            if giver.name in receiver.receive_from_names:
                continue
            if len(giver.target_names) > num_targets:
                continue
            giver.target_names.append(receiver.name)
            receiver.receive_from_names.append(giver.name)


assign(2304, 3, "./csvs/example_clan_2021.csv")

# show results
output = io.StringIO()
writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
writer.writerow(["Giver", "Receiver", "Shipping Address", "Email Address", "Suggestions/Hints"])
for clan in clans.values():
    for family in clan.families:
        for target in family.targets:
            writer.writerow([family.name, target.name, target.shipping_address, target.email_address, target.hints])
print(output.getvalue())
