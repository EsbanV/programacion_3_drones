class AVL_visualizer:

    @staticmethod
    def hierarchy_pos(G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None):
        if pos is None:
            pos = {}
        if root is None:
            root = list(G.nodes)[0]
        children = list(G.successors(root))
        if not children:
            pos[root] = (xcenter, vert_loc)
        else:
            dx = width / 2
            left_x = xcenter - dx/2
            right_x = xcenter + dx/2
            if len(children) == 2:
                pos[root] = (xcenter, vert_loc)
                pos = AVL_visualizer.hierarchy_pos(G, children[0], width=dx, vert_gap=vert_gap,
                                                   vert_loc=vert_loc - vert_gap, xcenter=left_x, pos=pos, parent=root)
                pos = AVL_visualizer.hierarchy_pos(G, children[1], width=dx, vert_gap=vert_gap,
                                                   vert_loc=vert_loc - vert_gap, xcenter=right_x, pos=pos, parent=root)
            elif len(children) == 1:
                pos[root] = (xcenter, vert_loc)
                pos = AVL_visualizer.hierarchy_pos(G, children[0], width=dx, vert_gap=vert_gap,
                                                   vert_loc=vert_loc - vert_gap, xcenter=xcenter, pos=pos, parent=root)
        return pos


