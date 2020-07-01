"""
Unit tests of WD invocation
"""
import unittest


class TestJobScheduling(unittest.TestCase):
    """ Tests Running WD Code"""

    def setUp(self):
        pass

    def test_lc_scheduling(self):
        import wdwrap
        from wdwrap.jobs import JobScheduler
        ret = JobScheduler.instance.schedule('lc', wdwrap.default_binary())
        r = ret.result()
        print(r)



if __name__ == '__main__':
    unittest.main()
