OUTPUT_FORMAT(elf64-x86-64)
ENTRY(_start)

/* Definiujemy nagłówki programu, które zmuszą linker do wrzucenia wszystkiego w wyższą pamięć */
PHDRS
{
    text PT_LOAD FLAGS(5);    /* Odczyt + Wykonanie (R-X) */
    data PT_LOAD FLAGS(6);    /* Odczyt + Zapis (RW-) */
}

SECTIONS
{
    /* Limine ładuje jądro w wyższej pamięci wirtualnej */
    . = 0xffffffff80000000;

    .text : {
        *(.text .text.*)
    } :text

    .rodata : {
        *(.rodata .rodata.*)
    } :text

    /* Przesuwamy wskaźnik na nową stronę pamięci dla sekcji danych */
    . = ALIGN(CONSTANT(MAXPAGESIZE));

    .data : {
        *(.data .data.*)
    } :data

    .bss : {
        *(.bss .bss.*)
        *(COMMON)
    } :data
}
