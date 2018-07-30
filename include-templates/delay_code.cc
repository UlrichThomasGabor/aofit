struct timespec ts;
// Chop off too big values in duration_in_ms, because it might not work as expected.
ts.tv_sec = round(duration_in_ms / 1000);
ts.tv_nsec = (duration_in_ms - (round(duration_in_ms / 1000) * 1000)) * 1000000.0;
nanosleep(&ts, NULL);
