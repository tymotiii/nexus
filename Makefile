# Używamy standardowego systemowego kompilatora
CC = gcc
LD = ld
OBJCOPY = objcopy
TAR = tar

# Flagi dla JĄDRA
CFLAGS = -Wall -Wextra -O2 -pipe -std=c11 \
         -ffreestanding -fno-stack-protector -fno-stack-check \
         -fno-lto -fno-PIE -fno-pic -m64 -march=x86-64 \
         -mno-80387 -mno-mmx -mno-sse -mno-sse2 -mno-red-zone \
         -mcmodel=kernel \
         -maccumulate-outgoing-args \
         -Ikernel/include

LDFLAGS = -nostdlib -static -no-pie -m elf_x86_64 -T kernel/arch/x86_64/linker.ld

# Flagi dla PROGRAMU UŻYTKOWNIKA (w initramfs)
# Linkujemy pod sztywny adres 0x2000000, bez nagłówków ELF
USER_CFLAGS  = -m64 -nostdlib -nostdinc -fno-builtin -fno-stack-protector -ffreestanding -c
USER_LDFLAGS = -m elf_x86_64 -Ttext 0x2000000 --oformat=elf64-x86-64

# Ścieżki ramdysku
INITRAMFS_SRC_DIR = initramfs
ETC_DIR           = $(INITRAMFS_SRC_DIR)/etc
TARGET_USER_BIN   = $(ETC_DIR)/test.bin
OUTPUT_TAR        = iso_root/boot/initramfs.tar

# Znajdź wszystkie pliki .c w folderze kernel i podfolderach
SRCS = $(shell find kernel -name "*.c")
OBJS = $(SRCS:%.c=build/%.o)

.PHONY: all clean iso qemu run initramfs_build

all: iso

# Kompilacja plików .c jądra do obiektowych .o
build/%.o: %.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c $< -o $@

# Linkowanie kernela do pliku .elf
iso_root/boot/kernel.elf: $(OBJS)
	@mkdir -p iso_root/boot
	$(LD) $(OBJS) $(LDFLAGS) -o $@

# =========================================================================
# AUTOMATYCZNE BUDOWANIE INITRAMFS
# =========================================================================
# =========================================================================
# AUTOMATYCZNE BUDOWANIE INITRAMFS
# =========================================================================
initramfs_build: iso_root/boot/kernel.elf
	@mkdir -p $(ETC_DIR)
	@echo "[nexus] cc: compiling user space app..."
	@$(CC) $(USER_CFLAGS) $(ETC_DIR)/test.c -o $(ETC_DIR)/test.o
	@echo "[nexus] ld: linking user space app using kernel symbols"
	# DODALIŚMY: -R iso_root/boot/kernel.elf
	@$(LD) $(USER_LDFLAGS) -R iso_root/boot/kernel.elf $(ETC_DIR)/test.o -o $(ETC_DIR)/test.elf
	@echo "[nexus] objcopy: stripping ELF headers to raw binary"
	@$(OBJCOPY) -O binary $(ETC_DIR)/test.elf $(TARGET_USER_BIN)
	@echo "[nexus] tar: packing $(INITRAMFS_SRC_DIR)/ into $(OUTPUT_TAR)"
	@cd $(INITRAMFS_SRC_DIR) && $(TAR) -cf ../$(OUTPUT_TAR) . --format=ustar

# Budowanie gotowego obrazu ISO (teraz zależy również od initramfs_build)
iso: iso_root/boot/kernel.elf initramfs_build
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
	rm -rf build iso_root/boot/kernel.elf iso_root/boot/initramfs.tar myos.iso
	rm -f $(ETC_DIR)/test.o $(ETC_DIR)/test.elf $(TARGET_USER_BIN)
