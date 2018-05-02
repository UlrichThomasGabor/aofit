#include <stdio.h>
#include <chrono>
#include <iostream>
#include <time.h>
#include <math.h>

int test() {
	// Wait here too, to make sure our test program is able to
	// differentiate between the custom sleep and the normal nanosleep.
	struct timespec ts;
	ts.tv_sec = 0;
	unsigned int duration_in_ms = 500;
	ts.tv_nsec = duration_in_ms * 1000000.0;

	nanosleep(&ts, NULL);

	return 5;
}

int main() {
	auto start = std::chrono::system_clock::now();
	test();
	auto end = std::chrono::system_clock::now();
	auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
	auto elapsed_seconds = lround(elapsed.count() / 1000.0);
	std::cout << elapsed_seconds << '\n';
	return 0;
}
