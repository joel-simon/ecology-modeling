import unittest
from main import randomly_distribute

class TestRandomlyDistribute(unittest.TestCase):
    def test_random_distribute(self):
        tokens = 10
        for i in range(10):
            groups = 5 + i
            result = randomly_distribute(tokens, groups)
            self.assertEqual(sum(result), tokens)
            self.assertEqual(len(result), groups)

if __name__ == '__main__':
    unittest.main()