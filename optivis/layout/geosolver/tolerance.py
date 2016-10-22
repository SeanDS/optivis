# -*- coding: utf-8 -*-

"""Basic toleranced comparison functions. Intended for use on double values, and
extention to positive and negative infinity, represented by PosInf and NegInf
respectively. Note that tol_eq(PosInf, PosInf) == True. This is mathematically
acceptable if we consider PosInf as a single value, greater than any other value
that can be represented by a computer. Same for NegInf. All toleranced
comparison function accept a tolerance value. When it is ommitted or when
"Default" is specified, a default value is used. This default value is stored in
the variable: default_tol."""

from __future__ import unicode_literals, division

class positiveinfinity:
	"""Positive Infinity, a value greater then any other value except itself.
   	Only one instance of this class is needed, instantiated in this module as
	PosInf."""
	def __cmp__(self, other):
		if other.__class__ == self.__class__:
			return 0
		else:
			return 1

        def __hash__(self):
            return 0

	def __repr__(self):
		return str(__name__)+".PosInf"

	def __str__(self):
		return "PosInf"
# end class positiveinfinity

class negativeinfinity:
	"""Negative Infinity, a value greater then any other value except itself.
   	Only one instance of this class is needed, instantiated in this module as
	NegInf."""
	def __cmp__(self, other):
		if other.__class__ == self.__class__:
			return 0
		else:
			return -1

        def __hash__(self):
            return 1

	def __repr__(self):
		return str(__name__)+".NegInf"

	def __str__(self):
		return "NegInf"
# end class positiveinfinity


#Positive infinity. This variable is an instance of positiveinfinity.
#No other instances need to be created.
PosInf = positiveinfinity()

#Negative infinity. This variable is an instance of negativeinfinity.
#No other instances need to be created.
NegInf = negativeinfinity()

# The default tolerance, used when no tolerance argument is given
# to the comparion functions, or when "Default" is passed.
default_tol = 1e-6

def tol_lt(a,b,tol="Default"):
	"""Tolerant less-than: return b-a>tol"""
	if tol=="Default":
		tol = default_tol
	if a == NegInf:
		return b != NegInf
	elif a == PosInf:
		return False
	elif b == PosInf:
		return a != PosInf
	elif b == NegInf:
		return False
	else:
		return b-a>tol

def tol_gt(a,b,tol="Default"):
	"""Tolerant greater-than: return a-b>tol"""
	if tol=="Default":
		tol = default_tol
	if a == NegInf:
		return False
	elif a == PosInf:
		return b != PosInf
	elif b == NegInf:
		return a != NegInf
	elif b == PosInf:
		return False
	else:
		return a-b>tol

def tol_eq(a,b,tol="Default"):
	"""Tolerant equal: return abs(a-b)<=tol"""
	if tol=="Default":
		tol = default_tol
	if a == PosInf:
		return b == PosInf
	elif a == NegInf:
		return b == NegInf
	elif b == PosInf:
		return a == PosInf
	elif b == NegInf:
		return a == NegInf
	else:
		return abs(a-b)<=tol

def tol_lte(a,b,tol="Default"):
	"""Tolerant less-than-or-equal: return not tol_gt(a,b,tol)"""
	return not tol_gt(a,b,tol)

def tol_gte(a,b,tol="Default"):
	"""Tolerant greater-than-or-equal: return not tol_lt(a,b,tol)"""
	return not tol_lt(a,b,tol)


def tol_compare(a,b,tol="Default"):
	if tol_lt(a,b,tol):
		return "<";
	elif tol_eq(a,b,tol):
		return "=";
	elif tol_gt(a,b,tol):
		return ">";
        else:
            raise StandardError, "tolerance interval error"

def tol_round(val,tol="Default"):
    if tol=="Default":
        tol = default_tol
    return val - (val % tol)

def test():
	tol = 0.005;
	print "tolerance =", tol;
	values = [NegInf, -1.001, -1.0, -0.999, 0.0, 0.01, 0.02, PosInf];

	#print header
	head = ""
	for v in values:
		head += '\t';
		head += str(v);
	print head
	# rows rows
	for v1 in values:
		row = str(v1) + '\t'
		for v2 in values:
			row += tol_compare(v1,v2,tol) + '\t';
		print row

if __name__ == "__main__":
	test()
