#!/usr/bin/env python3

import re
import sys
import random
import time
import math
import logging
from typing import List, BinaryIO
from dataclasses import dataclass

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@dataclass
class MemRange:
	start: int
	length: int

def enumerate_readable_ranges(target_pid: int) -> List[MemRange]:
	ranges = []
	with open(f"/proc/{target_pid}/maps") as maps_file:
		for line in maps_file.readlines():
			start_hex, end_hex, perms = re.match(
				r"^([0-9a-f]+)\-([0-9a-f]+) (.{4}) ",
				line
			).groups()
			if not perms.startswith("r"):
				continue
			start, end = int(start_hex, 16), int(end_hex, 16)
			ranges.append(MemRange(
				start=start,
				length=end - start
			))
	return ranges

def do_a_flip(mem: BinaryIO, ranges: List[MemRange]) -> None:
	range_total = sum(r.length for r in ranges)
	MAX_FLIP_RETRIES = 100
	for _ in range(MAX_FLIP_RETRIES):
		try:
			offset = random.randrange(range_total)
			bit_idx = random.randrange(8)
			for range_ in ranges:
				if offset < range_.length:
					target_addr = range_.start + offset
					break
				offset -= range_.length
			logger.debug(f"going to flip addr {hex(target_addr)}, bit {bit_idx}")
			mem.seek(target_addr)
			initial_val = mem.read(1)[0]
			flipped_val = initial_val ^ (1 << bit_idx)
			mem.seek(target_addr)
			mem.write(bytes([flipped_val]))
			logger.debug(f"0x{initial_val:02x} -> 0x{flipped_val:02x}")
			return True
		except:
			logger.info("flip failed, trying again at a different address...")

	logger.error("Failed to flip, giving up.")
	return False


if __name__ == "__main__":
	if len(sys.argv) != 3:
		print(f"USAGE: {sys.argv[0]} target_pid flip_rate")
		print()
		print('where flip_rate is measured in "bit flips per megabyte per second"')
		sys.exit(-1)

	target_pid = int(sys.argv[1])
	flip_rate = float(sys.argv[2])

	# if the flip rate is high, we'll perform flips in batches, such that the
	# expected avg wait time between batches does not fall below MIN_INTERVAL
	MIN_INTERVAL = 0.020 # 20ms

	while True:
		try:
			ranges = enumerate_readable_ranges(target_pid)
		except FileNotFoundError:
			logging.error("FileNotFoundError - the target process probably died")
			break

		range_total = sum(r.length for r in ranges)
		total_mb = range_total/1024/1024
		logging.info(f"found {hex(range_total)} bytes ({total_mb:.1f} MiB) of readable memory")

		flips_per_second = flip_rate * total_mb
		seconds_between_flips = 1 / flips_per_second

		if seconds_between_flips < MIN_INTERVAL:
			flip_count = int(MIN_INTERVAL // seconds_between_flips)
			interval = MIN_INTERVAL
		else:
			flip_count = 1
			interval = seconds_between_flips

		# I thiiiiiink this should give us a realistic exponential distribution?
		exp_interval = math.log(random.random()) * -interval

		logging.info(f"will perform {flip_count} flips and then wait {exp_interval:.2f} seconds ({interval:.2f} average)")

		try:
			with open(f"/proc/{target_pid}/mem", "wb+") as mem:
				for _ in range(flip_count):
					do_a_flip(mem, ranges)
			
			time.sleep(exp_interval)
		except FileNotFoundError:
			logging.error("FileNotFoundError - the target process probably died")
			break
		except IOError:
			logging.error("IOError - hoping this is temporary and retrying...")
