// Fill.asm (FIXED VERSION)
// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed,
// the screen should be cleared.

(RESTART)
    @KBD
    D=M
    @BLACK
    D;JGT       // Jika KBD > 0, lompat ke BLACK
    
    @WHITE
    0;JMP       // Jika tidak, lompat ke WHITE

(BLACK)
    @color
    M=-1        // Set variable 'color' jadi -1 (Hitam/All 1s)
                // Kita pake M=-1, BUKAN @-1
    @DRAW
    0;JMP       // Lanjut ke routine gambar

(WHITE)
    @color
    M=0         // Set variable 'color' jadi 0 (Putih)
    @DRAW
    0;JMP       // Lanjut ke routine gambar

(DRAW)
    // 1. Inisialisasi Pointer Screen
    @SCREEN     // Address 16384
    D=A
    @address
    M=D         // address = 16384

    // 2. Inisialisasi Counter Loop
    @8192       // Jumlah register layar (256 * 32)
    D=A
    @counter
    M=D         // counter = 8192

(NEXTPIXEL)
    // Ambil warna
    @color
    D=M
    
    // Warnai pixel di alamat saat ini
    @address
    A=M         // Pindah ke alamat pixel (misal 16384)
    M=D         // Tulis warna ke sana

    // Increment Address (Pindah ke pixel sebelah)
    @address
    M=M+1

    // Decrement Counter (Kurangi sisa pixel)
    @counter
    M=M-1
    D=M

    // Cek apakah loop sudah selesai?
    @NEXTPIXEL
    D;JGT       // Jika counter > 0, ulangi loop

    // Jika selesai, balik ke awal cek keyboard lagi
    @RESTART
    0;JMP   