#include <stdint.h>
#include <stdbool.h>
#include <assert.h>

#include "onefile.h"

void setup(void) {
}

void teardown(void) {
}

void test_fn1_disable(void) {
    int ret = fn1(false);
    assert(ret == 105);
}

void test_fn1_enable(void) {
    int ret = fn1(true);
    assert(ret == 115);
}

