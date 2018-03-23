#include <stdio.h>

int main() {
	FILE *fp = fopen("main.cc", "r");
	char c;
	while ((c = getc(fp)) != EOF) {
		putchar(c);
	}
	fclose(fp);
	return 0;
}

