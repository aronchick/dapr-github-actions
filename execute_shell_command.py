import os
import subprocess
import time
import select
import sys

def execute(command, finish_time=3):
    # create a pipe to receive stdout and stderr from process
    (pipe_r, pipe_w) = os.pipe()

    p = subprocess.Popen(command,
                        shell = True,
                        stdout = pipe_w,
                        stderr = pipe_w)


    start = time.time()

    # Loop while the process is executing
    while p.poll() is None:

        # Loop long as the selct mechanism indicates there
        # is data to be read from the buffer
        while len(select.select([pipe_r], [], [], 0)[0]) == 1:

            # Read up to a 1 KB chunk of data
            buf = os.read(pipe_r, 1024)

            sys.stdout.write(str(buf, "utf8"))
            sys.stdout.flush()

        end = time.time()
        if ((end - start) > finish_time):
            break
