import unittest
import mock
import time

import knxsonos.knx
import knxsonos.knxsonos
import knxsonos.sonos

def sleep1(t):
    time.sleep(1)

class wrapGetAPDU(object):

    def __init__(self, kl):
        self.kl = kl

    def EIBGetAPDU_Src(self, buf, src):

        self.kl.stopping = True
        buf.buffer = [1, 2]
        return 2

    def EIBClose(self):
        pass


class TestKnxSonos(unittest.TestCase):

    def setUp(self):

        self.sonos = None

    def tearDown(self):

        if self.sonos:
            self.sonos.stop()

    def test_config(self):

        cfg = knxsonos.knxsonos.loadConfig()

        self.assertEqual(cfg["knx"]["url"], "ip:gax58")

        # Should be 8 zones in example config
        self.assertEqual(len(cfg["zones"]), 8)

    @mock.patch("knxsonos.knx.EIBConnection")
    @mock.patch("knxsonos.knx.readgaddr")
    def test_knx(self, mock_readg, mock_eibc):

        mock_readg.return_value = "xx"

        inst = mock_eibc.return_value
        inst.EIBSocketURL.return_value = 0
        inst.EIBOpenT_Group.return_value = 0

        action = mock.Mock()

        kl = knxsonos.knx.KnxListenGrpAddr(
            "ip:localhost", "zone1", "1/1/1", (action, "param"))

        inst.EIBSocketURL.assert_called_with("ip:localhost")
        inst.EIBOpenT_Group.assert_called_with("xx", 0)

        wrc = mock.Mock(wraps=wrapGetAPDU(kl))
        kl.con = wrc

        kl.run()

        action.assert_called_once_with("zone1", "param")

        wrc.EIBClose.assert_called_once_with()
        wrc.EIBGetAPDU_Src.assert_called_once_with(mock.ANY, mock.ANY)

    @mock.patch("knxsonos.sonos.sleep", wraps=sleep1)
    @mock.patch("knxsonos.sonos.discover")
    def test_sonos(self, mock_discover, mock_sleep):

        z1 = mock.Mock(player_name="z1")
        z2 = mock.Mock(player_name="z2")

        mock_discover.return_value = [z1, z2]

        s = knxsonos.sonos.SonosCtrl(["z1", "z2"])
        self.sonos = s
        s.start()
        time.sleep(0.5)
        mock_discover.assert_called_once_with(10)
        mock_sleep.assert_called_once_with(1)
        time.sleep(1)
        self.assertEqual(mock_sleep.call_count, 2)

        s.play("z1")
        z1.group.coordinator.play.assert_called_once_with()
        self.assertFalse(z2.group.coordinator.play.called)

        s.pause("z2")
        z2.group.coordinator.pause.assert_called_once_with()
        self.assertFalse(z1.group.coordinator.pause.called)

        s.setURI("z2", "theURI")
        s.setURI("z1", "theOtherURI")
        z2.group.coordinator.play_uri.assert_called_once_with(
            "theURI", start=True)
        z1.group.coordinator.play_uri.assert_called_once_with(
            "theOtherURI", start=True)

if __name__ == '__m':
    unittest.main()
