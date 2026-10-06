# Supplied diagnosis

The top-level split owns velocity, pressure, and concentration, but the intermediate fluid split
does not declare the velocity and pressure variables it owns before subdivision. Repair only the
field-split ownership and mechanically required split wiring so every child is a subset of its
parent, siblings are disjoint, and the children cover the parent. Physics and solver choices are
frozen.
