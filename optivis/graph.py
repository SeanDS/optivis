# -*- coding: utf-8 -*-

"""Graph data structures and algorithms.

A graph is typically represented as G=(V,E) where V are vertices and E are
edges. All vertices in a graph have unique ids. Edges are directed edges and are
identified by an ordered pair of vertices (v1, v2). All edges are unique ordered
pairs. Associated with each edge is a value.

A graph is implemented as a dictionary of which the keys are vertices.
Associated with each vertex is (again) a dictionary of which the keys are the
vertices to which there is an edge. Associated with each edge is a value. (A
graph is implemented as a dictionary of dictionaries).

The reverse of the graph is also stored and kept up to date, for fast
determination of incoming edges and other algorithms."""

from __future__ import unicode_literals, division

from optivis.layout.geosolver.notify import Notifier

class Graph(Notifier):
    """A weighted directed graph"""

    def __init__(self, graph=None):
        # initialise parent
        Notifier.__init__(self)

        # forward and reverse edges are stored in a dictionary of dictionaries
        self._forward = {}
        self._reverse = {}

        # copy input graph
        if graph:
            # copy vertices
            map(self.add_vertex, graph.vertices())

            # set up edges between vertices
            map(self.set, [(v, w, graph.get(v, w)) for v, w in graph.edges()])

    def add_vertex(self, vertex):
        """Add vertex to graph

        :param vertex: vertex to add
        """

        if vertex in self._forward:
            # already in dict
            return

        # add vertex to each dict
        self._forward[vertex] = {}
        self._reverse[vertex] = {}

        # notify listeners
        self.send_notify(("add_vertex", vertex))

    def remove_vertex(self, vertex):
        """Remove vertex and incident edges

        :param vertex: vertex to remove
        """

        if vertex not in self._forward:
            raise Exception("Vertex not in graph")

        # remove edges going to and from vertex
        map(lambda u: self.remove_edge(u, vertex), self.ingoing_vertices(vertex))
        map(lambda w: self.remove_edge(vertex, w), self.outgoing_vertices(vertex))

        # remove vertex in dicts
        del self._forward[vertex]
        del self._reverse[vertex]

        # notify listeners
        self.send_notify(("remove_vertex", vertex))

    def add_edge(self, v1, v2, value=1):
        """Add edge with optional value

        :param v1: first vertex
        :param v2: second vertex
        :param value: optional value
        """

        # add vertices
        if v1 not in self._forward:
            self.add_vertex(v1)

        if v2 not in self._forward:
            self.add_vertex(v2)

        # add edge
        if v2 not in self._forward[v1]:
            self._forward[v1][v2] = value

        # and the reverse edge
        if v1 not in self._reverse[v2]:
            self._reverse[v2][v1] = value

        # notify listeners
        self.send_notify(("add_edge", (v1, v2, value)))

    def remove_edge(self, v1, v2):
        """Remove edge

        :param v1: first vertex
        :param v2: second vertex
        """

        if not self.has_edge(v1,v2):
            raise Exception("Edge not in graph")

        # remove edges from dicts
        del self._forward[v1][v2]
        del self._reverse[v2][v1]

        # notify listeners
        self.send_notify(("remove_edge", (v1, v2)))

    def add_bi_edge(self, v1, v2, *args, **kwargs):
        """Add bidirectional edge with optional value

        Supports the optional parameters of :meth:`add_edge`.

        :param v1: first vertex
        :param v2: second vertex
        """

        # add edges in each direction
        self.add_edge(v1, v2, *args, **kwargs)
        self.add_edge(v2, v1, *args, **kwargs)

    def remove_bi_edge(self, v1, v2):
        """Remove bidirectional edge

        :param v1: first vertex
        :param v2: second vertex
        """

        self.remove_edge(v1, v2)
        self.remove_edge(v2, v1)

    def has_vertex(self, vertex):
        """Check if this graph contains the specified vertex

        :param vertex: vertex to check
        :returns: True if the graph contains the vertex, False otherwise
        :rtype: boolean
        """

        return vertex in self._forward

    def has_edge(self, v1, v2):
        """Check if this graph contains the edge specified by the two vertices

        :param v1: first vertex
        :param v2: second vertex
        :returns: True if the graph contains the edge, False otherwise
        :rtype: boolean
        """

        if v1 not in self._forward:
            return False

        return v2 in self._forward[v1]

    def has_bi_edge(self, v1, v2):
        """Check if the specified vertices are connected in both directions

        :param v1: first vertex
        :param v2: second vertex
        :returns: True if the graph contains the bidirectional edge, False \
        otherwise
        :rtype: boolean
        """

        return self.has_edge(v1, v2) and self.has_edge(v2, v1)

    def has_any_edge(self, v1, v2):
        """Check if the specified vertices are connected in either direction

        :param v1: first vertex
        :param v2: second vertex
        :returns: True if the graph contains an edge, False otherwise
        :rtype: boolean
        """

        return self.has_edge(v1, v2) or self.has_edge(v2, v1)

    def get(self, v1, v2):
        """Get value of edge

        :param v1: first vertex
        :param v2: second vertex
        :returns: value of edge
        :rtype: hashable
        """

        return self._forward[v1][v2]

    def set(self, v1, v2, value):
        """Set value of edge, adding it if it doesn't yet exist

        :param v1: first vertex
        :param v2: second vertex
        :param value: vertex value
        """

        if not self.has_edge(v1, v2):
            # add new edge and set value
            self.add_edge(v1, v2, value)
        else:
            # set edge value
            self._forward[v1][v2] = value
            self._reverse[v2][v1] = value

            # notify listeners
            self.send_notify(("set", (v1, v2, value)))

    def set_bi_edge(self, v1, v2, value):
        """Set value of bidirectional edge, adding them if they doesn't yet \
        exist

        :param v1: first vertex
        :param v2: second vertex
        :param value: vertex value
        """

        self.set(v1, v2, value)
        self.set(v2, v1, value)

    def vertices(self):
        """Get a list of vertices in this graph"""

        return self._forward.keys()

    def edges(self):
        """Get a list of the edges in this graph"""

        # empty list
        l = []

        for i in self._forward:
            for j in self._forward[i]:
                l.append((i, j))

        return l

    def subgraph(self, vertices):
        """Derive subgraph containing specified vertices and enclosed edges

        :param vertices: list of vertices to include
        :returns: new subgraph
        :rtype: :class:`Graph`
        """

        # new empty graph
        g = Graph()

        for v in filter(self.has_vertex, vertices):
            # vertex is in the list, so add to new graph
            g.add_vertex(v)

            # copy associated edges
            for w in self._forward[v]:
                if w in vertices:
                    # copy over the edge's value
                    g.set(v, w, self.get(v, w))

        return g

    def copy(self):
        """Return a copy of this graph as a new object"""

        return self.subgraph(self.vertices())

    def outgoing_vertices(self, vertex):
        """Get a list of vertices connected from the specified vertex via an \
        edge

        :param vertex: vertex to use as a reference
        """

        # look up forward graph
        return self._forward[vertex].keys()

    def ingoing_vertices(self, vertex):
        """Get a list of vertices connected to the specified vertex via an \
        edge

        :param vertex: vertex to use as a reference
        """

        # look up the reverse graph
        return self._reverse[vertex].keys()

    def adjacent_vertices(self, vertex):
        """Get a list of adjacent (ingoing or outgoing) vertices

        :param vertex: vertex to use as a reference
        """

        # return union of ingoing and outgoing vertices
        return list(set(self.ingoing_vertices(vertex)).union(set(self.outgoing_vertices(vertex))))

    def ingoing_edges(self, vertex):
        """Get a list of edges connecting towards the specified vertex

        :param vertex: vertex to retrieve edges for
        """

        return [(v, vertex) for v in self.ingoing_vertices(vertex)]

    def outgoing_edges(self, vertex):
        """Get a list of edges connecting away from the specified vertex

        :param vertex: vertex to retrieve edges for
        """

        return [(v, vertex) for v in self.outgoing_vertices(vertex)]

    def adjacent_edges(self, vertex):
        """Get a list of ingoing and outgoing edges

        :param vertex: vertex to retrieve edges for
        """

        return self.ingoing_edges(vertex) + self.outgoing_edges(vertex)

    def reverse(self):
        """Get a copy of this graph with the edges reversed"""

        # new empty graph
        g = Graph()

        # add swapped edges
        map(lambda v1, v2: g.add_edge(v2, v1), *self.edges())

        return g

    def path(self, start, end):
        """Gets an arbitrary path (list of vertices) from start to end

        If start is equal to end, then the path is a cycle
        If there is no path between start and end, then an empty list is
        returned

        :param start: start vertex
        :param end: end vertex
        :returns: list of vertices connecting start and end
        :rtype: list
        """

        # map from vertices to shortest path to that key vertex
        trails = {}

        # set start vertex
        trails[start] = [start]

        # list of vertices to consider
        consider = [start]

        # loop until there are no vertices to consider
        while len(consider) > 0:
            # next key to consider
            key = consider.pop()

            # current path
            this_path = trails[key]

            for v in self.outgoing_vertices(key):
                if v == end:
                    # found the end, so return the path we have taken
                    return this_path + [v]
                elif v not in trails:
                    # add vertex to trails taken
                    trails[v] = this_path + [v]

                    # add the vertex to the list to be searched
                    consider.append(v)
                elif len(this_path) + 1 < len(trails[v]):
                    # this trail is shorter than a previous one, so overwrite
                    trails[v] = this_path + [v]

        # no path found
        return []

    def connected(self, vertex, ingoing=True, outgoing=True):
        """Gets vertices x connected to the specified vertex by following \
        edges connected to specified vertex or x

        The edges can be unidirectional or bidirectional as specified by the
        optional ingoing and outgoing flags.

        Specified vertex is not included in the result.

        :param vertex: vertex to start at
        :param ingoing: include ingoing edges
        :param outgoing: include outgoing edges
        """

        # work out which edge function to use
        if ingoing and outgoing:
            vertex_edge_func = self.adjacent_vertices
        elif ingoing:
            vertex_edge_func = self.ingoing_vertices
        else:
            vertex_edge_func = self.outgoing_vertices

        # vertices being searched
        front = [vertex]

        # connected vertices
        connected = {}

        # loop until there are no more connected vertices to follow
        while len(front) > 0:
            # get next connected vertex
            x = front.pop()

            # add vertex to dict
            if x not in connected:
                # add vertex
                connected[x] = 1

                # add connected vertices to search list
                front += vertex_edge_func(x)

        # delete the supplied vertex
        del connected[vertex]

        # convert result to a list
        return list(connected)

    def connected_via_outgoing(self, *args, **kwargs):
        """Gets vertices x connected from specified vertex by following only \
        outgoing edges from specified vertex or x

        :param vertex: vertex to start at
        """

        # return only outgoing connected edges
        return connected(ingoing=False, outgoing=True, *args, **kwargs)

    def connected_via_ingoing(self, *args, **kwargs):
        """Gets vertices x connected from specified vertex by following only \
        ingoing edges from specified vertex or x

        :param vertex: vertex to start at
        """

        # return only outgoing connected edges
        return connected(ingoing=True, outgoing=False, *args, **kwargs)

    def connected_subsets(self):
        """Gets a set of (undirectionally) connected subsets of vertices"""

        # set of vertices to get subsets for
        to_check = set(self.vertices())

        # empty set of subsets
        subsets = set()

        while len(to_check) > 0:
            # get next vertex
            vertex = to_check.pop()

            # set of vertices connected to this one
            connected = set(self.connected(vertex))

            # remove vertices connected to this one from check list
            map(to_check.remove, connected)

            # add this vertex to the list of connected vertices
            connected.add(v)

            # add this subset to the set
            subsets.add(connected)

        return subsets

    def __unicode__(self):
        s = ""

        for i in self._forward:
            v = ", ".join(["{0}: {1}".format(unicode(j), unicode(self.get(i, j))) for j in self._forward[i]])

            s += "{0}: {{1}}".format(unicode(i), v)

        return "{{0}}".format(s)

    def __str__(self):
        return unicode(self).encode('utf-8')
