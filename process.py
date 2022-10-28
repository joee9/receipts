# Joe Nyhan, 28 October 2022
# Script for processing a receipt amongst roommates

from dataclasses import dataclass
from yaml import safe_load
from csv import reader
from sys import argv
from os.path import isfile


@dataclass
class item:
    name: str
    price: float
    split: int
    price_per: float

    def __str__(self) -> str:
        fmt = '>6s'
        pr = f'{self.price:.2f}'
        pp = f'{round(self.price_per,2):.2f}'
        return f'({self.split}) ${str(pr):{fmt}}, ${str(pp):{fmt}}:  {self.name}'
    
    def __repr__(self) -> str:
        return self.__str__(self)

class person:
    name: str
    abv: str
    items: list[item]
    
    total = -1

    def __init__(self, name, abv) -> None:
        self.items = []
        self.name = name
        self.abv = abv

    def __str__(self) -> str:
        return f'{self.abv}: {self.name}'
    
    def append(self, item):
        self.items.append(item)
    
    def calc_total(self,total_bill):
        t = 0
        if total_bill:
            for i in self.items:
                t += i.price
        else:
            for i in self.items:
                t += i.price_per

        self.total = round(t,2)
        
    def get_total(self,total_bill=False):
        if self.total == -1:
            self.calc_total(total_bill)
            return self.total
        return self.total
    

def process_row(row,people,all_items):
    name, price, ss = row
    if ss == 'all':
        split = len(people)
    else:
        split = len(ss)
    
    i = item(
        name=str(name),
        price=float(price),
        split=split,
        price_per=float(price)/split
    )

    all_items.append(i)
    for p in people:
        if ss == 'all' or p.abv in ss:
            p.append(i)


def print_people_and_items(ps):
    for p in ps:
        print(f'{p.name}, {len(p.items)}, {p.get_total()}')
        for i in p.items:
            print(i)


def write_all_to_file(filename,ps,all_items):
    pretty_print_person(all_items,f'files/{filename}')
    for p in ps:
        pretty_print_person(p,f'out/{filename}')
    

def pretty_print_person(p,fn):
    with open(f'./{fn}-{p.abv}.txt','w') as f:
        f.write(f'${p.get_total()}: {p.name}\n\n')
        f.write(f'SPL   TOTAL    SPLIT   NAME\n')
        for i in p.items:
            f.write(f'{str(i)}\n')


def process(filename):

    with open('./people.yaml', 'r') as f:
        people = safe_load(f)
    
    all_items = person(f'{filename}', 'all')
    ps = [person(p.get('name'), p.get('abv')) for p in people]

    with open(f'./files/{filename}.csv','r') as f:
        out = reader(f, delimiter=',')
        for row in out:
            process_row(row,ps,all_items)

    write_all_to_file(filename,ps,all_items)

    
def main():

    assert len(argv) == 2
    filename = argv[1]

    if isfile(f'./files/{filename}.csv'):
        process(filename)
    else:
        raise Exception('Receipt does not exist.')


if __name__ == '__main__':
    main()

