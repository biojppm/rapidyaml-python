import ryml


# all the tests below create this tree
expected_yaml = '{HELLO: a,foo: b,bar: c,baz: d,seq: [0,1,2,3]}'
expected_json = '{"HELLO": "a","foo": "b","bar": "c","baz": "d","seq": [0,1,2,3]}'


# helper to create map children nodes
def _append_keyval(tree: ryml.Tree, node_id: int, key, val, flags=0):
    child_id = tree.append_child(node_id)
    tree.to_keyval(child_id, key, val, flags)
    return child_id


# helper to create seq children nodes
def _append_val(tree: ryml.Tree, node_id: int, val, flags=0):
    child_id = tree.append_child(node_id)
    tree.to_val(child_id, val, flags)
    return child_id


def test_create_tree():
    tree = ryml.Tree()
    root_id = tree.root_id()
    tree.to_map(root_id, ryml.FLOW_SL) # set the root node as a map,
                                       # with FLOW_SL style (flow, single line)
    _append_keyval(tree, root_id, "HELLO", "a")
    _append_keyval(tree, root_id, "foo", "b")
    _append_keyval(tree, root_id, "bar", "c")
    _append_keyval(tree, root_id, "baz", "d")
    seq_id = tree.append_child(root_id)
    tree.to_seq(seq_id, "seq", ryml.FLOW_SL)  # append a sequence
    _append_val(tree, seq_id, "0")
    _append_val(tree, seq_id, "1")
    _append_val(tree, seq_id, "2")
    _append_val(tree, seq_id, "3")
    # check that this tree is emitted as expected
    _check_emits(tree)


# BEWARE! The tree is pointing at the memory of the scalars!
#
# If you are using dynamic strings for scalars, you must be sure to
# hold onto them while using the tree!
#
# Because explicitly managing lifetimes is generally hard or
# cumbersome to do in python, ryml provides you a tree.to_arena()
# helper to do this: it copies the scalar to the tree's arena, which
# will fix any lifetime issues.
#
# Here's an example:
def test_create_tree_dynamic():
    # let's now programmatically create the same tree as above:
    tree = ryml.Tree()
    root_id = tree.root_id()
    tree.to_map(root_id, ryml.FLOW_SL) # set the root node as a map,
                                       # with FLOW_SL style (flow, single line)
    # utility function to create a dynamic string and store it in the tree:
    def ds(s: str):
        # make a dynamic copy (using f-string to force creation a
        # different string object)
        dyn = f"_{s}_"[1:-1]
        # ...serialize the copy in the tree's arena
        saved = tree.to_arena(dyn)
        return saved
    # now we use ds() with each scalar, making it safer
    _append_keyval(tree, root_id, ds("HELLO"), ds("a"))
    _append_keyval(tree, root_id, ds("foo"), ds("b"))
    _append_keyval(tree, root_id, ds("bar"), ds("c"))
    _append_keyval(tree, root_id, ds("baz"), ds("d"))
    seq_id = tree.append_child(root_id)
    tree.to_seq(seq_id, ds("seq"), ryml.FLOW_SL)  # append a sequence
    _append_val(tree, seq_id, ds("0"))
    _append_val(tree, seq_id, ds("1"))
    _append_val(tree, seq_id, ds("2"))
    _append_val(tree, seq_id, ds("3"))
    # check that this tree is emitted as expected
    _check_emits(tree)


# But note you don't need to use tree.to_arena(); you can save the
# dynamic scalars for example by keeping them in a tree. But then you
# must take care of the lifetimes!
#
# Here's an example:
def test_create_tree_dynamic_explicit_save():
    # let's now programmatically create the same tree as above:
    tree = ryml.Tree()
    root_id = tree.root_id()
    tree.to_map(root_id, ryml.FLOW_SL) # set the root node as a map,
                                       # with FLOW_SL style (flow, single line)
    # this time we'll use a list to save the scalars. It works because
    # both `tree` and `saved_scalars` are defined and used in the same
    # scope. But it would fail if `saved_scalars` went out of scope
    # before ending the use of `tree`, eg if tree was returned from
    # this function but `saved_scalars` were not.
    saved_scalars = []
    # utility function to create a dynamic string and store it:
    def ds(s: str):
        # make a dynamic copy (using f-string to force creation a
        # different string object)
        dyn = f"_{s}_"[1:-1]
        # save the string in the list
        saved_scalars.append(dyn)
        return dyn
    # now we use ds() with each scalar, making it safer
    _append_keyval(tree, root_id, ds("HELLO"), ds("a"))
    _append_keyval(tree, root_id, ds("foo"), ds("b"))
    _append_keyval(tree, root_id, ds("bar"), ds("c"))
    _append_keyval(tree, root_id, ds("baz"), ds("d"))
    seq_id = tree.append_child(root_id)
    tree.to_seq(seq_id, ds("seq"), ryml.FLOW_SL)  # append a sequence
    _append_val(tree, seq_id, ds("0"))
    _append_val(tree, seq_id, ds("1"))
    _append_val(tree, seq_id, ds("2"))
    _append_val(tree, seq_id, ds("3"))
    # check that this tree is emitted as expected
    _check_emits(tree)


def test_create_tree_bytes():
    # ryml also works with bytes scalars
    tree = ryml.Tree()
    root_id = tree.root_id()
    tree.to_map(root_id, ryml.FLOW_SL) # set the root node as a map,
                                       # with FLOW_SL style (flow, single line)
    _append_keyval(tree, root_id, b"HELLO", b"a")
    _append_keyval(tree, root_id, b"foo", b"b")
    _append_keyval(tree, root_id, b"bar", b"c")
    _append_keyval(tree, root_id, b"baz", b"d")
    seq_id = tree.append_child(root_id)
    tree.to_seq(seq_id, b"seq", ryml.FLOW_SL)  # append a sequence
    _append_val(tree, seq_id, b"0")
    _append_val(tree, seq_id, b"1")
    _append_val(tree, seq_id, b"2")
    _append_val(tree, seq_id, b"3")
    # check that this tree is emitted as expected
    _check_emits(tree)


def test_create_tree_memoryview():
    # ryml also works with memoryview scalars
    tree = ryml.Tree()
    root_id = tree.root_id()
    tree.to_map(root_id, ryml.FLOW_SL) # set the root node as a map,
                                       # with FLOW_SL style (flow, single line)
    def s(scalar: bytes):
        return memoryview(scalar)
    _append_keyval(tree, root_id, s(b"HELLO"), s(b"a"))
    _append_keyval(tree, root_id, s(b"foo"), s(b"b"))
    _append_keyval(tree, root_id, s(b"bar"), s(b"c"))
    _append_keyval(tree, root_id, s(b"baz"), s(b"d"))
    seq_id = tree.append_child(root_id)
    tree.to_seq(seq_id, s(b"seq"), ryml.FLOW_SL)  # append a sequence
    _append_val(tree, seq_id, s(b"0"))
    _append_val(tree, seq_id, s(b"1"))
    _append_val(tree, seq_id, s(b"2"))
    _append_val(tree, seq_id, s(b"3"))
    # check that this tree is emitted as expected
    _check_emits(tree)


# this function shows several different ways of emitting from an
# existing tree (and tests that the results are as expected).
def _check_emits(tree: ryml.Tree):
    # emit_yaml() and emit_json() return a str object
    out_yaml = ryml.emit_yaml(tree)
    out_json = ryml.emit_json(tree)
    assert isinstance(out_yaml, str)
    assert isinstance(out_json, str)
    assert out_yaml == expected_yaml
    assert out_json == expected_json
    # if it is really important, you can emit to existing buffers:
    len_yaml = ryml.compute_yaml_length(tree) #
    len_json = ryml.compute_json_length(tree)
    buf_yaml = bytearray(len_yaml)
    buf_json = bytearray(len_json)
    out_yaml = ryml.emit_yaml_in_place(tree, buf_yaml)
    out_json = ryml.emit_json_in_place(tree, buf_json)
    assert isinstance(out_yaml, memoryview)
    assert isinstance(out_json, memoryview)
    assert out_yaml.tobytes().decode('utf8') == expected_yaml
    assert out_json.tobytes().decode('utf8') == expected_json
