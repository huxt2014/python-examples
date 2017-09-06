
import os
import sys

version_info = '%s.%s' % sys.version_info[0:2]

for d in os.listdir("./build"):
    if d.startswith('lib') and d.find(version_info) > 0:
        sys.path.append(os.path.join('build', d))
        break
