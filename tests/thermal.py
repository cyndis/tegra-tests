import unittest

from linux import sysfs, kmsg
import tegra

class ThermalZone:
    def __init__(self, num):
        self.sysfs = sysfs.Object('class/thermal/thermal_zone%u' % num)

    def __getattr__(self, name):
        if name == 'type':
            with self.sysfs.open('type') as file:
                return file.read().strip()

        if name == 'temp':
            with self.sysfs.open('temp') as file:
                return int(file.read().strip())

        return super.__getattr__(self, name)

def num_zones():
    n = 0
    while True:
        if not sysfs.exists('class/thermal/thermal_zone%u' % n):
            return n
        n += 1

def thermal_enabled():
    return sysfs.exists('class/thermal')

@unittest.skipUnless(thermal_enabled(), 'Thermal sysfs not enabled')
class thermal(unittest.TestCase):
    def test_cpu_temp(self):
        n = num_zones()
        cpu = None

        for i in range(n):
            tz = ThermalZone(i)
            if tz.type == 'cpu':
                cpu = tz

        self.assertIsNotNone(cpu)
        self.assertTrue(cpu.temp > 1000)
        self.assertTrue(cpu.temp < 80000)

def tsense_reset_supported():
    return tegra.detect().compatible in ('nvidia,tegra20', 'nvidia,tegra30',
                                         'nvidia,tegra114', 'nvidia,tegra124',
                                         'nvidia,tegra132', 'nvidia,tegra210')

@unittest.skipUnless(tsense_reset_supported(), 'TSENSE reset not supported')
class tsense_reset(unittest.TestCase):
    def test_tsense_reset(self):
        found = False
        with kmsg.open() as k:
            for entry in k:
                if 'emergency thermal reset enabled' in entry.message:
                    found = True
                    break
        self.assertTrue(found)
