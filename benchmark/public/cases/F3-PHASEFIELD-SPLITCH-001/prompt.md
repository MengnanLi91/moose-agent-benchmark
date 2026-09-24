# F3 Task — MOOSE Object and Coupling Map

Read the supplied split Cahn-Hilliard weak formulation and permitted object registry.

For every supplied residual term, identify the MOOSE object, residual variable, coupled
variables, material properties, and relevant parameter names. Also identify the
derivative-capable free-energy material and constant-property material wiring.

Return the mapping as prose, a Markdown table, or a list. Presentation order and local variable
names do not affect credit when the object choices and couplings are semantically equivalent.

Do not rederive Cahn-Hilliard, add unlisted object types, or write a complete `.i` file.
