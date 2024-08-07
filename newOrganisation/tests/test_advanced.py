# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sample.model import Reaction
import hypothesis.extra.ghostwriter as ghostwriter
"""
import sample

import unittest


class AdvancedTestSuite(unittest.TestCase):
    Advanced test cases.

    def test_thoughts(self):
        self.assertIsNone(sample.hmm())
 """

if __name__ == '__main__':
    
    print([[chr(v) for v in range(ord('a'), ord('a') + 26)]])
    """ unittest.main() """
