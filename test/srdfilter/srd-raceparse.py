import json


def main():
    with open('races.json') as f:
        monsters = json.load(f)
    # with open('srd-backgrounds.txt') as f:
    srd = ['Dragonborn', 'Half-Elf', 'Half-Orc', 'Elf (High)', 'Dwarf (Hill)', 'Human', 'Human (Variant)',
           'Halfling (Lightfoot)', 'Gnome (Rock)', 'Tiefling (Infernal)']

    for monster in monsters:
        if monster['name'].lower() in srd:
            monster['srd'] = True
        else:
            monster['srd'] = False

    for sp in srd:
        if not sp in [s['name'].lower() for s in monsters]:
            print(sp)

    with open('srdproc.json', 'w') as f:
        json.dump(monsters, f, indent=2, sort_keys=True)


if __name__ == '__main__':
    main()
