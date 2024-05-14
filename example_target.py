import os
import hashlib
import time

print("Hello, I am running as PID", os.getpid())

buf = os.urandom(1024*1024*128) # 128MiB buffer

t = 0
while True:
	print(f"t={t},\tsha256(buf)={hashlib.sha256(buf).hexdigest()[32:]}...")
	time.sleep(1)
	t += 1
