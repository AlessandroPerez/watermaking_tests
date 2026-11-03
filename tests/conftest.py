import os

# as wmecc.experiment does: must be set before numba is first imported
os.environ.setdefault("NUMBA_NUM_THREADS", "1")
