// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

    // 1. Inisialisasi Result (R2) jadi 0
    @2
    M=0     // R2 = 0

    // 2. Cek apakah R0 == 0?
    @0
    D=M
    @END
    D;JEQ   // Jika R0 = 0, lompat ke END (Hasil tetap 0)

    // 3. Cek apakah R1 == 0?
    @1
    D=M
    @END
    D;JEQ   // Jika R1 = 0, lompat ke END (Hasil tetap 0)

(LOOP)
    // 4. Tambahkan R0 ke R2
    @0
    D=M     // Ambil nilai R0
    @2
    M=D+M   // R2 = R2 + R0

    // 5. Kurangi Counter (R1)
    @1
    M=M-1   // R1 = R1 - 1
    D=M     // Simpan nilai R1 yang baru ke D untuk dicek

    // 6. Cek apakah masih perlu looping?
    @LOOP
    D;JGT   // Jika R1 > 0, ulangi loop

(END)
    @END
    0;JMP   // Infinite loop untuk mengakhiri program