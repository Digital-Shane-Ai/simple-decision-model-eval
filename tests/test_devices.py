"""Explicit GPU requests must never silently become CPU comparisons."""
import unittest
from unittest.mock import patch

from model_worker import device_name, synchronize


class DeviceTests(unittest.TestCase):
    def test_indexed_mps_device_is_synchronized(self):
        with patch('torch.mps.synchronize') as sync:
            synchronize('mps:0')
        sync.assert_called_once_with()

    def test_explicit_mac_gpu_fails_when_metal_is_hidden(self):
        with patch('torch.backends.mps.is_available', return_value=False):
            with self.assertRaisesRegex(RuntimeError, 'Mac GPU is unavailable'):
                device_name('mps')

    def test_auto_selects_available_mac_gpu(self):
        with patch('torch.cuda.is_available', return_value=False), \
                patch('torch.backends.mps.is_available', return_value=True):
            self.assertEqual(device_name('auto'), 'mps')


if __name__ == '__main__':
    unittest.main()
