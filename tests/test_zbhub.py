#! /usr/bin/python
"""
test_zbhub.py

By James Saunders, 2017

Tests PyAlertMe Module.
"""
import sys
sys.path.insert(0, '../')
from pyalertme import *
import unittest
from mock_serial import Serial


class TestZBHub(unittest.TestCase):
    """
    Test PyAlertMe ZBHub Class.
    """
    def setUp(self):
        """
        Create a node object for each test.
        """
        self.maxDiff = None
        self.hub_ser = Serial()
        self.hub_obj = ZBHub(self.hub_ser)
        self.hub_obj.addr_long = b'\x00\x1e\x5e\x09\x02\x14\xc5\xab'
        self.hub_obj.addr_short = b'\x88\xd2'

        self.device_ser = Serial()
        self.device_obj = ZBDevice(self.device_ser)

    def tearDown(self):
        """
        Teardown node object.
        """
        self.hub_obj.halt()
        self.device_obj.halt()

    def test_receive_message(self):
        """
        Test Receive Message.
        """
        # First, lets manually construct a Version message and send it into the Hub.
        message = {
            'profile': b'\xc2\x16',
            'source_addr': b'\x92T',
            'dest_endpoint': b'\x02',
            'rf_data': b'\t\x00\xfeT\x92\x1b\xf7r\x01\x00o\r\x009\x10\x07\x00\x01(\x00\x01\x0bAlertMe.com\tSmartPlug\n2011-07-25',
            'source_endpoint': b'\x02',
            'options': b'\x01',
            'source_addr_long': b'\x00\ro\x00\x01r\xf7\x1b',
            'cluster': b'\x00\xf6',
            'id': 'rx_explicit'
        }
        self.hub_obj.receive_message(message)
        result = self.hub_obj.list_devices()
        expected = {
            '00:0d:6f:00:01:72:f7:1b': {
                'manu_string': 'AlertMe.com',
                'type': 'SmartPlug',
                'hwMajorVersion': 1,
                'hwMinorVersion': 0,
            }
        }
        self.assertEqual(result, expected)

        # Next, lets get the class to generate a Version message and send it into the Hub.
        params = {
            'type': 'Generic',
            'hwMajorVersion': 1,
            'hwMinorVersion': 0,
            'manu_string': 'PyAlertMe',
            'manu_date': '2017-01-01'
        }
        message = self.device_obj.generate_message('version_info_update', params)
        message['id'] = 'rx_explicit'
        message['source_addr'] = b'\x88\xfd'
        message['source_addr_long'] = b'\x00\x0d\x6f\x00\x00\x00\xff\xff'
        message['rf_data'] = message['data']
        self.hub_obj.receive_message(message)
        result = self.hub_obj.list_devices()
        expected = {
            '00:0d:6f:00:01:72:f7:1b': {
                'type': 'SmartPlug',
                'hwMajorVersion': 1,
                'hwMinorVersion': 0,
                'manu_string': 'AlertMe.com'
            },
            '00:0d:6f:00:00:00:ff:ff': {
                'type': 'Generic',
                'hwMajorVersion': 1,
                'hwMinorVersion': 0,
                'manu_string': 'PyAlertMe'
            }
        }
        self.assertEqual(result, expected)

        # Test get device
        result = self.hub_obj.get_device('00:0d:6f:00:01:72:f7:1b')
        self.assertTrue(result['type'] == 'SmartPlug')
        self.assertTrue(result['hwMajorVersion'] == 1)
        self.assertTrue(result['hwMinorVersion'] == 0)

    def test_mock_serial(self):
        """
        Test Mock Serial
        """
        # Match Descriptor Request
        message = {
            'source_addr_long': b'\x00\x13\xa2\x00@\xa2;\t',
            'source_addr': 'RK',
            'source_endpoint': b'\x00',
            'dest_endpoint': b'\x00',
            'profile': b'\x00\x00',
            'cluster': b'\x00\x06',
            'id': 'rx_explicit',
            'options': b'\x01',
            'rf_data': b'\x01\xfd\xff\x16\xc2\x00\x01\xf0\x00'
        }
        self.hub_obj.receive_message(message)
        result = self.hub_ser.get_data_written()
        expected = b'~\x00\x17}1\x00\x00}3\xa2\x00@\xa2;\tRK\x02\x02\x00\xf6\xc2\x16\x00\x00}1\x00\xfc\x97'        
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main(verbosity=2)
