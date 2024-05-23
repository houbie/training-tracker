import compileall
import sys
from py_compile import PycInvalidationMode

dependencies_dir = sys.argv[1]
sys.path.append(dependencies_dir)
compileall.compile_dir("../src", force=True, invalidation_mode=PycInvalidationMode.UNCHECKED_HASH, optimize=2)
