import unittest
from signup.signup.handler import Credentials


class TestCredentials(unittest.TestCase):
    def test_correct_password(self):
        correct_password = '12Abcde!'

        output_value = Credentials.password_minimal_length(
            value=correct_password
        )

        self.assertEqual(output_value, correct_password)

    def test_minimal_length_password(self):
        incorrect_password = '12Abce!'

        self.assertRaises(
            ValueError,
            Credentials.password_minimal_length,
            incorrect_password
        )

    def test_maximal_length_password(self):
        incorrect_password = '12Abcde!' * 4 + '1'

        self.assertRaises(
            ValueError,
            Credentials.password_minimal_length,
            incorrect_password
        )

    def test_special_character_password(self):
        incorrect_password = '12Abcde'

        self.assertRaises(
            ValueError,
            Credentials.password_minimal_length,
            incorrect_password
        )

    def test_lower_case_password(self):
        incorrect_password = '12abcde!'

        self.assertRaises(
            ValueError,
            Credentials.password_minimal_length,
            incorrect_password
        )

    def test_upper_case_password(self):
        incorrect_password = '12ABCDE!'

        self.assertRaises(
            ValueError,
            Credentials.password_minimal_length,
            incorrect_password
        )
