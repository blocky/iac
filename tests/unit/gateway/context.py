import sys

from get_project_root.get_project_root import root_path

sys.path.insert(0, root_path())

import gateway  # noqa # pylint: disable=unused-import, wrong-import-position
