import unittest
import resources.lib.channels.lesdocus as plugin
import time


class SimpleTest(unittest.TestCase):
    def setUp(self):
        plugin.test_mode = True

    def test_1(self):
        root_menu = (plugin.list_shows('lesdocus', 'none'))
        print('Root menu %s' % root_menu)
        self.assertNotEquals(0, len(root_menu))

        first_sub_menu = plugin.list_shows('lesdocus', root_menu[0][1])
        self.assertNotEquals(0, len(first_sub_menu))
        print('Sub menu %s' % first_sub_menu)

        start_time = time.time()
        videos = plugin.list_videos('lesdocus', first_sub_menu[0][1])
        elapsed_time = time.time() - start_time
        self.assertNotEquals(0, len(videos))
        print('Loaded %d Videos in %d seconds' % (len(videos), elapsed_time))

    def test_url_resolution(self):
        self.assertIsNotNone(plugin.getVideoURL('lesdocus', 'http://www.les-docus.com/new-york-face-aux-ouragans/'))
        self.assertIsNotNone(plugin.getVideoURL('lesdocus', 'http://www.les-docus.com/archi-du-sud/'))
        self.assertIsNotNone(
            plugin.getVideoURL('lesdocus', 'http://www.les-docus.com/cest-pas-sorcier-faire-un-disque-ca-vous-chante/'))

    def test_multithread(self):
        start_time = time.time()
        result = plugin.list_videos_multithreaded('lesdocus', u'http://www.les-docus.com/arts/architecture/')
        elapsed_time = time.time() - start_time
        print('Loaded %d Videos in %d seconds' % (len(result), elapsed_time))