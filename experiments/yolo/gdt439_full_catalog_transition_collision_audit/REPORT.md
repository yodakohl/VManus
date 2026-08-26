# GDT439 — the main deck is safe, the full catalog is not yet bijective

## Result

The 49 main future cards remain mutually distinct. The larger 1,563-key reader
does not: its 382,935 state/register transitions reduce to 1,449 distinct full
signatures.

- 1,345 recipes have a signature of their own;
- 218 recipes occupy 104 collision groups;
- those groups contain 125 colliding recipe pairs;
- the largest group contains four recipes;
- all exact vectors, not only their hashes, are equal inside a group.

The reader is still operationally unambiguous because it matches the exact
ordered component recipe before rendering. What fails is the stronger claim
that every exact key already has a different fluent semantic transition.

## Two different causes

Seventy-six collision groups contain the same atoms in a different order.
Among 155 same-multiset catalog pairs, 82 still collapse completely. GDT437
repaired relation versus argument order, but the old bucket renderer can still
erase order between an action and relation, order control and relation, grade
and action, or larger packages.

The other 28 groups use different local-control atoms that deliberately share
the same broad working value—for example several address forms all read HIER,
and `OS`/`RESUME_CARD` both read VORBEZUG. These are legitimate semantic
collisions under the present dictionary. Their exact signs must stay visible;
inventing different English words would merely hide the issue.

## The five main-card contacts

No collision contains two main cards, but five main cards collide with a card
outside the main deck:

- `AIR+OL` ↔ `OL+AIR`;
- `CHD+L` ↔ `L+CHD`;
- `Y+K+L` ↔ `L+K+Y`;
- `O+OR` ↔ `OR+O`;
- `D_ADDR+CH+AIN` ↔ `CH+LOCAL_CHAR_F+AIN`.

The first four are clean written-order repair candidates. The fifth is the
expected collision of two HIER channels and must retain its literal channel
identity rather than receive a fabricated meaning contrast.

## Consequence

The 49-card prospective deck remains usable, and GDT438 remains the correct
command. The next repair is now concrete: preserve top-level written package
order throughout the renderer, then rerun these 104 groups. Success means
removing same-multiset collisions while leaving the genuinely co-valued local
channels explicit and separate.

All 33 checks pass. No meaning, surface or page changed.
