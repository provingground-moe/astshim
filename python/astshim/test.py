import unittest

import numpy as np
from numpy.testing import assert_allclose

from .channel import Channel
from .polyMap import PolyMap
from .xmlChan import XmlChan
from .stream import StringStream


class ObjectTestCase(unittest.TestCase):

    """Base class for unit tests of objects
    """

    def checkCopy(self, obj):
        """Check that an astshim object can be deep-copied
        """
        nobj = obj.getNObject()
        nref = obj.getRefCount()
        cp = obj.copy()
        self.assertEqual(type(obj), type(cp))
        self.assertEqual(str(obj), str(cp))
        self.assertEqual(repr(obj), repr(cp))
        self.assertEqual(obj.getNObject(), nobj + 1)
        # Object.copy makes a new pointer instead of copying the old one,
        # so the reference count of the old one does not increase
        self.assertEqual(obj.getRefCount(), nref)
        self.assertFalse(obj.same(cp))
        self.assertEqual(cp.getNObject(), nobj + 1)
        self.assertEqual(cp.getRefCount(), 1)

    def checkPersistence(self, obj):
        """Check that an astshim object can be persisted and unpersisted
        """
        # round trip with a Channel
        ss1 = StringStream()
        chan1 = Channel(ss1)
        chan1.write(obj)
        ss1.sinkToSource()
        obj_copy1 = chan1.read()
        self.assertEqual(obj.getClassName(), obj_copy1.getClassName())
        self.assertEqual(obj.show(), obj_copy1.show())
        self.assertEqual(str(obj), str(obj_copy1))
        self.assertEqual(repr(obj), repr(obj_copy1))

        # round trip with an XmlChan
        ss2 = StringStream()
        chan2 = XmlChan(ss2)
        chan2.write(obj)
        ss2.sinkToSource()
        obj_copy2 = chan2.read()
        self.assertEqual(obj.getClassName(), obj_copy2.getClassName())
        self.assertEqual(obj.show(), obj_copy2.show())
        self.assertEqual(str(obj), str(obj_copy2))
        self.assertEqual(repr(obj), repr(obj_copy2))


class MappingTestCase(ObjectTestCase):

    """Base class for unit tests of mappings
    """

    def checkRoundTrip(self, amap, poslist, rtol=1e-05, atol=1e-08):
        """Check that a mapping's reverse transform is the opposite of forward

        amap is the mapping to test
        poslist is a list of input position for a forward transform;
            a numpy array with shape [nin, num points]
            or collection that can be cast to same
        rtol is the relative tolerance for numpy.testing.assert_allclose
        atol is the absolute tolerance for numpy.testing.assert_allclose
        """
        poslist = np.array(poslist, dtype=float)
        if len(poslist.shape) == 1:
            # supplied data was a single list of points
            poslist.shape = (1, len(poslist))
        # forward with tranForward, inverse with tranInverse
        to_poslist = amap.tranForward(poslist)
        rt_poslist = amap.tranInverse(to_poslist)
        assert_allclose(poslist, rt_poslist, rtol=rtol, atol=atol)

        # forward with tranForward, inverse with getInverse().tranForward
        amapinv = amap.getInverse()
        rt2_poslist = amapinv.tranForward(to_poslist)
        assert_allclose(poslist, rt2_poslist, rtol=rtol, atol=atol)

        # forward and inverse with a compound map of amap.getInverse().of(amap)
        acmp = amapinv.of(amap)
        assert_allclose(poslist, acmp.tranForward(poslist), rtol=rtol, atol=atol)

        # test vector versions of forward and inverse
        posvec = list(poslist.flat)
        to_posvec = amap.tranForward(posvec)
        # cast to_poslist to np.array because if poslist has 1 axis then
        # a list is returned, which has no `flat` attribute
        assert_allclose(to_posvec, list(to_poslist.flat), rtol=rtol, atol=atol)

        rt_posvec = amap.tranInverse(to_posvec)
        assert_allclose(posvec, rt_posvec, rtol=rtol, atol=atol)

    def checkBasicSimplify(self, amap):
        """Check basic simplfication for a reversible mapping

        Check the following:
        - A compound mapping of a amap and its inverse simplifies to a unit amap
        - A compound mapping of a amap and a unit amap simplifies to the original amap
        """
        amapinv = amap.getInverse()
        cmp1 = amapinv.of(amap)
        unit1 = cmp1.simplify()
        self.assertEqual(unit1.getClassName(), "UnitMap")
        self.assertEqual(amap.getNIn(), cmp1.getNIn())
        self.assertEqual(amap.getNIn(), cmp1.getNOut())
        self.assertEqual(cmp1.getNIn(), unit1.getNIn())
        self.assertEqual(cmp1.getNOut(), unit1.getNOut())

        cmp2 = amap.of(amapinv)
        unit2 = cmp2.simplify()
        self.assertEqual(unit2.getClassName(), "UnitMap")
        self.assertEqual(amapinv.getNIn(), cmp2.getNIn())
        self.assertEqual(amapinv.getNIn(), cmp2.getNOut())
        self.assertEqual(cmp2.getNIn(), unit2.getNIn())
        self.assertEqual(cmp2.getNOut(), unit2.getNOut())

        for ma, mb, desmap3 in (
            (unit1, amap, amap),
            (amap, unit2, amap),
            (unit2, amapinv, amapinv),
            (amapinv, unit1, amapinv),
        ):
            cmp3 = mb.of(ma)
            cmp3simp = cmp3.simplify()
            self.assertEqual(cmp3simp.getClassName(), amap.simplify().getClassName())
            self.assertEqual(ma.getNIn(), cmp3.getNIn())
            self.assertEqual(mb.getNOut(), cmp3.getNOut())
            self.assertEqual(cmp3.getNIn(), cmp3simp.getNIn())
            self.assertEqual(cmp3.getNOut(), cmp3simp.getNOut())


def makePolyMapCoeffs(nIn, nOut):
    """Make an array of coefficients for astshim.PolyMap for the following equation:

    fj(x) = C0j x0^2 + C1j x1^2 + C2j x2^2 + ... + CNj xN^2
    where:
    * i ranges from 0 to N=nIn-1
    * j ranges from 0 to nOut-1,
    * Cij = 0.001 (i+j+1)
    """
    baseCoeff = 0.001
    forwardCoeffs = []
    for out_ind in range(nOut):
        coeffOffset = baseCoeff * out_ind
        for in_ind in range(nIn):
            coeff = baseCoeff * (in_ind + 1) + coeffOffset
            coeffArr = [coeff, out_ind + 1] + [2 if i == in_ind else 0 for i in range(nIn)]
            forwardCoeffs.append(coeffArr)
    return np.array(forwardCoeffs, dtype=float)


def makeTwoWayPolyMap(nIn, nOut):
    """Make an astShim.PolyMap suitable for testing

    The forward transform is as follows:
    fj(x) = C0j x0^2 + C1j x1^2 + C2j x2^2 + ... + CNj xN^2 where Cij = 0.001 (i+j+1)

    The reverse transform is the same equation with i and j reversed
    thus it is NOT the inverse of the forward direction,
    but is something that can be easily evaluated.

    The equation is chosen for the following reasons:
    - It is well defined for any positive value of nIn, nOut
    - It stays small for small x, to avoid wraparound of angles for SpherePoint endpoints
    """
    forwardCoeffs = makePolyMapCoeffs(nIn, nOut)
    reverseCoeffs = makePolyMapCoeffs(nOut, nIn)
    polyMap = PolyMap(forwardCoeffs, reverseCoeffs)
    assert polyMap.getNIn() == nIn
    assert polyMap.getNOut() == nOut
    assert polyMap.hasForward()
    assert polyMap.hasInverse()
    return polyMap


def makeForwardPolyMap(nIn, nOut):
    """Make an astShim.PolyMap suitable for testing

    The forward transform is the same as for `makeTwoWayPolyMap`.
    This map does not have a reverse transform.

    The equation is chosen for the following reasons:
    - It is well defined for any positive value of nIn, nOut
    - It stays small for small x, to avoid wraparound of angles for SpherePoint endpoints
    """
    forwardCoeffs = makePolyMapCoeffs(nIn, nOut)
    polyMap = PolyMap(forwardCoeffs, nOut, "IterInverse=0")
    assert polyMap.getNIn() == nIn
    assert polyMap.getNOut() == nOut
    assert polyMap.hasForward()
    assert not polyMap.hasInverse()
    return polyMap
