from django.test import TestCase

# Create your tests here.
from .algorithm.algorithm import allocate
from .algorithm.fake_data import example_1, example_2, example_3


class AlgorithmTests(TestCase):
    def setUp(self):
        self.example_1 = example_1()
        self.example_2 = example_2()
        self.example_3 = example_3()

    def test_hospital_can_send_multiple_times(self):
        output = [(10, 200, 1), (10, 100, 2)]
        self.assertEqual(allocate(self.example_1['orders'],
            self.example_1['htov'], self.example_1['htog']), output)

    def test_hopitals_only_send_within_group(self):
        output = [(10, 200, 1), (11, 500, 2)]
        self.assertEqual(allocate(
        self.example_2['orders'], self.example_2['htov'], self.example_2['htog']
        ), output)

    def test_hospitals_can_receive_from_two_senders(self):
        output = [(10, 100, 1), (11, 100, 1)]
        self.assertEqual(allocate(
        self.example_3['orders'], self.example_3['htov'], self.example_3['htog']
        ), output)
