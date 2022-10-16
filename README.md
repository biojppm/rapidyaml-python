# Rapid YAML
[![MIT Licensed](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/biojppm/rapidyaml/blob/master/LICENSE.txt)
[![PyPI](https://img.shields.io/pypi/v/rapidyaml?color=g)](https://pypi.org/project/rapidyaml/)

Or ryml, for short. ryml is [a C++ library to parse and emit
YAML](https://github.com/biojppm/rapidyaml), and do it fast, on
everything from x64 to bare-metal chips without operating system. This
repo contains the rapidyaml python package, which was previously in
the original repo.

(Note that this is a work in progress. Additions will be made and
things will be changed.).

The python port is using only the index-based low-level API, which
works with node indices and string views. This API is fast, but you
may find it hard to use: it does not build a python structure of
dicts/seqs/scalars, and all the scalars are strings, and not
typed. With that said, it is really fast, and once you have the tree
you can still walk over the tree to create the native python
structure. Have a look at this [test file](test/test_ryml.py) to see
how the python API works, and to judge whether it may be useful to
your case.

As for performance, in a [timeit benchmark](bm/parse_bm.py)
compared against [PyYaml](https://pyyaml.org/) and
[ruamel.yaml](https://yaml.readthedocs.io/en/latest/), ryml parses
quicker by generally 100x and up to 400x:

```
+----------------------------------------+-------+----------+----------+-----------+
| style_seqs_blck_outer1000_inner100.yml | count | time(ms) | avg(ms)  | avg(MB/s) |
+----------------------------------------+-------+----------+----------+-----------+
| parse:RuamelYamlParse                  |     1 | 4564.812 | 4564.812 |     0.173 |
| parse:PyYamlParse                      |     1 | 2815.426 | 2815.426 |     0.280 |
| parse:RymlParseInArena                 |    38 |  588.024 |   15.474 |    50.988 |
| parse:RymlParseInArenaReuse            |    38 |  466.997 |   12.289 |    64.202 |
| parse:RymlParseInPlace                 |    38 |  579.770 |   15.257 |    51.714 |
| parse:RymlParseInPlaceReuse            |    38 |  462.932 |   12.182 |    64.765 |
+----------------------------------------+-------+----------+----------+-----------+
```
(Note that the parse timings above are somewhat biased towards ryml, because
it does not perform any type conversions in Python-land: return types
are merely `memoryviews` to the source buffer, possibly copied to the tree's
arena).

As for emitting, the improvement can be as high as 3000x:
```
+----------------------------------------+-------+-----------+-----------+-----------+
| style_maps_blck_outer1000_inner100.yml | count |  time(ms) |  avg(ms)  | avg(MB/s) |
+----------------------------------------+-------+-----------+-----------+-----------+
| emit_yaml:RuamelYamlEmit               |     1 | 18149.288 | 18149.288 |     0.054 |
| emit_yaml:PyYamlEmit                   |     1 |  2683.380 |  2683.380 |     0.365 |
| emit_yaml:RymlEmitToNewBuffer          |    88 |   861.726 |     9.792 |    99.976 |
| emit_yaml:RymlEmitReuse                |    88 |   437.931 |     4.976 |   196.725 |
+----------------------------------------+-------+-----------+-----------+-----------+
```

------
## License

ryml is permissively licensed under the [MIT license](LICENSE.txt).
