import importlib.util
import pathlib
import tempfile
import unittest

SERVER_PATH = pathlib.Path(__file__).parents[1] / 'server.py'
spec = importlib.util.spec_from_file_location('voice_recorder_server', SERVER_PATH)
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)

class VoiceRecorderSecurityTests(unittest.TestCase):
    def test_slug_removes_path_and_html(self):
        self.assertEqual(server.safe_slug('../../<b>Giọng Hương</b>'), 'giong-huong')

    def test_extension_from_allowed_audio_type(self):
        self.assertEqual(server.extension_for('audio/webm;codecs=opus'), '.webm')
        with self.assertRaises(ValueError):
            server.extension_for('text/html')

    def test_unique_recording_dir_stays_inside_root(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d).resolve()
            target = server.make_recording_dir(root, '../Hương')
            self.assertTrue(target.resolve().is_relative_to(root))
            self.assertTrue(target.is_dir())

if __name__ == '__main__':
    unittest.main()
