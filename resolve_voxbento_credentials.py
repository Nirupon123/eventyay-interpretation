with open("interpretation/backends/voxbento_credentials.py", "r") as f:
    content = f.read()

import re

conflict_pattern = re.compile(r"<<<<<<< HEAD\n(.*?)\n=======\n.*?\n>>>>>>> origin/dev", re.DOTALL)
content = conflict_pattern.sub(r"\1", content)

with open("interpretation/backends/voxbento_credentials.py", "w") as f:
    f.write(content)
