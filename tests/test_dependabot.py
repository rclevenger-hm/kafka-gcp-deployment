"""Offline compatibility-contract port, not a full Dependabot integration test.

Ports provider_declaration_regex and update_registry_declaration (lines 142-162,
386-403), including their line-anchored version substitution, from:
https://github.com/dependabot/dependabot-core/blob/905e544553263dd3d60f49caab10f923c3153eb1/terraform/lib/dependabot/terraform/file_updater.rb
Copyright GitHub, Inc.; MIT license in LICENSE.dependabot beside this file.
"""
from pathlib import Path
import re
import unittest

TERRAFORM = Path(__file__).resolve().parents[1] / "terraform/versions.tf"
EXPECTED_PROVIDERS = ["hashicorp/google", "hashicorp/random"]


def update_requirement(content, provider, old, new):
    name = re.escape(provider)
    registry = re.escape("registry.terraform.io")
    version_first = rf'''(((?<!required_)version\s=\s*["'].*["'])(\s*source\s*=\s*["']({registry}/)?{name}["']|\s*{name}\s*=\s*\{{.*))'''
    source_first = rf'''((source\s*=\s*["']({registry}/)?{name}["']|\s*{name}\s*=\s*\{{.*)(?:(?!^\}}).)+)'''
    # Ruby /m means dot-all, while its ^/$ are always line anchors.
    flags = re.DOTALL | re.MULTILINE | re.IGNORECASE | re.VERBOSE
    declaration = version_first if re.search(version_first, content, flags) else source_first
    version = rf'''^\s*version\s*=\s*["'].*{re.escape(old)}.*['"]'''
    return re.sub(declaration, lambda match: re.sub(
        version, lambda line: line[0].replace(old, new, 1),
        match[0], count=1, flags=re.MULTILINE,
    ), content, flags=flags)


def provider_requirements(content):
    """Read flat source/version objects, accepting either order and inline HCL."""
    requirements = []
    for block in re.finditer(r"[\w-]+\s*=\s*\{([^{}]*)\}", content):
        source = re.search(r'\bsource\s*=\s*"([^"]+)"', block[1])
        version = re.search(r'\bversion\s*=\s*"([^"]+)"', block[1])
        if source and version:
            requirements.append((source[1], version[1],
                                 block.start(1) + version.start(1),
                                 block.start(1) + version.end(1)))
    return requirements


class DependabotProviderTests(unittest.TestCase):
    def test_each_checked_in_provider_updates_without_other_changes(self):
        content = TERRAFORM.read_text()
        requirements = provider_requirements(content)
        self.assertCountEqual([item[0] for item in requirements], EXPECTED_PROVIDERS)
        for provider, old, start, end in requirements:
            with self.subTest(provider=provider):
                new = "999.0.0"  # Synthetic requirement, used only in memory.
                self.assertNotEqual(old, new)
                updated = update_requirement(content, provider, old, new)
                # Full-file equality protects all other providers and required_version.
                self.assertEqual(updated, content[:start] + new + content[end:])

    def test_inline_fixture_reproduces_the_failed_update(self):
        content = ('terraform {\n  required_providers {\n'
                   '    example = { source = "hashicorp/example", version = "~> 1.0" }\n'
                   '  }\n}\n')
        self.assertEqual(len(provider_requirements(content)), 1)
        self.assertEqual(update_requirement(content, "hashicorp/example", "~> 1.0", "~> 2.0"), content)
