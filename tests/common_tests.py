#!/usr/bin/python
import sys
import numpy
import unittest
sys.path.append("../")
from common import encodeSubjectPictureName, decodeSubjectPictureName, scaleCoords


class TestSubjectPictureNameEncoder(unittest.TestCase):

    def test_decode_fail_none(self):
        name, email = decodeSubjectPictureName(None)
        self.assertEqual(name, '')
        self.assertEqual(email, '')

    def test_decode_fail_empty(self):
        name, email = decodeSubjectPictureName('')
        self.assertEqual(name, '')
        self.assertEqual(email, '')

    def test_decode_fail_incomplete(self):
        name, email = decodeSubjectPictureName('asdasd_asd')
        self.assertEqual(name, 'asdasd asd')
        self.assertEqual(email, '')

    def test_decode(self):
        name, email = decodeSubjectPictureName('juan_gabriel_arias-juangarias@gmail.com')
        self.assertEqual(name, 'juan gabriel arias')
        self.assertEqual(email, 'juangarias@gmail.com')

    def test_encode(self):
        x = encodeSubjectPictureName('Juan Gabriel Arias', 'juangarias@gmail.com')
        self.assertEqual(x, 'Juan_Gabriel_Arias-juangarias@gmail.com')


class TestScaleCoords(unittest.TestCase):

    def test_scale_dummy(self):
        source = (0, 0, 10, 10)
        size = (100, 100, 3)
        image = numpy.empty(size)
        result = scaleCoords(source, image, None)
        expected = (0, 0, 10, 10)
        self.assertEquals(result, expected)

    def test_scale_zero(self):
        source = (0, 0, 10, 10)
        size = (100, 100, 3)
        image = numpy.empty(size)
        result = scaleCoords(source, image, 1000)
        expected = (0, 0, 100, 100)
        self.assertEquals(result, expected)

    def test_scale_middle(self):
        source = (5, 5, 10, 10)
        size = (100, 100, 3)
        image = numpy.empty(size)
        result = scaleCoords(source, image, 1000)
        expected = (50, 50, 100, 100)
        self.assertEquals(result, expected)

    def test_scale_raises_error(self):
        with self.assertRaises(ValueError):
            scaleCoords((10, 10, 10, 10), None, 400)


if __name__ == '__main__':
    unittest.main()
