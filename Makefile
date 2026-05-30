# Używamy standardowego systemowego kompilatora
CC = gcc
LD = ld

CFLAGS = -Wall -Wextra -O2 -pipe -std=c11 \
         -ffreestanding -fno-stack-protector -fno-stack-check \
         -fno-lto -fno-PIE -fno-pic -m64 -march=x86-64 \
         -mno-80387 -mno-mmx -mno-sse -mno-sse2 -mno-red-zone \
         -mcmodel=kernel \
         -maccumulate-outgoing-args \
         -Ikernel/include


LDFLAGS = -nostdlib -static -no-pie -m elf_x86_64 -T kernel/arch/x86_64/linker.ld

# Znajdź wszystkie pliki .c w folderze kernel i podfolderach
SRCS = $(shell find kernel -name "*.c")
OBJS = $(SRCS:%.c=build/%.o)

# Tutaj dopisujemy 'run', żeby był oficjalną komendą
.PHONY: all clean iso qemu run

all: iso

# Kompilacja plików .c do obiektowych .o
build/%.o: %.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c $< -o $@

# Linkowanie kernela do pliku .elf
iso_root/boot/kernel.elf: $(OBJS)
	@mkdir -p iso_root/boot
	$(LD) $(OBJS) $(LDFLAGS) -o $@

# Budowanie gotowego obrazu ISO
iso: iso_root/boot/kernel.elf
	cp limine/limine-bios.sys limine/limine-bios-cd.bin iso_root/boot/
	xorriso -as mkisofs -b boot/limine-bios-cd.bin \
		-no-emul-boot -boot-load-size 4 -boot-info-table \
		iso_root -o myos.iso
	./limine/limine bios-install myos.iso

# Starsza reguła qemu (zostawiamy ją)
qemu: iso
	qemu-system-x86_64 -cdrom myos.iso

# NOWOŚĆ: Twoje upragnione 'make run'
run: iso
	qemu-system-x86_64 -cdrom myos.iso

clean:
	rm -rf build iso_root/boot/kernel.elf myos.iso
