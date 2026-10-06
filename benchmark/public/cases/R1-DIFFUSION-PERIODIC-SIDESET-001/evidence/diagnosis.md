# Supplied diagnosis

The configured periodic sidesets do not form a one-to-one translated pair. The right sideset
contains faces outside the translated overlap. Restrict that sideset to the matching portion and
update the periodic reference. The diffusion equation, translation vector, and remaining model
are already correct and frozen.

Only creation or restriction of the right periodic sideset and its periodic boundary reference are
authorized.
