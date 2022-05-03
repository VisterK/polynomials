import os

import sympy
from sympy import Symbol, latex

from graph_functions.bernoulli_barnes import get_rk
from graph_functions.subtrees import SubtreesGetter


class PolynomialGetter:
    def __init__(self, edges, start_vertex, weights):
        self._edges = edges
        self._start_vertex = start_vertex
        self._new_edges_list = []
        self._weights = weights
        self._bernoulli_barnes = []
        self.init_bernoulli_barnes()
        self._size = 0
        self._length = 0
        self._polynomial_first = None
        self._polynomial_second = None
        self.polynomial_result = None

    def init_bernoulli_barnes(self):
        for i in range(len(self._edges) + 1):
            self._bernoulli_barnes.append(get_rk(i))

    def set_ones(self):
        for i in range(len(self._weights)):
            for j in range(len(self._weights[0])):
                if self._weights[i][j] > 0:
                    self._weights[i][j] = 1

    def init_rk_first(self):
        rk = self._bernoulli_barnes[self._size - 1]
        rk = rk.subs(Symbol("lambda"), (Symbol("T") + self._length))
        pos = 1
        for u in range(len(self._new_edges_list)):
            for v in range(len(self._new_edges_list[u])):
                if u < self._new_edges_list[u][v]:
                    rk = rk.subs(Symbol('w_' + str(pos)), 2 * sympy.S(self._weights[u][self._new_edges_list[u][v]]))
                    pos += 1
        return rk

    def init_rk_second(self, path, first, second):
        rk = self._bernoulli_barnes[self._size - 2]
        sum_of_lengths = 0
        for i in range(1, len(path) - 1):
            sum_of_lengths += self._weights[path[i]][path[i - 1]]
        sum_of_lengths -= self._weights[first][second]
        rk = rk.subs(Symbol("lambda"), (Symbol("T") + sum_of_lengths))
        pos = 1
        for u in range(len(self._new_edges_list)):
            for v in self._new_edges_list[u]:
                if u < v and not (u == min(first, second) and v == max(first, second)):
                    rk = rk.subs(Symbol('w_' + str(pos)), 2 * sympy.S(self._weights[u][v]))
                    pos += 1
        return rk

    def write_file(self):
        path = os.path.abspath(os.curdir) + "\\latex.txt"
        f = open(path, "w")
        f.write(latex(self.polynomial_result))
        f.close()

    def get_first(self):
        s = SubtreesGetter(self._edges, self._start_vertex)
        all_subtrees = s.get()
        polynomial = 0
        for i in range(len(all_subtrees)):
            self._new_edges_list = s.get_new_edges_list(all_subtrees[i])
            all_paths = s.get_all_paths(self._start_vertex, self._new_edges_list)
            self._size = 0
            for vertex in all_subtrees[i]:
                if vertex:
                    self._size += 1
            for path in all_paths:
                self._length = 0
                print(all_subtrees[i])
                print(path)
                for j in range(1, len(path)):
                    diff = len(self._edges[path[j]]) - len(self._new_edges_list[path[j]])
                    self._length += self._weights[path[j]][path[j - 1]]
                    rk_polynomial = self.init_rk_first()
                    polynomial += diff * rk_polynomial
        self._polynomial_first = sympy.simplify(polynomial)

    def get_second(self):
        s = SubtreesGetter(self._edges, self._start_vertex)
        all_subtrees = s.get()
        polynomial = 0
        for i in range(len(all_subtrees)):
            self._new_edges_list = s.get_new_edges_list(all_subtrees[i])
            all_paths = s.get_all_paths(self._start_vertex, self._new_edges_list)
            self._size = 0
            for vertex in all_subtrees[i]:
                if vertex:
                    self._size += 1
            for path in all_paths:
                for j in range(1, len(path)):
                    if len(self._new_edges_list[path[j]]) < 2:
                        continue
                    rk_polynomial = self.init_rk_second(path, path[j - 1], path[j])
                    polynomial += rk_polynomial
        self._polynomial_second = sympy.simplify(polynomial)

    def get(self):
        self.get_first()
        self.get_second()
        self.polynomial_result = sympy.simplify(self._polynomial_first + self._polynomial_second)
        self.polynomial_result = sympy.collect(self.polynomial_result, Symbol("T"))
