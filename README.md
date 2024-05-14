# irradiate.py

A simple script to simulate random "cosmic ray" memory errors against a linux process.

```
USAGE: irradiate.py target_pid flip_rate

where flip_rate is measured in "bit flips per megabyte per second"
```

`example_target.py` is a simple script that hashes a buffer at regular intervals. Bit-flips that modify the value of the buffer will cause the hash to change. Bit-flips elsewhere might crash or hang the process, or explode your computer - anything is possible!

Example invocation:

```
$ python3 example_target.py 
Hello, I am running as PID 299761
t=0,    sha256(buf)=21cf078a3545d03437366e36a8c3c067...
t=1,    sha256(buf)=21cf078a3545d03437366e36a8c3c067...
t=2,    sha256(buf)=21cf078a3545d03437366e36a8c3c067...
t=3,    sha256(buf)=21cf078a3545d03437366e36a8c3c067...
t=4,    sha256(buf)=21cf078a3545d03437366e36a8c3c067...
t=5,    sha256(buf)=21cf078a3545d03437366e36a8c3c067...
t=6,    sha256(buf)=35d5ddcf517c64651352a170092825c0...
t=7,    sha256(buf)=1a999a28a8d2c56f82fb3a65636c8ebc...
double free or corruption (out)
Aborted (core dumped)
```

After `t=5`, I ran `python3 irradiate.py 299761 10` in another terminal session, where 299761 is the target PID, and 10 means 10 bitflips per megabyte of RAM, per second.

At `t=6` and `t=7`, you can see the buffer is getting corrupted, and later, the heap. Results may vary!

Bit-flip intervals are currently evenly spaced in time. For fast flip rates this probably doesn't matter, but for slower rates I should implement realistic random delay distributions (TODO).

Depending on the security config of your system, you may need to invoke `irradiate.py` with root privileges.
