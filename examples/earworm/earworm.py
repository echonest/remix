#!/usr/bin/env python
# encoding: utf=8

"""
earworm.py
(name suggested by Jonathan Feinberg on 03/10/10)

Accepts a song and duration on the commandline, and makes a new audio file of that duration.
Creates an optimal loop if specified for looping.

Created by Tristan Jehan and Jason Sundram.
"""

from copy import deepcopy
from optparse import OptionParser
import numpy as np
from numpy.matlib import repmat, repeat
from numpy import sqrt
import operator
import os
import sys

try:
    import networkx as nx
except ImportError:
    print """earworm.py requires networkx. 
    
If setuptools is installed on your system, simply:
easy_install networkx 

Otherwise, you can get it here: http://pypi.python.org/pypi/networkx

Get the source, unzip it, cd to the directory it is in and run:
    python setup.py install
"""
    sys.exit(1)

from echonest.action import Playback, Jump, Fadeout, render, display_actions
from echonest.audio import LocalAudioFile
# from echonest.cloud_support import AnalyzedAudioFile

from earworm_support import evaluate_distance, timbre_whiten, resample_features
from utils import rows, tuples, flatten


DEF_DUR = 600
MAX_SIZE = 800
MIN_RANGE = 16
MIN_JUMP = 16
MIN_ALIGN = 16
MAX_EDGES = 8
FADE_OUT = 3
RATE = 'beats'

def read_graph(name="graph.gpkl"):
    if os.path.splitext(name)[1] == ".gml": 
        return nx.read_gml(name)
    else: 
        return nx.read_gpickle(name)

def save_graph(graph, name="graph.gpkl"):
    if os.path.splitext(name)[1] == ".gml": 
        nx.write_gml(graph, name)
    else: 
        nx.write_gpickle(graph, name)

def print_screen(paths):
    for i, p in enumerate(paths):
        print i, [l[0] - i for l in p]

def save_plot(graph, name="graph.png"):
    """save plot with index numbers rather than timing"""
    edges = graph.edges(data=True)
    nodes = [edge[2]['source'] for edge in edges]
    order = np.argsort(nodes)
    edges =  [edges[i] for i in order.tolist()]
    new_edges = []
    for edge in edges:
        v = edge[2]['target'] - edge[2]['source']-1
        new_edges.append((edge[2]['source'], edge[2]['target']))
    DG = nx.DiGraph()
    DG.add_edges_from(new_edges)
    A = nx.to_agraph(DG)
    A.layout()
    A.draw(name)
    
def make_graph(paths, markers):
    DG = nx.DiGraph()
    # add nodes
    for i in xrange(len(paths)):
        DG.add_node(markers[i].start)
    # add edges
    edges = []
    for i in xrange(len(paths)):
        if i != len(paths)-1:
            edges.append((markers[i].start, markers[i+1].start, {'distance':0, 'duration': markers[i].duration, 'source':i, 'target':i+1})) # source and target for plots only
        edges.extend([(markers[i].start, markers[l[0]+1].start, {'distance':l[1], 'duration': markers[i].duration, 'source':i, 'target':l[0]+1}) for l in paths[i]])
    DG.add_edges_from(edges)
    return DG

def make_similarity_matrix(matrix, size=MIN_ALIGN):
    singles = matrix.tolist()
    points = [flatten(t) for t in tuples(singles, size)]
    numPoints = len(points)
    distMat = sqrt(np.sum((repmat(points, numPoints, 1) - repeat(points, numPoints, axis=0))**2, axis=1, dtype=np.float32))
    return distMat.reshape((numPoints, numPoints))

def get_paths(matrix, size=MIN_RANGE):
    mat = make_similarity_matrix(matrix, size=MIN_ALIGN)
    paths = []
    for i in xrange(rows(mat)):
        paths.append(get_loop_points(mat[i,:], size))
    return paths

def get_paths_slow(matrix, size=MIN_RANGE):
    paths = []
    for i in xrange(rows(matrix)-MIN_ALIGN+1):
        vector = np.zeros((rows(matrix)-MIN_ALIGN+1,), dtype=np.float32)
        for j in xrange(rows(matrix)-MIN_ALIGN+1):
            vector[j] = evaluate_distance(matrix[i:i+MIN_ALIGN,:], matrix[j:j+MIN_ALIGN,:])
        paths.append(get_loop_points(vector, size))
    return paths

# can this be made faster?
def get_loop_points(vector, size=MIN_RANGE, max_edges=MAX_EDGES):
    res = set()
    m = np.mean(vector)
    s = np.std(vector)
    for i in xrange(vector.size-size):
        sub = vector[i:i+size]
        j = np.argmin(sub)
        if sub[j] < m-s and j != 0 and j != size-1 and sub[j] < sub[j-1] and sub[j] < sub[j+1] and sub[j] != 0:
            res.add((i+j, sub[j]))
            i = i+j # we skip a few steps
    # let's remove clusters of minima
    res = sorted(res, key=operator.itemgetter(0))
    out = set()
    i = 0
    while i < len(res):
        tmp = [res[i]]
        j = 1
        while i+j < len(res):
            if res[i+j][0]-res[i+j-1][0] < MIN_RANGE:
                tmp.append(res[i+j])
                j = j+1
            else:
                break
        tmp = sorted(tmp, key=operator.itemgetter(1))
        out.add(tmp[0])
        i = i+j
    out = sorted(out, key=operator.itemgetter(1))
    return out[:max_edges]

def path_intersect(timbre_paths, pitch_paths):
    assert(len(timbre_paths) == len(pitch_paths))
    paths = []
    for i in xrange(len(timbre_paths)):
        t_list = timbre_paths[i]
        p_list = pitch_paths[i]
        t = [l[0] for l in t_list]
        p = [l[0] for l in p_list]
        r = filter(lambda x:x in t,p)
        res = [(v, t_list[t.index(v)][1] + p_list[p.index(v)][1]) for v in r]
        paths.append(res)
    return paths

def get_jumps(graph, mode='backward'):
    loops = []
    edges = graph.edges(data=True)
    for edge in edges:
        if mode == 'infinite' and edge[1] < edge[0] or edge[2]['distance'] == 0:
            loops.append(edge)
        if mode == 'backward' and edge[1] < edge[0]: 
            loops.append(edge)
        if mode == 'forward' and edge[0] < edge[1] and 1 < edge[2]['target']-edge[2]['source']:
            loops.append(edge)
    if mode == 'infinite':
        order = np.argsort([l[0] for l in loops]).tolist()
    if mode == 'backward': 
        order = np.argsort([l[0]-l[1]+l[2]['duration'] for l in loops]).tolist()
        order.reverse() # we want long loops first
    if mode == 'forward': 
        order = np.argsort([l[1]-l[0]-l[2]['duration'] for l in loops]).tolist()
        order.reverse() # we want long loops first
    loops =  [loops[i] for i in order]
    return loops

def trim_graph(graph):
    
    # trim first_node if necessary
    first_node = min(graph.nodes())
    deg = graph.degree(first_node)
    while deg <= 1:
        graph.remove_node(first_node)
        first_node = min(graph.nodes())
        deg = graph.degree(first_node)
        
    # trim last node if necessary
    last_node = max(graph.nodes())
    deg = graph.degree(last_node)
    while deg <= 1:
        graph.remove_node(last_node)
        last_node = max(graph.nodes())
        deg = graph.degree(last_node)
    
    return graph, first_node, last_node

def collect(edges, path):
    # kind slow but fine
    res = []
    for p in path:
        for e in edges:
            if (p[0], p[1]) == (e[0], e[1]):
                if e[2]['target']-e[2]['source'] == 1:
                    res.append(p)
                else:
                    res.append(e)
    return res
    
def infinite(graph, track, target):
    DG = nx.DiGraph()
    loops = get_jumps(graph, mode='backward')
    DG.add_edges_from(loops)
    DG, first_node, last_node = trim_graph(DG)
    
    def dist(node1, node2): return node2-node1
    
    # search for shortest path from last to first node
    alt = True
    path = []
    while path == []:
        edges = DG.edges(data=True)
        try:
            path = tuples(nx.astar_path(DG, last_node, first_node, dist))
        except:
            if alt == True:
                DG.remove_node(first_node)
                alt = False
            else:
                DG.remove_node(last_node)
                alt = True
            DG, first_node, last_node = trim_graph(DG)
            
    assert(path != []) # FIXME -- maybe find a few loops and deal with them
    
    res = collect(edges, path)
    res_dur = 0
    for r in res:
        if r[1] < r[0]: res_dur += r[2]['duration']
        else: res_dur += r[1]-r[0]
    
    # trim graph to DG size
    f_n = min(graph.nodes())
    while f_n < first_node:
        graph.remove_node(f_n)
        f_n = min(graph.nodes())
    l_n = max(graph.nodes())
    while last_node < l_n:
        graph.remove_node(l_n)
        l_n = max(graph.nodes())
    
    # find optimal path
    path = compute_path(graph, max(target-res_dur, 0))    
    path = path + res
    # build actions
    actions = make_jumps(path, track)
    actions.pop(-1)
    jp = Jump(track, actions[-1].source, actions[-1].target, actions[-1].duration)
    actions.pop(-1)
    actions.append(jp)
    return actions

def remove_short_loops(graph, mlp):
    edges = graph.edges(data=True)
    for e in edges:
        dist = e[2]['target'] - e[2]['source']
        if dist == 1: continue
        if mlp < dist: continue
        if dist <= -mlp+1: continue
        graph.remove_edge(e[0], e[1])

def one_loop(graph, track, mode='shortest'):
    jumps = get_jumps(graph, mode='backward')
    if len(jumps) == 0: return []
    loop = None
    if mode == 'longest':
        loop = jumps[0]
    else:
        jumps.reverse()
        for jump in jumps:
            if jump[1] < jump[0]:
                loop = jump
                break
    if loop == None: return []
    # Let's capture a bit of the attack
    OFFSET = 0.025 # 25 ms
    pb = Playback(track, loop[1]-OFFSET, loop[0]-loop[1])
    jp = Jump(track, loop[0]-OFFSET, loop[1]-OFFSET, loop[2]['duration'])
    return [pb, jp]
    
def compute_path(graph, target):

    first_node = min(graph.nodes())
    last_node = max(graph.nodes())
        
    # find the shortest direct path from first node to last node
    if target == 0:
        def dist(node1, node2): return node2-node1 # not sure why, but it works
        # we find actual jumps
        edges = graph.edges(data=True)
        path = tuples(nx.astar_path(graph, first_node, last_node, dist))
        res = collect(edges, path)
        return res
    
    duration = last_node - first_node
    if target < duration: 
        # build a list of sorted jumps by length.
        remaining = duration-target
        # build a list of sorted loops by length.
        loops = get_jumps(graph, mode='forward')
        
        def valid_jump(jump, jumps, duration):
            for j in jumps:
                if j[0] < jump[0] and jump[0] < j[1]:
                    return False
                if j[0] < jump[1] and jump[1] < j[1]:
                    return False
                if duration - (jump[1]-jump[0]+jump[2]['duration']) < 0:
                    return False
            if duration - (jump[1]-jump[0]+jump[2]['duration']) < 0:
                return False
            return True
        
        res = []
        while 0 < remaining:
            if len(loops) == 0: break
            for l in loops:
                if valid_jump(l, res, remaining) == True:
                    res.append(l)
                    remaining -= (l[1]-l[0]+l[2]['duration'])
                    loops.remove(l)
                    break
                if l == loops[-1]:
                    loops.remove(l)
                    break
        res = sorted(res, key=operator.itemgetter(0))
        
    elif duration < target:
        remaining = target-duration
        loops = get_jumps(graph, mode='backward')
        tmp_loops = deepcopy(loops)
        res = []
        # this resolution value is about the smallest denominator
        resolution = loops[-1][1]-loops[-1][0]-loops[-1][2]['duration']
        while remaining > 0:
            if len(tmp_loops) == 0: 
                tmp_loops = deepcopy(loops)
            d = -9999999999999999
            i = 0
            while d < resolution and i+1 <= len(tmp_loops):
                l = tmp_loops[i]
                d = remaining - (l[0]-l[1]+l[2]['duration'])
                i += 1
            res.append(l)
            remaining -= (l[0]-l[1]+l[2]['duration'])
            tmp_loops.remove(l)
        order = np.argsort([l[0] for l in res]).tolist()
        res =  [res[i] for i in order]
        
    else:
        return [(first_node, last_node)]
        
    def dist(node1, node2): return 0 # not sure why, but it works
    start = tuples(nx.astar_path(graph, first_node, res[0][0], dist))
    end = tuples(nx.astar_path(graph, res[-1][1], last_node, dist))
    
    return start + res + end

def make_jumps(path, track):
    actions = []
    source = path[0][0]
    #pb = Playback(track, 0, 10)
    for p in path:
        try:
            if p[2]['target']-p[2]['source'] == 1: 
                raise
            target = p[0]
            if 0 < target-source:
                actions.append(Playback(track, source, target-source))
            actions.append(Jump(track, p[0], p[1], p[2]['duration']))
            source = p[1]
        except:
            target = p[1]
    if 0 < target-source:
        actions.append(Playback(track, source, target-source))
    return actions

def terminate(dur_intro, middle, dur_outro, duration, lgh):
    # merge intro
    if isinstance(middle[0], Playback):
        middle[0].start = 0
        middle[0].duration += dur_intro
        start = []
    else:
        start = [Playback(middle[0].track, 0, dur_intro)]
    # merge outro
    if isinstance(middle[-1], Playback):
        middle[-1].duration += dur_outro
        end = []
    else:
        end = [Playback(middle[-1].track, middle[-1].start + middle[-1].duration, dur_outro)]
    # combine
    actions = start + middle + end
    if lgh == False:
        return actions
    excess = sum(inst.duration for inst in actions)-duration
    if excess == 0:
        return actions
    # trim the end with fadeout
    if actions[-1].duration <= FADE_OUT+excess:
        start = actions[-1].start
        dur = FADE_OUT
        actions.remove(actions[-1])
    else:
        actions[-1].duration -= FADE_OUT+excess
        start = actions[-1].start+actions[-1].duration
        dur = FADE_OUT
    actions.append(Fadeout(middle[0].track, start, dur))
    return actions

def do_work(track, options):
    
    dur = float(options.duration)
    mlp = int(options.minimum)
    lgh = bool(options.length)
    inf = bool(options.infinite)
    pkl = bool(options.pickle)
    gml = bool(options.graph)
    plt = bool(options.plot)
    fce = bool(options.force)
    sho = bool(options.shortest)
    lon = bool(options.longest)
    vbs = bool(options.verbose)
    
    mp3 = track.filename
    try:
        if fce == True:
            raise
        graph = read_graph(mp3+".graph.gpkl")
    except:
        # compute resampled and normalized matrix
        timbre = resample_features(track, rate=RATE, feature='timbre')
        timbre['matrix'] = timbre_whiten(timbre['matrix'])
        pitch = resample_features(track, rate=RATE, feature='pitches')
        
        # pick a tradeoff between speed and memory size
        if rows(timbre['matrix']) < MAX_SIZE:
            # faster but memory hungry. For euclidean distances only.
            t_paths = get_paths(timbre['matrix'])
            p_paths = get_paths(pitch['matrix'])
        else:
            # slower but memory efficient. Any distance possible.
            t_paths = get_paths_slow(timbre['matrix'])
            p_paths = get_paths_slow(pitch['matrix'])
            
        # intersection of top timbre and pitch results
        paths = path_intersect(t_paths, p_paths)
        # TEMPORARY -- check that the data looks good
        if vbs == True:
            print_screen(paths)
        # make graph
        markers = getattr(track.analysis, timbre['rate'])[timbre['index']:timbre['index']+len(paths)]
        graph = make_graph(paths, markers)
        
    # remove smaller loops for quality results
    if 0 < mlp:
        remove_short_loops(graph, mlp)
    # plot graph
    if plt == True:
        save_plot(graph, mp3+".graph.png")
    # save graph
    if pkl == True:
        save_graph(graph, mp3+".graph.gpkl")
    if gml == True:
        save_graph(graph, mp3+".graph.gml")
    # single loops
    if sho == True:
        return one_loop(graph, track, mode='shortest')
    if lon == True:
        return one_loop(graph, track, mode='longest')
    # other infinite loops
    if inf == True:
        if vbs == True:
            print "\nInput Duration:", track.analysis.duration
        # get the optimal path for a given duration
        return infinite(graph, track, dur)
        
    dur_intro = min(graph.nodes())
    dur_outro = track.analysis.duration - max(graph.nodes())
    
    if vbs == True:
        print "Input Duration:", track.analysis.duration
    # get the optimal path for a given duration
    path = compute_path(graph, max(dur-dur_intro-dur_outro, 0))
    # build actions
    middle = make_jumps(path, track)
    # complete list of actions
    actions = terminate(dur_intro, middle, dur_outro, dur, lgh)
    
    return actions

def main():
    usage = "usage: %s [options] <one_single_mp3>" % sys.argv[0]
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--duration", default=DEF_DUR, help="target duration (argument in seconds) default=600")
    parser.add_option("-m", "--minimum", default=MIN_JUMP, help="minimal loop size (in beats) default=8")
    parser.add_option("-i", "--infinite", action="store_true", help="generate an infinite loop (outputs a wav file)")
    parser.add_option("-l", "--length", action="store_true", help="length must be accurate")
    parser.add_option("-k", "--pickle", action="store_true", help="output graph as a pickle object")
    parser.add_option("-g", "--graph", action="store_true", help="output graph as a gml text file")
    parser.add_option("-p", "--plot", action="store_true", help="output graph as png image")
    parser.add_option("-f", "--force", action="store_true", help="force (re)computing the graph")
    parser.add_option("-S", "--shortest", action="store_true", help="output the shortest loop")
    parser.add_option("-L", "--longest", action="store_true", help="output the longest loop")
    parser.add_option("-v", "--verbose", action="store_true", help="show results on screen")
    
    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.print_help()
        return -1
    
    verbose = options.verbose
    track = LocalAudioFile(args[0], verbose=verbose)
    
    # this is where the work takes place
    actions = do_work(track, options)
    
    if verbose:
        display_actions(actions)
        print "Output Duration = %.3f sec" % sum(act.duration for act in actions)
    
    # Send to renderer
    name = os.path.splitext(os.path.basename(args[0]))
    
    # Output wav for loops in order to remain sample accurate
    if bool(options.infinite) == True: 
        name = name[0]+'_'+str(int(options.duration))+'_loop.wav'
    elif bool(options.shortest) == True: 
        name = name[0]+'_'+str(int(sum(act.duration for act in actions)))+'_shortest.wav'
    elif bool(options.longest) == True: 
        name = name[0]+'_'+str(int(sum(act.duration for act in actions)))+'_longest.wav'
    else: 
        name = name[0]+'_'+str(int(options.duration))+'.mp3'
    
    if options.verbose:
        print "Rendering..."
    render(actions, name, verbose=verbose)
    return 1


if __name__ == "__main__":
    main()
