"""Keep test scratch data independent of shared Windows temp permissions."""
from pathlib import Path
import tempfile


def pytest_configure(config):
    # Preserve an explicitly supplied --basetemp. Each default run gets its own
    # directory, so concurrent runs do not erase one another's databases/models.
    if config.option.basetemp is None:
        scratch = Path(__file__).resolve().parents[1] / '.test-tmp'
        scratch.mkdir(exist_ok=True)
        config.option.basetemp = tempfile.mkdtemp(prefix='run-', dir=scratch)
