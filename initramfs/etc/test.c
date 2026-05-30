// Zamiast stdint.h definiujemy podstawowe typy wbudowane w architekturę x86_64
typedef unsigned int        uint32_t;
typedef unsigned long long  uint64_t;

// Informujemy kompilator o funkcji z jądra
extern void terminal_print(const char *str, uint32_t color);

void _start(void) {
    // Przypisujemy adres do wskaźnika, aby wymusić bezpieczny 64-bitowy skok absolutny
    void (*print)(const char*, uint32_t) = terminal_print;

    // Wywołujemy funkcję przez wskaźnik!
    print("Welcome from test.c!", 0xFFFFFFFF);

    while(1) {
        // Nasza pętla procesu
        for(volatile int i = 0; i < 10000000; i++);
    }
}
