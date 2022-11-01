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
    ss: str

    def __str__(self) -> str:
        fmt = '>7s'
        pr = f'{self.price:.2f}'
        pp = f'{round(self.price_per,2):.2f}'
        ss = ''.join(sorted(self.ss))
        return f'({self.split}) {ss:<3s}  ${str(pr):{fmt}}, ${str(pp):{fmt}}:  {self.name}'
    
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
        price_per=float(price)/split,
        ss=ss
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
    pretty_print_person(all_items,f'files/{filename}',total_bill=True)
    for p in ps:
        pretty_print_person(p,f'out/{filename}')
    

def pretty_print_person(p,fn,total_bill=False):
    with open(f'./{fn}-{p.abv}.txt','w') as f:

        _, fn = fn.split('/')
        date, name = fn.split('-')
        date = f'{date[4:6]}/{date[6:8]}/{date[0:4]}'
        f.write(f'{date}, {name.title()}: {p.name}\n\n')
        f.write(f'  SPLIT     TOTAL       PER   NAME\n')
        f.write(f'--------------------------------\n')
        for i in p.items:
            f.write(f'{str(i)}\n')
        f.write(f'\n            TOTAL: ${str(p.get_total(total_bill=total_bill)):>6s}')

def process(filename):

    with open('./people.yaml', 'r') as f:
        people = safe_load(f)
    
    all_items = person(f'ALL', 'all')
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

