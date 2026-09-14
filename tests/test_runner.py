import sys
import tempfile
import unittest
from pathlib import Path

from moose_benchmark.loader import resolve_inside
from moose_benchmark.runner import RunLimits, run_command


class RunnerTests(unittest.TestCase):
    def test_shell_free_command_runner(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_command(
                [sys.executable, "-c", "print('ok')"],
                cwd=Path(directory),
                limits=RunLimits(wall_time_seconds=10, cpu_seconds=5, memory_mib=1024),
            )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout.strip(), "ok")

    def test_root_confinement(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                resolve_inside(Path(directory), "../outside.i")

    def test_limits_must_be_positive(self):
        with self.assertRaises(ValueError):
            RunLimits(wall_time_seconds=0, cpu_seconds=1, memory_mib=1)

    def test_wall_timeout_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_command(
                [sys.executable, "-c", "import time; time.sleep(2)"],
                cwd=Path(directory),
                limits=RunLimits(wall_time_seconds=1, cpu_seconds=5, memory_mib=1024),
            )
        self.assertTrue(result.timed_out)
        self.assertIsNone(result.exit_code)


if __name__ == "__main__":
    unittest.main()
