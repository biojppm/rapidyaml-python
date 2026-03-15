import ryml

def test_read_yaml():
    yaml = b"{HELLO: a, foo: b, bar: c, baz: d, seq: [0, 1, 2, 3]}"

    # ryml holds only views to the parsed yaml source (following the C++ library).
    #
    # parse_in_place() parses directly the input buffer,
    # so this requires the user to keep the input buffer
    # alive while using the tree.
    #
    # parse_in_arena() copies the input buffer to
    # an arena in the tree, then parses the copy.
    # This is safer, so let's use it here:
    tree = ryml.parse_in_arena(yaml)

    # The returned tree has the following structure:
    #
    #   [node 0] root, map
    #     ` [node 1] "HELLO": "a"
    #     ` [node 2] "foo": "b"
    #     ` [node 3] "bar": "c"
    #     ` [node 4] "baz": "d"
    #     ` [node 5] "seq":
    #         ` [node 6] "0"
    #         ` [node 7] "1"
    #         ` [node 8] "2"
    #         ` [node 9] "3"
    #
    # let's now do some assertions (keeping this structure in mind):
    assert tree.size() == 10
    assert tree.root_id() == 0
    assert tree.is_root(0)
    assert tree.is_map(0)
    assert tree.is_keyval(1)
    assert tree.is_seq(5)
    assert tree.is_val(6)
    # use bytes or str objects for queries
    assert tree.find_child(0, b"HELLO") == 1
    assert tree.find_child(0, "HELLO") == 1
    assert tree.find_child(0, b"foo") == 2
    assert tree.find_child(0, "foo") == 2
    assert tree.find_child(0, b"seq") == 5
    assert tree.find_child(0, "seq") == 5
    assert tree.key(1) == b"HELLO"
    assert tree.val(1) == b"a"
    assert tree.key(2) == b"foo"
    assert tree.val(2) == b"b"
    assert tree.find_child(0, b"seq") == 5
    assert tree.find_child(0, "seq") == 5
    # hierarchy:
    assert tree.first_child(0) == 1
    assert tree.last_child(0) == 5
    assert tree.next_sibling(1) == 2
    assert tree.first_sibling(5) == 1
    assert tree.last_sibling(1) == 5
    assert tree.first_child(5) == 6
    assert tree.last_child(5) == 9
    # to loop over children:
    expected = [b"0", b"1", b"2", b"3"]
    for i, ch in enumerate(ryml.children(tree, 5)):
        assert tree.val(ch) == expected[i]
    # to loop over siblings:
    expected = [b"HELLO", b"foo", b"bar", b"baz", b"seq"]
    for i, sib in enumerate(ryml.siblings(tree, 5)):
        assert tree.key(sib) == expected[i]
    # to walk over all elements
    visited = [False] * tree.size()
    for node_id, indentation_level in ryml.walk(tree):
        visited[node_id] = True
    assert False not in visited
    # NOTE about encoding!
    k = tree.key(5)
    assert isinstance(k, memoryview)
    #print(k)  # '<memory at 0x7f80d5b93f48>'
    assert k == b"seq"               # ok, as expected
    assert k != "seq"                # not ok - NOTE THIS!
    assert str(k) != "seq"           # not ok
    assert str(k, "utf8") == "seq"   # ok again
