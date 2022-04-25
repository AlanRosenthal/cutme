int fn_b(int bbb1);

int fn_a(int param1, int param2) {
    return param1 + param2 + fn_b(param1);
}
