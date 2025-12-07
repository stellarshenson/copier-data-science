"""
Example test module demonstrating unittest best practices.

This module shows how to structure tests with:
- setUp and tearDown methods for test lifecycle
- Docstrings for test documentation
- Multiple test methods in a TestCase
"""
import unittest


class TestSampleData(unittest.TestCase):
    """Test case demonstrating unittest patterns.

    Each test method should start with 'test_' and test
    a single piece of functionality.
    """

    def setUp(self):
        """Set up test fixtures before each test method.

        This method runs before every test in the class.
        Use it for common setup like creating test data
        or initializing resources.
        """
        self.sample_data = {"key": "value", "count": 42}

    def tearDown(self):
        """Clean up after each test method.

        This method runs after every test, even if the test fails.
        Use it for cleanup like closing files or connections.
        """
        self.sample_data = None

    def test_sample_data_has_key(self):
        """Test that sample data contains expected key."""
        self.assertIn("key", self.sample_data)

    def test_sample_data_has_count(self):
        """Test that sample data contains count field."""
        self.assertIn("count", self.sample_data)

    def test_count_is_integer(self):
        """Test that count value is an integer."""
        self.assertIsInstance(self.sample_data["count"], int)

    def test_count_value(self):
        """Test that count has expected value."""
        self.assertEqual(self.sample_data["count"], 42)


if __name__ == '__main__':
    unittest.main()
