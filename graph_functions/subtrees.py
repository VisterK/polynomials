class SubtreesGetter:

    def __init__(self, edges, start):
        self._edges = edges
        self._start = start
        self._possible_subtrees = []
        self.size = len(self._edges)
        self.find_all_graphs()

    def find_all_graphs(self, options=None):
        if options is None:
            options = []
        if len(options) == self.size:
            self._possible_subtrees.append(options.copy())
            return
        options.append(False)
        self.find_all_graphs(options)
        options.pop()
        options.append(True)
        self.find_all_graphs(options)
        options.pop()

    def get_subtrees(self):
        subtrees = []
        for option in self._possible_subtrees:
            if self.check_if_subtree(option):
                subtree = []
                for i in range(self.size):
                    if option[i]:
                        subtree.append(i)
                subtrees.append(subtree.copy())
        return subtrees

    def get_options(self):
        options = []
        for option in self._possible_subtrees:
            if self.check_if_subtree(option):
                options.append(option.copy())
        return options

    def check_if_subtree(self, option):
        was = [False] * len(self._edges)
        self.depth_first_search(self._start, option, was)
        for i in range(self.size):
            if was[i] != option[i]:
                return False
        return True

    def depth_first_search(self, vertex, option, was):
        was[vertex] = True
        for edge in self._edges[vertex]:
            if option[edge] and not was[edge]:
                self.depth_first_search(edge, option, was)

    def depth_first_search_paths(self, current_node, prev_node, edges, array, new_array):
        new_array.append(array.copy())
        for nodes in edges[current_node]:
            if nodes != prev_node:
                array.append(nodes)
                self.depth_first_search_paths(nodes, current_node, edges, array, new_array)
                array.pop()

    def get_all_paths(self, start_node, edges):
        new_array = []
        self.depth_first_search_paths(start_node, -1, edges, [start_node], new_array)
        return new_array

    def get(self):
        return self.get_options()

    def get_new_edges_list(self, option):
        new_edges = []
        for i in range(self.size):
            fake_array = []
            new_edges.append(fake_array)
        for i in range(self.size):
            for j in range(len(self._edges[i])):
                if option[i] and option[self._edges[i][j]]:
                    new_edges[i].append(self._edges[i][j])
        return new_edges
