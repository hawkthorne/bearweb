from django.test import TestCase

from games import base58


class Base58Tests(TestCase):

    def test_alphabet_length(self):
        self.assertEqual(58, len(base58.alphabet))

    def test_encode_10002343_returns_Tgmc(self):
        result = base58.encode('10002343')
        self.assertEqual('9EBsk7sUpHY', result)

    def test_encode_1000_returns_if(self):
        result = base58.encode('1000')
        self.assertEqual('2FvabH', result)
