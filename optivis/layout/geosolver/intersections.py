# -*- coding: utf-8 -*-

"""Intersection classes for performing geometric transformations on
configurations"""

from __future__ import unicode_literals, division

import logging
import math

import optivis.layout.geosolver.vector as vector
from optivis.layout.geosolver.matfunc import Mat, Vec
from optivis.layout.geosolver.tolerance import *

def sign(x):
	"""Returns 1 if x>0, return -1 if x<=0"""
	if x > 0:
		return 1
	else:
		return -1

def cc_int(p1, r1, p2, r2):
	"""
	Intersect circle (p1,r1) circle (p2,r2)
	where p1 and p2 are 2-vectors and r1 and r2 are scalars
	Returns a list of zero, one or two solution points.
	"""
	d = vector.norm(p2-p1)
	if not tol_gt(d, 0):
		return []
	u = ((r1*r1 - r2*r2)/d + d)/2
	if tol_lt(r1*r1, u*u):
		return []
        elif r1*r1 < u*u:
            v = 0.0
        else:
            v = math.sqrt(r1*r1 - u*u)
	s = (p2-p1) * u / d
	if tol_eq(vector.norm(s),0):
	        p3a = p1+vector.vector([p2[1]-p1[1],p1[0]-p2[0]])*r1/d
	        if tol_eq(r1/d,0):
                    return [p3a]
                else:
                    p3b = p1+vector.vector([p1[1]-p2[1],p2[0]-p1[0]])*r1/d
                    return [p3a,p3b]
	else:
	        p3a = p1 + s + vector.vector([s[1], -s[0]]) * v / vector.norm(s)
                if tol_eq(v / vector.norm(s),0):
                    return [p3a]
                else:
                    p3b = p1 + s + vector.vector([-s[1], s[0]]) * v / vector.norm(s)
    	            return [p3a,p3b]

def cl_int(p1,r,p2,v):
	"""
	Intersect a circle (p1,r) with line (p2,v)
	where p1, p2 and v are 2-vectors, r is a scalar
	Returns a list of zero, one or two solution points
	"""
	p = p2 - p1
	d2 = v[0]*v[0] + v[1]*v[1]
	D = p[0]*v[1] - v[0]*p[1]
	E = r*r*d2 - D*D
	if tol_gt(d2, 0) and tol_gt(E, 0):
		sE = math.sqrt(E)
		x1 = p1[0] + (D * v[1] + sign(v[1])*v[0]*sE) / d2
		x2 = p1[0] + (D * v[1] - sign(v[1])*v[0]*sE) / d2
		y1 = p1[1] + (-D * v[0] + abs(v[1])*sE) / d2
		y2 = p1[1] + (-D * v[0] - abs(v[1])*sE) / d2
		return [vector.vector([x1,y1]), vector.vector([x2,y2])]
	elif tol_eq(E, 0):
		x1 = p1[0] + D * v[1] / d2
		y1 = p1[1] + -D * v[0] / d2
		# return [vector.vector([x1,y1]), vector.vector([x1,y1])]
		return [vector.vector([x1,y1])]
	else:
		return []

def cr_int(p1,r,p2,v):
	"""
	Intersect a circle (p1,r) with ray (p2,v) (a half-line)
	where p1, p2 and v are 2-vectors, r is a scalar
	Returns a list of zero, one or two solutions.
	"""
        sols = []
	all = cl_int(p1,r,p2,v)
        for s in all:
	    if tol_gte(vector.dot(s-p2,v), 0):          # gt -> gte 30/6/2006
                sols.append(s)
	return sols

def ll_int(p1, v1, p2, v2):
	"""Intersect line though p1 direction v1 with line through p2 direction v2.
	   Returns a list of zero or one solutions
	"""
	logging.getLogger("intersections").debug("ll_int "+str(p1)+str(v1)+str(p2)+str(v2),"intersections")
	if tol_eq((v1[0]*v2[1])-(v1[1]*v2[0]),0):
		return []
	elif not tol_eq(v2[1],0.0):
		d = p2-p1
		r2 = -v2[0]/v2[1]
		f = v1[0] + v1[1]*r2
		t1 = (d[0] + d[1]*r2) / f
	else:
		d = p2-p1
		t1 = d[1]/v1[1]
	return [p1 + v1*t1]

def lr_int(p1, v1, p2, v2):
	"""Intersect line though p1 direction v1 with ray through p2 direction v2.
	   Returns a list of zero or one solutions
	"""
	logging.getLogger("intersections").debug("lr_int "+str(p1)+str(v1)+str(p2)+str(v2),"intersections")
	s = ll_int(p1,v1,p2,v2)
	if len(s) > 0 and tol_gte(vector.dot(s[0]-p2,v2), 0):
		return s
	else:
		return []

def rr_int(p1, v1, p2, v2):
	"""Intersect ray though p1 direction v1 with ray through p2 direction v2.
	   Returns a list of zero or one solutions
	"""
	logging.getLogger("intersections").debug("rr_int "+str(p1)+str(v1)+str(p2)+str(v2),"intersections")
	s = ll_int(p1,v1,p2,v2)
	if len(s) > 0 and tol_gte(vector.dot(s[0]-p2,v2), 0) and tol_gte(vector.dot(s[0]-p1,v1),0):
		return s
	else:
		return []

def angle_3p(p1, p2, p3):
    """Returns the angle, in radians, rotating vector p2p1 to vector p2p3.
       arg keywords:
          p1 - a vector
          p2 - a vector
          p3 - a vector
       returns: a number
       In 2D, the angle is a signed angle, range [-pi,pi], corresponding
       to a clockwise rotation. If p1-p2-p3 is clockwise, then angle > 0.
       In 3D, the angle is unsigned, range [0,pi]
    """
    d21 = vector.norm(p2-p1)
    d23 = vector.norm(p3-p2)
    if tol_eq(d21,0) or tol_eq(d23,0):
        return None         # degenerate angle
    v21 = (p1-p2) / d21
    v23 = (p3-p2) / d23
    t = vector.dot(v21,v23) # / (d21 * d23)
    if t > 1.0:             # check for floating point error
        t = 1.0
    elif t < -1.0:
        t = -1.0
    angle = math.acos(t)
    if len(p1) == 2:        # 2D case
        if is_counterclockwise(p1,p2,p3):
            angle = -angle
    return angle

def distance_2p(p1, p2):
    """Returns the euclidean distance between two points
       arg keywords:
          p1 - a vector
          p2 - a vector
       returns: a number
    """
    return vector.norm(p2 - p1)

def is_clockwise(p1,p2,p3):
    """ returns True iff triangle p1,p2,p3 is clockwise oriented"""
    u = p2 - p1
    v = p3 - p2;
    perp_u = vector.vector([-u[1], u[0]])
    return tol_lt(vector.dot(perp_u,v),0)

def is_counterclockwise(p1,p2,p3):
    """ returns True iff triangle p1,p2,p3 is counterclockwise oriented"""
    u = p2 - p1
    v = p3 - p2;
    perp_u = vector.vector([-u[1], u[0]])
    return tol_gt(vector.dot(perp_u,v), 0)

def is_flat(p1,p2,p3):
    """ returns True iff triangle p1,p2,p3 is flat (neither clockwise of counterclockwise oriented)"""
    u = p2 - p1
    v = p3 - p2;
    perp_u = vector.vector([-u[1], u[0]])
    return tol_eq(vector.dot(perp_u,v), 0)

def is_acute(p1,p2,p3):
    """returns True iff angle p1,p2,p3 is acute, i.e. less than pi/2"""
    angle = angle_3p(p1, p2, p3)
    if angle != None:
        return tol_lt(abs(angle), math.pi / 2)
    else:
        return False

def is_obtuse(p1,p2,p3):
    """returns True iff angle p1,p2,p3 is obtuse, i.e. greater than pi/2"""
    angle = angle_3p(p1, p2, p3)
    if angle != None:
        return tol_gt(abs(angle), math.pi / 2)
    else:
        return False

def is_left_handed(p1,p2,p3,p4):
    """return True if tetrahedron p1 p2 p3 p4 is left handed"""
    u = p2-p1
    v = p3-p1
    uv = vector.cross(u,v)
    w = p4-p1
    return vector.dot(uv,w) < 0

def is_right_handed(p1,p2,p3,p4):
    """return True if tetrahedron p1 p2 p3 p4 is right handed"""
    u = p2-p1
    v = p3-p1
    uv = vector.cross(u,v)
    w = p4-p1
    return vector.dot(uv,w) > 0

def make_hcs_2d (a, b):
    """build a 2D homogeneus coordiate system from two vectors"""
    u = b-a
    if tol_eq(vector.norm(u), 0.0):     # 2006/6/30
        return None
    else:
        u = u / vector.norm(u)
    v = vector.vector([-u[1], u[0]])
    hcs = Mat([ [u[0],v[0],a[0]] , [u[1],v[1],a[1]] , [0.0, 0.0, 1.0] ] )
    return hcs

def make_hcs_2d_scaled (a, b):
    """build a 2D homogeneus coordiate system from two vectors, but scale with distance between input point"""
    u = b-a
    if tol_eq(vector.norm(u), 0.0):     # 2006/6/30
        return None
    #else:
    #    u = u / vector.norm(u)
    v = vector.vector([-u[1], u[0]])
    hcs = Mat([ [u[0],v[0],a[0]] , [u[1],v[1],a[1]] , [0.0, 0.0, 1.0] ] )
    return hcs

def cs_transform_matrix(from_cs, to_cs):
    """returns a transform matrix from from_cs to to_cs"""
    transform = to_cs.mmul(from_cs.inverse())
    return transform

def translate_2D(dx,dy):
	mat = Mat([
		[1.0, 0.0, dx] ,
		[0.0, 1.0, dy] ,
		[0.0, 0.0, 1.0] ] )
	return mat

def rotate_2D(angle):
	mat = Mat([
		[math.sin[angle],math.cos[angle],0.0] ,
		[math.cos[angle],-math.sin[angle],0.0] ,
		[0.0, 0.0, 1.0] ] )
	return mat

def transform_point(point, transform):
    """transform a point from from_cs to to_cs"""
    hpoint = Vec(point)
    hpoint.append(1.0)
    hres = transform.mmul(hpoint)
    res = vector.vector(hres[1:-1]) / hres[-1]
    return res

# -------------------------test code -----------------

def test_ll_int():
	"""test random line-line intersection. returns True iff succesful"""
	# generate three points A,B,C an two lines AC, BC.
	# then calculate the intersection of the two lines
	# and check that it equals C
	p_a = vector.randvec(2, 0.0, 10.0, 1.0)
	p_b = vector.randvec(2, 0.0, 10.0, 1.0)
	p_c = vector.randvec(2, 0.0, 10.0, 1.0)
	# print p_a, p_b, p_c
	if tol_eq(vector.norm(p_c - p_a),0) or tol_eq(vector.norm(p_c - p_b),0):
		return True # ignore this case
	v_ac = (p_c - p_a) / vector.norm(p_c - p_a)
	v_bc = (p_c - p_b) / vector.norm(p_c - p_b)
	s = ll_int(p_a, v_ac, p_b, v_bc)
	if tol_eq(math.fabs(vector.dot(v_ac, v_bc)),1.0):
		return len(s) == 0
	else:
		if len(s) > 0:
			p_s = s[0]
			return tol_eq(p_s[0],p_c[0]) and tol_eq(p_s[1],p_c[1])
		else:
			return False

def test_rr_int():
	"""test random ray-ray intersection. returns True iff succesful"""
	# generate tree points A,B,C an two rays AC, BC.
	# then calculate the intersection of the two rays
	# and check that it equals C
	p_a = vector.randvec(2, 0.0, 10.0,1.0)
	p_b = vector.randvec(2, 0.0, 10.0,1.0)
	p_c = vector.randvec(2, 0.0, 10.0,1.0)
	# print p_a, p_b, p_c
	if tol_eq(vector.norm(p_c - p_a),0) or tol_eq(vector.norm(p_c - p_b),0):
		return True # ignore this case
	v_ac = (p_c - p_a) / vector.norm(p_c - p_a)
	v_bc = (p_c - p_b) / vector.norm(p_c - p_b)
	s = rr_int(p_a, v_ac, p_b, v_bc)
	if tol_eq(math.fabs(vector.dot(v_ac, v_bc)),1.0):
		return len(s) == 0
	else:
		if len(s) > 0:
			p_s = s[0]
			return tol_eq(p_s[0],p_c[0]) and tol_eq(p_s[1],p_c[1])
		else:
			return False

def test1():
	sat = True
	for i in range(0,100):
		sat = sat and test_ll_int()
		if not sat:
			print "ll_int() failed"
			return
	if sat:
		print "ll_int() passed"
	else:
		print "ll_int() failed"

	sat = True
	for i in range(0,100):
		sat = sat and test_rr_int()
		if not sat:
			print "rr_int() failed"
			return

	if sat:
		print "rr_int() passed"
	else:
		print "rr_int() failed"

	print "2D angles"
	for i in xrange(9):
		a = i * 45 * math.pi / 180
		p1 = vector.vector([1.0,0.0])
		p2 = vector.vector([0.0,0.0])
		p3 = vector.vector([math.cos(a),math.sin(a)])
		print p3, angle_3p(p1,p2,p3) * 180 / math.pi, "flip", angle_3p(p3,p2,p1) * 180 / math.pi

if __name__ == '__main__': test1()
