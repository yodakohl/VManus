# GDT521 method

## Question

Can short component history distinguish visibly identical closure families such
as `...eody → O+DY` versus `...eody → O+D_ADDR+Y`, where GDT520's visible
boundary model necessarily sees the same tail?

## Inputs

- GDT407's 1,558 invariant old running surface types and recipes;
- GDT516's 159 current new-to-old-base surfaces and already selected recipes;
- GDT520's finite candidate score, including stems, short renderers, segment
  economy and visible boundary licenses.

No new page or surface is admitted.

## Short-history model

Each invariant old surface type contributes its component recipe once. Start
markers are prepended and an end marker appended. Add-0.5 order-five
probabilities are learned:

```text
P(next | previous four atoms)
  = (count(history,next) + 0.5)
    / (count(history) + 0.5 * vocabulary_size)
```

The candidate cost is mean negative log probability over its components and
end marker. Averaging prevents a mechanical preference for shorter recipes;
GDT520 already carries the small explicit segment economy.

The selected score is:

```text
GDT520 score + 0.50 * mean order-five recipe NLL
```

The full old model has 1,993 histories, 3,284 observed history→next contacts
and a 44-token component/end vocabulary.

## Rehearsal

The old SHA-256 four-way surface rotation is rebuilt completely in every fold:
compiler, visible-form decoder, renderer deck, boundary model and recipe
history model all use only the other three groups. Nine order/weight choices
are emitted for both the rotating old deck and the current 159 forms.

## Decision rule and ceiling

The selected model must remain a small additive prior after GDT520. Exact
event and known surface/role cards keep precedence. An atom sequence made more
probable by the model is a familiar working composition, not established
syntax, a phrase, a word or plaintext.
