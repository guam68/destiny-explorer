# destiny-explorer


## Overview
...

## Functionality

- Select format, type, and affinity
- Enter name or id
    * If name or id entered: show card info, else: show list of card names/ids/set/color/point values(or cost)
    * Once card is searched, show card info
    * Options to view card image and for characters, view available pairings




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