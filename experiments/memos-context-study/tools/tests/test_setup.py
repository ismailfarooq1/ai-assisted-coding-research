"""Preparation safeguards, using the pinned local source; no agents or app tests."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

TOOL = Path(__file__).resolve().parents[1] / 'setup.py'
spec = importlib.util.spec_from_file_location('memos_setup', TOOL)
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)
ORIGINAL_STUDY = setup.STUDY


@unittest.skipUnless(setup.SOURCE.exists(), 'Run make setup to download the pinned local source first')
class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.study = Path(self.temp.name) / 'study'
        (self.study / 'shared').mkdir(parents=True)
        shutil.copyfile(ORIGINAL_STUDY / 'shared/study.json', self.study / 'shared/study.json')
        for method in setup.METHODS:
            target = self.study / 'methods' / method
            target.mkdir(parents=True)
            shutil.copyfile(ORIGINAL_STUDY / 'methods' / method / 'method.json', target / 'method.json')
        shutil.copytree(ORIGINAL_STUDY / 'methods/prepared-context/context',
                        self.study / 'methods/prepared-context/context')
        self.addCleanup(patch.stopall)
        patch.object(setup, 'STUDY', self.study).start()

    def test_projects_share_source_without_sharing_writable_files(self):
        first = setup.setup('existing-workflow')
        second = setup.setup('prepared-context')
        self.assertEqual(first['source_commit'], second['source_commit'])
        left = setup.method_path('existing-workflow') / 'project'
        right = setup.method_path('prepared-context') / 'project'
        self.assertEqual((left / 'go.mod').read_bytes(), (right / 'go.mod').read_bytes())
        self.assertNotEqual((left / 'go.mod').stat().st_ino, (right / 'go.mod').stat().st_ino)
        self.assertTrue((left / '.git').is_dir())
        self.assertTrue((right / '.git').is_dir())
        before = (right / 'README.md').read_bytes()
        with (left / 'README.md').open('a') as f:
            f.write('\nLocal change in experiment one\n')
        self.assertEqual((right / 'README.md').read_bytes(), before)
        with self.assertRaisesRegex(ValueError, 'Starting files changed'):
            setup.check('existing-workflow')
        setup.check('prepared-context')

    def test_prepared_method_retains_native_body_and_adds_only_context(self):
        setup.setup('prepared-context')
        project = setup.method_path('prepared-context') / 'project'
        original = setup.git('show', setup.spec()['project']['candidate_commit'] + ':AGENTS.md',
                             cwd=setup.SOURCE, binary=True)
        self.assertEqual((project / 'AGENTS.md').read_bytes(), original + setup.CONTEXT_NOTICE)
        self.assertEqual(set(setup.git('diff', '--name-only', 'HEAD', cwd=project).splitlines()), {'AGENTS.md'})
        self.assertEqual(setup.git('remote', cwd=project), '')
        self.assertEqual(len(list((project / setup.CONTEXT_DIR).glob('*.md'))), 4)

    def test_repeated_setup_keeps_manifest_and_existing_work(self):
        first = setup.setup('existing-workflow')
        folder = setup.method_path('existing-workflow')
        manifest = (folder / 'setup-manifest.json').read_bytes()
        self.assertEqual(setup.setup('existing-workflow'), first)
        self.assertEqual((folder / 'setup-manifest.json').read_bytes(), manifest)
        target = folder / 'project/README.md'
        target.write_text('Uncommitted task work must survive.\n')
        with self.assertRaisesRegex(ValueError, 'refusing to overwrite'):
            setup.setup('existing-workflow')
        self.assertEqual(target.read_text(), 'Uncommitted task work must survive.\n')

    def test_third_method_refuses_setup_before_source_access(self):
        with patch.object(setup, 'acquire_source') as acquire:
            with self.assertRaisesRegex(ValueError, 'disabled shell'):
                setup.setup('proposed-method')
            acquire.assert_not_called()
        self.assertFalse((setup.method_path('proposed-method') / 'project').exists())
        self.assertFalse((setup.method_path('proposed-method') / 'setup-manifest.json').exists())

    def test_context_tampering_is_detected(self):
        setup.setup('prepared-context')
        project = setup.method_path('prepared-context') / 'project'
        (project / setup.CONTEXT_DIR / 'README.md').write_text('Changed context\n')
        with self.assertRaisesRegex(ValueError, 'Starting files changed'):
            setup.check('prepared-context')

    def test_unexpected_agent_visible_file_is_detected(self):
        setup.setup('existing-workflow')
        project = setup.method_path('existing-workflow') / 'project'
        (project / 'other-method-result.txt').write_text('Unpermitted extra input\n')
        with self.assertRaisesRegex(ValueError, 'Starting files changed'):
            setup.check('existing-workflow')

    def test_changed_shared_settings_require_repreparation(self):
        setup.setup('existing-workflow')
        target = self.study / 'shared/study.json'
        settings = json.loads(target.read_text())
        settings['agent_model'] = 'a-new-unfrozen-setting'
        target.write_text(json.dumps(settings))
        with self.assertRaisesRegex(ValueError, 'Shared study configuration changed'):
            setup.check('existing-workflow')


if __name__ == '__main__':
    unittest.main()
