#include <stdint.h>

#include "file_b.h"

int fn_b(uint16_t b1) {
    if (b1 == 0) {
        return 3;
    }
    if (b1 > 10) {
        return 10;
    }
    return 0;
}
