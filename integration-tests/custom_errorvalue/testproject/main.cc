#include <stdio.h>

aspect whatever {
	advice call("% ...::test(...)") : after() {
		*tjp->result() = 10;
	}
};

int test() {
	return 5;
}

int main() {
	printf("%d\n", test());
	return 0;
}
