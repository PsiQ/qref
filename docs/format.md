# HQAR Format

HQAR format is a domain-specific language (DSL) for describing quantum algorithms
for the purpose of resource estimation.

The algorithms are described as programs comprising hierarchical, directed
acyclic graph (henceforth hierarchical DAG) of subroutines. Let's break down
what this means:

- *Hierarchical* means that routines can be nested.
- *Directed* means that every edge connecting two routines also defines order
  between them.
- *Acyclic* means that traversing the graph along its edges will never lead
  to visiting the same node twice.


