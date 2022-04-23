#include <stdint.h>
#include <stdbool.h>
#include <assert.h>
#include "onefile.h"

uint32_t fn1(bool enable) {
    uint32_t ret3 = 10;
    if (enable) {
        ret3 = 20;
    }
    return 95 + ret3;
}

uint32_t fn2(int myparam1, char myparam2) {
    uint32_t ret = 10;
    if (myparam1 > 10) {
        ret = 20;
    }
    return 95 - ret;
}
