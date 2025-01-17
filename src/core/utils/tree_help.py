from treebeard.mp_tree import MP_Node

"""
cache parents and children of tree (like mptt cache tree)
"""


def add_top_node(obj: MP_Node, top_nodes: list, path: list) -> None:
    """forming a list with top(root) nodes"""
    # empty list; or del lst[:]
    top_nodes.append(obj)
    path.clear()


def add_child(parent: MP_Node, obj: MP_Node) -> None:
    obj._cached_parent = parent
    parent._cached_children.append(obj)


def is_child_of(child: MP_Node, parent: MP_Node) -> bool:
    """
    return whether `child` is a sub categ of `parent` without database query
    `_get_children_path_interval` (see built-in MP_Node)
    """
    start, end = parent._get_children_path_interval(parent.path)
    return start < child.path < end


def get_cached_trees(queryset) -> list:
    """This avoids having to query the database.
    queryset contains only root obj
    Each categ will have its
    children stored in `_cached_children` attr
    parent in `_cached_parent` attr
    """
    top_nodes: list = []
    path: list = []
    for obj in queryset:
        obj._cached_children = []
        if obj.depth == queryset[0].depth:
            add_top_node(obj, top_nodes, path)
        else:
            while not is_child_of(obj, parent := path[-1]):
                path.pop()
            add_child(parent, obj)

        if obj.numchild:
            # amount of children
            path.append(obj)

    return top_nodes
