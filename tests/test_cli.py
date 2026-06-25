from typer.testing import CliRunner

from nodex.cli.main import app

runner = CliRunner()


class TestCli:
    def test_help_lists_commands(self):
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "new" in result.output
        assert "run" in result.output
        assert "dev" in result.output

    def test_new_creates_project_files(self):
        import os
        from pathlib import Path
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmpdir:
            old_cwd = Path.cwd()
            os.chdir(tmpdir)
            try:
                result = runner.invoke(app, ["new", "my-agent"])
            finally:
                os.chdir(old_cwd)

            assert result.exit_code == 0
            assert "Created nodex project" in result.output

            project = Path(tmpdir) / "my-agent"
            assert (project / "agent.py").exists()
            assert (project / ".env").exists()
            assert (project / "requirements.txt").exists()
            assert (project / ".gitignore").exists()

    def test_new_fails_when_directory_exists(self):
        import os
        from pathlib import Path
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmpdir:
            old_cwd = Path.cwd()
            os.chdir(tmpdir)
            try:
                Path("my-agent").mkdir()
                result = runner.invoke(app, ["new", "my-agent"])
            finally:
                os.chdir(old_cwd)

            assert result.exit_code == 1
            assert "already exists" in result.output

    def test_run_rejects_invalid_target(self):
        result = runner.invoke(app, ["run", "agent"])

        assert result.exit_code == 1
        assert "Invalid format" in result.output

    def test_run_rejects_invalid_json(self):
        result = runner.invoke(app, ["run", "agent:app", "--input", "{bad"])

        assert result.exit_code == 1
        assert "Invalid JSON" in result.output
