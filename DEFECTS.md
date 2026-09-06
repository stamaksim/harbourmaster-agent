# DEFECTS.md

Problems with RULEBOOK.md's own text — contradictions, gaps, and
undefined terms — found by reading it fully, independent of any agent
implementation.

## 1. Spice scoring contradiction (§4.2 vs §7.1)

§4.2:
> Spice is the most valuable trade good in the harbour and counts double when scored.

§7.1's scoring table:

| Suit | Points per card |
|---|---|
| Spice | face value |

§4.2 states Spice scores double; §7.1's table — the section §7.1 itself explicitly says to use for scoring ("score each card using the table below") — lists Spice at plain face value with no doubling. These directly contradict each other. An implementation must guess which of the two rules is authoritative, since nothing in the text ranks one section over the other or reconciles them (e.g. as an old rule superseded by an errata table).

## 2. No rule for an exhausted Draw Pile (missing near §2.1 / §4.1)

§2.1:
> Shuffle the Cargo cards to form the **Draw Pile**. Deal five cards to each player as their starting **Hold**.

§4.1:
> **Draw** — take two Cargo cards from the Draw Pile into your Hold.

Nothing in §2 (Setup) or §4.1 (Draw) — nor anywhere else in the rulebook — states what happens once the Draw Pile has no cards left to take: whether discard piles are reshuffled back into it, whether Draw simply becomes unavailable, or whether running out ends the game. With 60 total cards, most of which end up locked into Holds, on Ships, or unloaded onto Docks (§5.2: cargo "cannot be reclaimed"), this is a reachable state the rules never address, and an implementation has no textual basis for any of the three plausible answers.

## 3. "The round" is used but never defined, and collides with the unrelated defined term "Storm round" (§5.4 vs §6.1–§6.4)

§5.4:
> The Harbourmaster token passes to the player who unloads the single largest cargo of the round, counted as number of cards.

§6.1:
> At the end of each player's turn, that player rolls the Storm die. A wave result begins a **Storm round**.

§6.3:
> A Storm round ends when play returns to the player who rolled the wave.

The only place the rulebook formally defines a bounded "round" is §6's **Storm round**, which is an unrelated, conditionally-triggered event (it only exists after a wave is rolled, and most turns never enter one). §5.4 refers to "the round" for Harbourmaster token reassignment without ever defining what a normal round is — one full go-around of all players' turns, a single player's turn, or (by the only textual precedent available) a Storm round. This matters because it directly determines how often the Harbourmaster token — which gates unloading more than three cards per §5.1 — actually changes hands, and there's no way to resolve it from the text as written.

## 4. Sail (§4.3) only specifies Open Sea ↔ Dock movement; Dock-to-Dock is neither permitted nor forbidden

§4.3:
> **Sail** — move your Ship from the Open Sea to any unoccupied Dock tile on the Quay, or from a Dock tile back to the Open Sea. Only one Ship may occupy a Dock tile at a time.

The action is defined as exactly two transitions: Open Sea→Dock and Dock→Open Sea. Moving directly from one occupied Dock tile to a different Dock tile is never mentioned as either allowed or disallowed. Read strictly, a single Sail action cannot accomplish a Dock-to-Dock move, and since §3.1 forbids repeating the same action twice in one turn, such a move would take a minimum of two separate turns (Dock→Open Sea, then later Open Sea→Dock) — but the rulebook never confirms this is the intended interpretation versus a simple omission, leaving a common-sense scenario ("can my Ship move to a different Dock") without a stated answer.
