#include <stdio.h>
#include <chrono>
#include <iostream>
#include <time.h>
#include <math.h>

int test() {
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
