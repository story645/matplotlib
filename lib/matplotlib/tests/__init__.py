from pathlib import Path
import pytest

pytest.register_assert_rewrite("matplotlib.testing")

# Check that the test directories exist.
if not (Path(__file__).parent / 'baseline_images').exists():
    raise OSError(
        'The baseline image directory does not exist. '
        'This is most likely because the test data is not installed. '
        'You may need to install matplotlib from source to get the '
        'test data.')
