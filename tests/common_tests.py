#!/usr/bin/python
import sys
sys.path.append("../")
import unittest
from common import encodeSubjectPictureName, decodeSubjectPictureName


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


if __name__ == '__main__':
    unittest.main()