import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from configure import ProjectConfigurator

def test_project_configurator_replacements():
    with tempfile.TemporaryDirectory() as tmpdir:
        sample_file = os.path.join(tmpdir, "sample.md")
        with open(sample_file, "w", encoding="utf-8") as f:
            f.write("Welcome to AgentPulse on agentpulse.dev. Contact: contact@agentpulse.dev, Repo: your-username/agentpulse")

        configurator = ProjectConfigurator(tmpdir)
        stats = configurator.apply_configuration(
            project_name="DeepFlow",
            domain="deepflow.ai",
            contact_email="team@deepflow.ai",
            github_repo="felix/deepflow",
            files=["sample.md"]
        )

        assert stats["sample.md"] == 4

        with open(sample_file, "r", encoding="utf-8") as f:
            updated = f.read()

        assert "DeepFlow" in updated
        assert "deepflow.ai" in updated
        assert "team@deepflow.ai" in updated
        assert "felix/deepflow" in updated
        assert "AgentPulse" not in updated

def test_project_configurator_nonexistent_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        configurator = ProjectConfigurator(tmpdir)
        stats = configurator.apply_configuration(
            project_name="TestApp",
            domain="test.dev",
            contact_email="a@b.com",
            github_repo="a/b",
            files=["missing.txt"]
        )
        assert "missing.txt" not in stats
