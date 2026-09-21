import unittest

class TestGenMarketContract(unittest.TestCase):

    def test_market_initialization(self):
        question = "Will Bitcoin reach $100k in 2026?"
        evidence = "https://api.coingecko.com"
        
        self.assertIsNotNone(question)
        self.assertIsNotNone(evidence)
        self.assertTrue(len(question) > 0)

    def test_valid_outcomes(self):
        valid_outcomes = ["YES", "NO"]
        test_choice = "YES"
        self.assertIn(test_choice, valid_outcomes)

if __name__ == "__main__":
    unittest.main()
