# -*- coding: utf-8 -*-

"""Graph data structures and algorithms.

A graph is typically represented as G=(V,E) where V are vertices and E are
edges. All vertices in a graph are uniquely, i.e. have unique ids. Edges are
directed edges and are identified by an ordered pair of vertices (v1, v2). All
edges are unique, i.e. are unique ordered pairs. Associated with each edge is a
value.

A graph is implemented as a dictionary of which the keys are vertices.
Associated with each vertex is (again) a dictionary of which the keys are the
vertices to which there is an edge. Associated with each edge is a value. (A
graph is implemented as a dictionairy of dictionairies).

The add_* and rem_* methods ensure that the graph contains no edges to vertices
that are not in main dictionary (anymore).

The reverse of the graph is also sored and kept up to date, for fast
determination of incoming edges and other algorithms.

Also dictionaries are kept mapping vertices to fan-in and fanout numbers, and
mapping numbers to vertices with that fan-in/out number. This allows us to
quickly find sources, sinks, etc."""

from __future__ import unicode_literals, division

from optivis.layout.geosolver.notify import Notifier

class Graph(Notifier):
    """A weighted directed graph"""

    def __init__(self, graph=None):
        Notifier.__init__(self)
        self._dict = {}
        """the edges are stored in a dictionary of dictionaries"""
        self._reverse = {}
        """the reverse graph is stored here"""
        # copy input graph
        if graph:
            for v in graph.vertices():
                self.add_vertex(v)
            for e in graph.edges():
                (v,w) = e
                self.set(v,w,graph.get(v,w))
        #end __init__

    def add_vertex(self, v):
        "Add vertex to graph if not already."
        if v not in self._dict:
            self._dict[v] = {}
            self._reverse[v] = {}
            self.send_notify(("add_vertex",v))

    def add_edge(self, v1, v2, value=1):
        "Add edge from v1 to v2 with optional value."
        # add vertices of not in graph
        if v1 not in self._dict:
            self.add_vertex(v1)
        if v2 not in self._dict:
            self.add_vertex(v2);
        # add edge if not yet in graph
        if v2 not in self._dict[v1]:
            self._dict[v1][v2] = value
        # and the reverse edge in the reverse
        if v1 not in self._reverse[v2]:
            self._reverse[v2][v1] = value
            self.send_notify(("add_edge",(v1,v2,value)))

    def add_bi(self, v1, v2, value=1):
        "Add edges bi-directinally with optional value."
        self.add_edge(v1,v2, value)
        self.add_edge(v2,v1, value)

    def add_graph(self, graph):
        "Add all vertices and edges of given graph, and set edge values from given graph too."
        for v in graph.vertices():
            self.add_vertex(v)
        for e in graph.edges():
            (v,w) = e
            self.set(v,w,graph.get(v,w))


    def rem_vertex(self, v):
        "Remove vertex and incident edges."
        if v in self._dict:
            # remove edges going to vertex
            for u in self.ingoing_vertices(v):
                self.rem_edge(u,v)
            # remove edges going from vertex
            for w in self.outgoing_vertices(v):
                self.rem_edge(v,w)
            # remove vertex (and edges going from vertex)
            del self._dict[v]
            # and in the reverse
            del self._reverse[v]
            # notify
            self.send_notify(("rem_vertex",v))
        else:
            raise StandardError, "vertex not in graph"

    def rem_edge(self, v1, v2):
        "Remove edge."
        if self.has_edge(v1,v2):
            del self._dict[v1][v2]
            # remove from reverse
            del self._reverse[v2][v1]
            # notify
            self.send_notify(("rem_edge",(v1,v2)))
        else:
            raise StandardError, "edge not in graph"

    def rem_bi(self, v1, v2):
        "Remove edges bi-directionally."
        self.rem_edge(v1, v2)
        self.rem_edge(v2, v1)

    def has_vertex(self, v):
        "True if v a vertex of this graph."
        return v in self._dict

    def has_edge(self, v1, v2):
        "True if there is a directed edge (v1,v2) in this graph."
        if v1 in self._dict:
            return v2 in self._dict[v1]
        else:
            return False

    def has_bi(self, v1, v2):
        "True if both edges (v1,v2) and (v2,v1) are in this graph."
        return self.has_edge(v1,v2) and self.has_edge(v2,v1)

    def has_one(self, v1, v2):
        "True if either edge (v1,v2) or (v2,v1) is in this graph."
        return self.has_edge(v1,v2) or self.has_edge(v2,v1)

    def get(self, v1, v2):
        "Get value of edge (v1,v2)."
        return self._dict[v1][v2]

    def set(self, v1, v2, value):
        "Set value of edge (v1,v2) and add edge if it doesn't exist"
        if not self.has_edge(v1,v2):
            self.add_edge(v1,v2,value)
        else:
            self._dict[v1][v2] = value
            self._reverse[v2][v1] = value
            self.send_notify(("set",(v1,v2,value)))

    def set_bi(self, v1, v2, value):
        "Set value of edges (v1,v2) and (v2,v1)."
        self.set(v1,v2,value)
        self.set(v2,v1,value)

    def vertices(self):
        "List vertices"
        return self._dict.keys()

    def edges(self):
        "List edges"
        l = []
        for i in self._dict:
            for j in self._dict[i]:
                l.append((i, j))
        return l


    def subgraph(self, vertices):
        "Derive subgraph containing specified vertices and enclosed edges."
        g = Graph()
        # copy dictionairy for given vertices
        for v in vertices:
            if self.has_vertex(v):
                g.add_vertex(v)
                # copy edges
                for w in self._dict[v]:
                    if w in vertices:
                        g.set(v,w,self.get(v,w))
        return g

    def copy(self):
        return self.subgraph(self.vertices())

    def ingoing_vertices(self,vertex):
        """return list of vertices from which edge goes to given vertex"""
        # this is where keeping reverse graph pays off (also used in remove)
        return self._reverse[vertex].keys()

    def outgoing_vertices(self, vertex):
        """return list of vertices to which edge goes from given vertex"""
        return self._dict[vertex].keys()

    def adjacent_vertices(self, v):
        """list of adjacent (ingoing or outgoing) vertices"""
        from sets import Set
        iset = set(self.ingoing_vertices(v))
        oset = set(self.outgoing_vertices(v))
        vset = iset.union(oset)
        return list(vset)

    def ingoing_edges(self, vertex):
        """return list of incoming edges"""
        k = self.ingoing_vertices(vertex)
        l = []
        for v in k:
            l.append((v,vertex))
        return l

    def outgoing_edges(self, vertex):
        """return list of outgoing edges"""
        k = self.outgoing_vertices(vertex)
        l = []
        for v in k:
            l.append((vertex,v))
        return l

    def adjacent_edges(self, vertex):
        """return list of outgoing and outgoing edges"""
        return self.ingoing_edges(vertex) + self.outgoing_edges(vertex)

    def reverse(self):
        """return a reverse graph"""
        g = Graph()
        for e in self.edges():
            (v1,v2) = e
            g.add_edge(v2,v1)
        return g

    def path(self, start, end):
        """return an arbitrary path (list of vertices) from start to end.
        If start equal to end, then return a cycle.
        If no path, then return empty list.
        """
        # map from vertices to shortest path to that key vertex
        trails = {}
        trails[start] = [start]
        # list of vertices to considered now
        consider = [start]
        while len(consider) > 0:
            key = consider.pop()
            pth = trails[key]
            for v in self.outgoing_vertices(key):
                if v == end:
                    return pth + [v]
                elif v not in trails:
                    trails[v] = pth + [v]
                    consider.append(v)
                elif len(pth)+1 < len(trails[v]):
                    trails[v] = pth + [v]
            #endfor
        #endwhile
        return []
    #end def path

    def connected(self, v):
        """return vertices X connected to v by following edges ajdajecnt to v or X
        (v is not in the result)"""
        front = [v]
        result = {}
        while len(front) > 0:
            x = front.pop()
            if x not in result:
                result[x] = 1
                front += self.outgoing_vertices(x)
                front += self.ingoing_vertices(x)
        del result[v]
        return list(result)

    def connected_outgoing(self, v):
        """return vertices X connected from v by following only outgoing edges from v or X
        (v is not in the result)"""
        front = [v]
        result = {}
        while len(front) > 0:
            x = front.pop()
            if x not in result:
                result[x] = 1
                front += self.outgoing_vertices(x)
        del result[v]
        return list(result)

    def connected_ingoing(self, v):
        """return vertices X connected to v by following only ingoing edges to v or X (v is not in the result)"""
        front = [v]
        result = {}
        while len(front) > 0:
            x = front.pop()
            if x not in result:
                result[x] = 1
                front += self.ingoing_vertices(x)
        del result[v]
        return list(result)

    def connected_subsets(self):
        """returns a set of (undirectionally) connected subsets of vertices"""
        todo = set(self.vertices())
        subsets = set()
        while (todo):
            v = todo.pop()
            s = set(self.connected(v))
            for x in s:
                todo.remove(x)
            s.add(v)
            subsets.add(s)
        return subsets

    def mincut(self):
        """Returns a minimum cut of the graph.
           Implements the Stoer/Wagner algorithm. The graph is interpreted
           as a undirected graph, by adding the weights of co-edges.
           Returns (value, edges, g1, g2)
           where value is the weight of the cut,
           edges is the set of cut edges,
           g1 and g2 are disjoint sets of vertices.
        """
        # create graph of one-clusters
        graph = Graph()
        for edge in self.edges():
            (v1,v2) = edge
            g1 = frozenset([v1])
            g2 = frozenset([v2])
            graph.add_edge(g1,g2)

        # Stoer/Wagner algorithm
        mincutvalue = None
        mincut = frozenset()
        while len(graph.vertices()) > 1:
            (phasecut,phasecutvalue) = self._mincutphase(graph)
            if mincutvalue == None or phasecutvalue < mincutvalue:
                mincutvalue = phasecutvalue
                mincut = phasecut

        # rewrite output
        g1 = mincut
        g2 = frozenset(self.vertices()).difference(g1)
        edges = set()
        for v in g1:
            for k in self.adjacent_vertices(v):
                if k in g2:
                    if self.has_edge(v,k):
                        edges.add((v,k))
                    if self.has_edge(k,v):
                        edges.add((k,v))
        for v in g2:
            for k in self.adjacent_vertices(v):
                if k in g1:
                    if self.has_edge(v,k):
                        edges.add((v,k))
                    if self.has_edge(k,v):
                        edges.add((k,v))

        return (mincutvalue, frozenset(edges), g1, g2)

    def _mincutphase(self, graph):
        # returns the last vertex (group) added and the cut value
        #print "start cut phase"
        # select random vertex and add to 'done' set
        pick = random.choice(graph.vertices())
        done = [pick]
        #print "start:",pick
        # map vertices to cost of merge with done
        todo = {}
        for v in graph.vertices():
            todo[v] = 0
        del todo[pick]
        for v in graph.adjacent_vertices(pick):
            if v in todo:
                sum = todo[v]
                if graph.has_edge(v,pick):
                    sum = sum + graph.get(v,pick)
                if graph.has_edge(pick,v):
                    sum = sum + graph.get(pick,v)
                todo[v] = sum
        # add vertices to done, most tighly connected first
        while len(todo) > 0:
            # pick vertex
            todolist = list(todo)
            todolist = filter(lambda x: todo[x] > 0, todolist)   #connected!
            todolist.sort(lambda x,y: cmp(todo[x],todo[y]))
            if len(todolist) == 0:
                raise StandardError, "graph is not connected"
            pick = todolist[-1]
            # print "pick:",pick
            # store cut of the phase
            if len(todo) == 1:
                cut = pick
                cutvalue = todo[pick]
            # del from todo, add to done
            del todo[pick]
            done.append(pick)
            # update todo cost mapping
            for v in graph.adjacent_vertices(pick):
                if v in todo:
                    sum = todo[v]
                    if graph.has_edge(v,pick):
                        sum = sum + graph.get(v,pick)
                    if graph.has_edge(pick,v):
                        sum = sum + graph.get(pick,v)
                    todo[v] = sum
            # rof
        # elihw
        # merge last two added vertices
        last = done[len(done)-1]
        butlast = done[len(done)-2]
        mergetex = last.union(butlast)
        graph.add_vertex(mergetex)
        for v in graph.ingoing_vertices(last):
            graph.add_edge(v, mergetex)
        for v in graph.outgoing_vertices(last):
            graph.add_edge(mergetex,v)
        for v in graph.ingoing_vertices(butlast):
            graph.add_edge(v, mergetex)
        for v in graph.outgoing_vertices(butlast):
            graph.add_edge(mergetex,v)
        graph.rem_vertex(last)
        graph.rem_vertex(butlast)
        # klaar
        #print "cut, cutvalue:", cut, cutvalue
        return (cut,cutvalue)

    def __str__(self):
        """Create a string representation, using str() for each element"""
        s = ""
        s += "{"
        for i in self._dict:
            s += str(i)
            s += ":"
            s += "{"
            for j in self._dict[i]:
                s += str(j)
                s += ":"
                s += str(self.get(i,j))
                s += ","
            if len(self._dict[i]) > 0: s = s[:-1]
            s += "},"
        if len(self._dict) > 0: s = s[:-1]
        s += "}"
        return s

class FanGraph(Graph):
    """A graph with updated fan-in and fan-out numbers"""

    def __init__(self, graph=None):
        Notifier.__init__(self)
        self._dict = {}
        """the edges are stored in a dictionary of dictionaries"""
        self._reverse = {}
        """the reverse graph is stored here"""

        self._fanin = {}
        """map from vertices to fan-in number"""
        self._fanout = {}
        """map from vertices to fan-out number"""
        self._infan = {}
        """map from fan-in numbers to vertices with that fan-in"""
        self._outfan = {}
        """map from fan-out numbers to vertices with that fan-out"""
        # copy input graph
        if graph:
            for v in graph.vertices():
                self.add_vertex(v)
            for e in graph.edges():
                (v,w) = e
                self.set(v,w,graph.get(v,w))
    #end __init__

    def add_vertex(self, v):
        "Add vertex to graph if not already."
        if v not in self._dict:
            self._dict[v] = {}
            self._reverse[v] = {}
            self._set_fanin(v, 0)
            self._set_fanout(v, 0)
            self.send_notify(("add_vertex",v))

    def add_edge(self, v1, v2, value=1):
        "Add edge from v1 to v2 with optional value."
        # add vertices of not in graph
        if v1 not in self._dict:
            self.add_vertex(v1)
        if v2 not in self._dict:
            self.add_vertex(v2);
        # add edge if not yet in graph
        if v2 not in self._dict[v1]:
            self._dict[v1][v2] = value
        # and the reverse edge in the reverse
        if v1 not in self._reverse[v2]:
            self._reverse[v2][v1] = value
            # increment fan-out for v1
            self._set_fanout(v1, self._fanout[v1]+1)
            # increment fan-in for v2
            self._set_fanin(v2, self._fanin[v2]+1)
            # notify
            self.send_notify(("add_edge",(v1,v2,value)))

    def rem_vertex(self, v):
        "Remove vertex and incident edges."
        if v in self._dict:
            # remove edges going to vertex
            for u in self.ingoing_vertices(v):
                self.rem_edge(u,v)
            # remove edges going from vertex
            for w in self.outgoing_vertices(v):
                self.rem_edge(v,w)
            # remove entries from fan-in and fan-out tables
            self._set_fanin(v, None)
            self._set_fanout(v, None)
            # remove vertex (and edges going from vertex)
            del self._dict[v]
            # and in the reverse
            del self._reverse[v]
            # notify
            self.send_notify(("rem_vertex",v))
        else:
            raise StandardError, "vertex not in graph"

    def rem_edge(self, v1, v2):
        "Remove edge."
        if self.has_edge(v1,v2):
            del self._dict[v1][v2]
            # remove from reverse
            del self._reverse[v2][v1]
            # decrement fan-out for v1
            self._set_fanout(v1, self._fanout[v1]-1)
            # decrement fan-in for v2
            self._set_fanin(v2, self._fanin[v2]-1)
            # notify
            self.send_notify(("rem_edge",(v1,v2)))
        else:
            raise StandardError, "edge not in graph"

    def fanin(self, v):
        """return fan-in number (number of in-going edges)"""
        return self._fanin[v]

    def fanout(self, v):
        """return fan-out number (number of out-going edges)"""
        return self._fanout[v]

    def infan(self, number):
        """return a list of vertices with given fan-in number"""
        if number in self._infan:
            return list(self._infan[number])
        else:
            return []

    def outfan(self, number):
        """return a list of vertices with given fan-out number"""
        if number in self._outfan:
            return list(self._outfan[number])
        else:
            return []

    def fanin_numbers(self):
        """the set of fan-in numbers,
           i.e. the union of the fan-in numbers of all veretices
        """
        return self._infan.keys()

    def fanout_numbers(self):
        """the set of fan-out numbers,
        i.e. the union of the fan-out numbers of all veretices
        """
        return self._outfan.keys()

    def roots(self):
        """return a list of vertices with zero fan-in"""
        return self.infan(0)

    def leafs(self):
        """return a list of vertices with zero fan-out"""
        return self.outfan(0)

    def singular(self, number):
        """return a list of vertices with no fan-in and no fan-out"""
        l = self._infan[0]
        for v in l:
            if self._fanout[v] == 0:
                l.append(v)
        return l


    # overrides Graph.subgraph because it must return a FanGraph

    def subgraph(self, vertices):
        "Derive subgraph containing specified vertices and enclosed edges."
        g = FanGraph()
        # copy dictionairy for given vertices
        for v in vertices:
            if self.has_vertex(v):
                g.add_vertex(v)
                # copy edges
                for w in self._dict[v]:
                    if w in vertices:
                        g.set(v,w,self.get(v,w))
        return g


    # non-public methods

    def _set_fanin(self, vertex, number):
        # remove previous entry in infan dict
        if vertex in self._fanin: # test for new vertices
            old = self._fanin[vertex]
            l = self._infan[old]
            l.remove(vertex)
            if len(l) == 0: del self._infan[old]
        if number == None: # test for deleted vertices
            del self._fanin[vertex]
        else:
            # store new fanin
            self._fanin[vertex] = number
            # store in infan
            if number not in self._infan:
                self._infan[number] = []
            self._infan[number].append(vertex)

    def _set_fanout(self, vertex, number):
        # remove previous entry in outfan dict
        if vertex in self._fanout: # test for new vertices
            old = self._fanout[vertex]
            l = self._outfan[self._fanout[vertex]]
            l.remove(vertex)
            if len(l) == 0: del self._outfan[old]
        if number == None: # test for deleted vertices
            del self._fanout[vertex]
        else:
            # store new fanin
            self._fanout[vertex] = number
            # store in infan
            if number not in self._outfan:
                self._outfan[number] = []
            self._outfan[number].append(vertex)
