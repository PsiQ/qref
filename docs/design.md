# Design choices

## Using lists instead of mappings

One of the most controversial choices we have made in QREF is the choice of
using lists instead of mappings (Python dictionaries) for objects that
should have an unique name. This choice affects:

- Children of a `Routine`.
- Ports of a `Routine`.

For instance, you may ask why we chose to represent ports like this:

```yaml
ports:
  - {"name": "in_0", "direction": "input", "size": 2},
  - {"name": "out_0", "direction": "output", "size": "N"}
```

instead of this:

```yaml
ports:
  in_0: {"direction": "input", "size": 2}
  out_0: {"direction": "output", "size": "N"}
```
There are two answers to this question.

The first answer is purely pragmatic. On the one hand using mappings
instead of lists would guarantee uniqueness of names of ports
and children. However it would also give a false
sense of security. To see why consider the following example, which loads an incorrect definition of ports:

```python
import yaml

data = """
ports:
  in_0: {"direction": "input", "size": 2}
  in_0: {"direction": "input", "size": "N"}
"""

print(yaml.safe_load(data))
```

If you are new to parsing YAML (or JSON) in Python you might be
surprised that the code runs - after all shouldn't keys
in YAML mappings be unique? Well they should, but most parsers
will just load the last key if the duplicates are present. The
code above prints:

```text
{'ports': {'in_0': {'direction': 'input', 'size': 'N'}}}
```

So, suppose you are editing a QREF file. You made a mistake and
used the same port name twice. If we used mapping, your file would
load fine, but you would lose one entry. Importantly, from your
code's perspective you wouldn't even know - you would just get
a dictionary with unique keys. Debugging problems that could arise
in this way would be a nightmare, and we want to save all of us
such hurdles.

Now, what happens if we use lists? Let's try the following code:

```python
import yaml

data = """
ports:
  - {"name": "in_0", "direction": "input", "size": 2}
  - {"name": "in_0", "direction": "input", "size": "N"}
"""

print(yaml.safe_load(data))
```

This time, we get the following output:
```text
{'ports': [{'name': 'in_0', 'direction': 'input', 'size': 2}, {'name': 'in_0', 'direction': 'input', 'size': 'N'}]}
```
Now, we have ports with duplicate names, which is not good, but we
are able to detect this and react e.g. by raising exception.
No information was lost.

The natural question to ask is: why won't we use dictionaries,
and handle duplicate keys by customizing YAML (or JSON) parsers?
We could do this, but keep in mind that QREF is mainly a
data format. Different users can use different parsers and we
want to make sure everyone gets consistent results no matter
what parsing library they use.

The second reason concerns the `children` field and is much more nuanced,
but essentially boils down to the fact that lists are naturally better suited
for storing ordered information. While QREF itself does not enforce
ordering on the input data, there might be algorithms that
utilize a particular ordering of subroutines. Therefore, it is
essential that at least the order of children is expressed in a list.

!!! note

    When constructing instances of QREF pydantic models, lists of ports and
    resources are sorted alphabetically by name. However, initial order
    of children is always preserved.

## Why isn't the program a top level object?

The actual program you are representing in QREF is stored
as the `program` property of a top-level schema object, i.e.

```yaml
version: v1
program:
  name: my_program
  children:
    # ...
```
You might wonder why wouldn't we just make the program a
top-level object, or, in other words, why don't QREF
documents look like this instead:

```yaml
version: v1
name: my_program
children:
  # ...
```

There are essentially two reasons, but both of them
have to do with the fact that we wanted our structure
to be recursive.

To quickly explain what recursive in this context means,
let's think about `program` and its `children`. Both of
them can be viewed as objects of the same type. The
`program` is a *routine* which can contain other routines
as its `children`. Each of the children can have
other routines as their children etc. It's routines all
the way down.

Now, if we used a top-level object to represent a program,
we face a problem - we need to include version only in
this object and not in the children. Therefore we would
have to create a separate type for the main program
and separate one for subroutines. This would have the
following consequences, listed in the order of importance:

- The JSON schema would no longer be recursive, and thus
  would contain more definitions, which simply means
  it would be more complex and harder to read.
- The hierarchy of our Pydantic models would get slightly
  more complex.

We don't mind putting effort into creating more complex
hierarchy of models if it would add usability. However, we
think that having the JSON schema as simple as possible
is beneficial to the users (especially considering that
QREF is mostly a data format!), and thus we made a choice
of using the recursive type hierarchy.


