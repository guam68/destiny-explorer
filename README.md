# destiny-explorer

## TODO

- Export pairing listing + card info to file
- Add coloring/formating to text output of proxy dice
- migrate functions to card_options

## Overview
...

## Functionality

- Filter by format, type, color, set, and affinity
- Enter name/keyword (adv search) or id
    * Displays card info if individual card or lists card names/ids/set/color/point values(or cost)
    * Options to view card image and for characters, view available pairings
    * Option to search for dice card proxies 




### Options


**-f FORMAT**

Restricts card pool by format. Defaults to standard.
    options:  - inf
              - std
              - tri


**-t TYPE**

Options for restricting card pool by card type, affinity, and color. Defaults to all.
    type options:  - char
                   - supp
                   - upgr
                   - event
                   - plot


**-a AFFINITY**

Options for restricting card pool by card type, affinity, and color. Defaults to hvn.
    affinity options:  - h (hero)
                       - v (villain)
                       - n (neutral)
                       - hn
                       - vn
                       - hv
                       - hvn

**-c COLOR**

Restiricts card pool by card color. Defaults to rgby.
    color options:  - g (gray)
                    - y (yellow)
                    - b (blue)
                    - r (red)

**-s SET**

Restricts card pool by set. Defaults to all.
    set options:    - awk
                    - sor
                    - eaw
                    - 2ps
                    - leg
                    - riv
                    - wotf
                    - atg
                    - conv

**-h, --help**

Shows available options