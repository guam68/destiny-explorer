import argparse
from colorama import Fore, Style, init
from explorer import Explorer


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-t', dest='card_type', default='all', help='Limit card pool by card type ' +
        'Options: [all, char, supp, upgr, event, plot, dgrd]\n') 
    parser.add_argument('-a', dest='affinity', default='hvn', help='Limit card pool by affinity. ' +
        'Options: [h]ero, [v]illain, [n]eutral\n' +
        '\tNote: May contain any combination of the options\n' +
        '\tex. -a vn\n \n')
    parser.add_argument('-c', dest='color', default='rgby', help='Limit card pool by color. ' +
        'Options: [g]ray, [y]ellow, [b]lue, [r]ed\n' +
        '\tNote: May contain any combination of the options\n' +
        '\tex. -c rbg\n \n')
    parser.add_argument('-f', dest='t_format', default='std', help='Restrict card pool by format. Options: [inf, std, tri]')
    parser.add_argument('-s', dest='card_set', default='all', help='Restrict card pool by set. ' +
        'Options: [AW, SoR, EaW, TPS, LEG, RIV, WotF, AtG, CONV, AoN, SoH]\n \n')

    args = parser.parse_args()

    return vars(args)


def main():
    init()
    explorer = Explorer(parse_args())
    explorer.search()


if __name__ == "__main__":
    main() 
