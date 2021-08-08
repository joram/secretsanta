#!/usr/bin/env python3

import csv
import random
from typing import List, Dict, Optional

families = {}


def all_families() -> List["Family"]:
    global families
    return list(families.values())


def all_flexible_families() -> List["Family"]:
    global families
    flexible_families = []
    for family in families.values():
        if family.flexible:
            flexible_families.append(family)
    return flexible_families


def all_strict_families() -> List["Family"]:
    global families
    flexible_families = []
    for family in families.values():
        if not family.flexible:
            flexible_families.append(family)
    return flexible_families


class Family:
    name: str = ""
    shipping_address: str = ""
    email_address: str = ""
    hints: str = ""
    num_presents: int = 3
    blacklist_names: List[str] = []
    target_names: List[str] = []

    def __init__(
        self,
        name: str = "",
        shipping_address: str = "",
        email_address: str = "",
        hints: str = "",
        num_presents: int = 3,
        flexible: bool = True
    ):
        self.name = name
        self.shipping_address = shipping_address
        self.email_address = email_address
        self.hints = hints
        self.num_presents = num_presents
        self.target_names = []
        self.blacklist_names = []
        self.flexible = flexible

    def valid_targets(self) -> List["Family"]:
        if len(self.target_names) >= self.num_presents:
            return []

        valid_families = []
        for family in all_families():
            if family.name in self.blacklist_names:
                continue
            if family.name in self.target_names:
                continue
            if family.name == self.name:
                continue
            if not self.flexible and len(self.receiving_from()) >= self.num_presents:
                continue
            valid_families.append(family)
        return valid_families

    def valid_givers(self) -> List["Family"]:
        if len(self.receiving_from()) >= self.num_presents:
            return []

        valid_families = []
        for family in all_families():
            if self.name in family.blacklist_names:
                continue
            if self.name in family.target_names:
                continue
            if family.name == self.name:
                continue
            if not self.flexible and len(self.receiving_from()) >= self.num_presents:
                continue
            valid_families.append(family)
        return valid_families

    def pick_another_target(self) -> str:
        target = random.choice(self.valid_targets())
        self.target_names.append(target.name)
        return target.name

    @property
    def needs_more_targets(self) -> bool:
        return len(self.target_names) < self.num_presents

    def needs_more_presents(self) -> bool:
        return len(self.receiving_from()) < self.num_presents

    def receiving_from(self) -> List["Family"]:
        receiving_from_families = []
        for family in all_families():
            if self.name in family.target_names:
                receiving_from_families.append(family)
        return receiving_from_families


def get_families(blacklist_pairs: Optional[List] = None, blacklist_bidirectional: bool = True, filepath: str = "data.csv"):
    global families
    if blacklist_pairs is None:
        blacklist_pairs = []

    # load from CSV
    families = {}
    with open(filepath) as f:
        data = csv.DictReader(f)
        for row in data:
            name = row["Name"]
            families[name] = Family(
                name=name,
                shipping_address=row["Shipping Address"],
                email_address=row["Email Address"],
                hints=row["Message for Santa"],
                num_presents=random.randint(3, 5),
                flexible=random.choice([False])
            )

    # add in blacklist relationships
    if blacklist_bidirectional:
        reversed_blacklist_pairs = [(b, a) for (a, b) in blacklist_pairs]
        blacklist_pairs += reversed_blacklist_pairs
    for (a, b) in blacklist_pairs:
        families[a].blacklist_names.append(b)

    # pick givers
    still_need_assignments = all_families()
    fails = 0
    while fails < 10 and len(still_need_assignments) > 0:
        family_name = random.choice(still_need_assignments).name
        try:
            families[family_name].pick_another_target()
        except:
            fails += 1
            continue
        still_need_assignments = [family for family in families.values() if family.needs_more_targets]
        max_assignments_needed = 0
        for family in still_need_assignments:
            max_assignments_needed = max(max_assignments_needed, len(family.target_names)-family.num_presents)
        still_need_assignments = [family for family in all_families() if family.num_presents == max_assignments_needed]

    # pick receivers
    still_need_gifts = all_families()
    while len(still_need_gifts) > 0:
        receiver = random.choice(still_need_gifts)
        giver = random.choice(families[receiver.name].valid_givers())
        families[giver.name].target_names.append(receiver.name)
        still_need_gifts = [family for family in families.values() if family.needs_more_presents()]


def get_families_retry(blacklist_pairs: Optional[List] = None, blacklist_bidirectional: bool = True, filepath: str = "data.csv", seed: int = 0):
    while True:
        print(seed)
        random.seed(seed)
        try:
            get_families(blacklist_pairs, blacklist_bidirectional, filepath)
            return
        except Exception as e:
            print(e)
            seed += 1
            raise

avoid_pairs = [
    ("Colin Benjamin", "Malcolm Walker"),
    ("Aurora Walker", "Malcolm Walker"),
]
get_families_retry(avoid_pairs, True, "nerdhouse_2020_data.csv", 2303)
for family in families.values():
    print(f"family: {family.name} ({family.num_presents}) ({'flexible' if family.flexible else 'strict'})")
    for target_name in family.target_names:
        print(f"giving to\t- {target_name}")
    for other_family in family.receiving_from():
        print(f"receive from\t- {other_family.name}")
    print("")