#include <stdio.h>

namespace aofit {
	attribute noerror(const char*, ...);
}

int main() {
	FILE *fp;
	[[aofit::noerror("EINTR", "EISDIR", "ELOOP", "EMFILE", "ENAMETOOLONG", "ENFILE", "ENOENT", "ENOTDIR", "ENOSPC", "ENOTDIR", "ENXIO", "EROFS", "EINVAL", "ENOMEM", "ETXTBSY")]] {
		fp = fopen("main.cc", "r");
	}
	char c;
	while ((c = getc(fp)) != EOF) {
		putchar(c);
	}
	fclose(fp);
	return 0;
}
