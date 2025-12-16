# Nand2Tetris Projects 1-5 Report (Hardware)
**Student:** 林順義 (111310521)
**Date:** 2025/12/16

---

## ⚠️ 誠實聲明 (Declaration of Originality)

**總結 (Summary):**
本專案 (Project 1 - Project 5) 的所有程式碼 (HDL & Assembly) 皆為**本人原創撰寫 (100% Original)**。
我完全理解每一行程式碼的邏輯，未使用 AI 生成，也未複製他人作業。

---

## 詳細章節說明 (Module Breakdown & Status)

### Project 1: Boolean Logic
* **狀態 (Status):** **全部原創 (All Original)**.
* **內容 (Content):** Built elementary logic gates (`And`, `Or`, `Xor`, `Mux`, `DMux`) using only `NAND`.
* **理解 (Note):** I optimized the gate logic manually to ensure efficiency.

### Project 2: Boolean Arithmetic & ALU
* **狀態 (Status):** **全部原創 (All Original)**.
* **內容 (Content):** Implemented `HalfAdder`, `FullAdder`, `Inc16`, and the `ALU`.
* **理解 (Note):** I implemented the ALU control bits (`zx`, `nx`, `zy`, etc.) strictly following the truth table logic.

### Project 3: Sequential Logic (Memory)
* **狀態 (Status):** **全部原創 (All Original)**.
* **內容 (Content):** Built `Register`, `RAM8` through `RAM16K`, and the `PC` (Program Counter).
* **理解 (Note):** Constructed the memory hierarchy recursively.

### Project 4: Machine Language (Assembly)
* **狀態 (Status):** **全部原創 (All Original)**.
* **內容 (Content):**
    1.  `Mult.asm`: Implemented multiplication using a loop-based addition algorithm.
    2.  `Fill.asm`: Implemented screen manipulation by listening to the keyboard memory map.

### Project 5: Computer Architecture
* **狀態 (Status):** **全部原創 (All Original)**.
* **內容 (Content):**
    1.  `Memory.hdl`: Integrated RAM and Memory Mapped I/O.
    2.  `CPU.hdl`: Implemented instruction decoding, ALU control, and jump logic.
    3.  `Computer.hdl`: Connected ROM, CPU, and RAM.

---

## Architecture Overview (My Implementation)

The Hack computer is a 16-bit architecture consisting of:
* **Data Bus:** 16-bit.
* **Address Space:** 15-bit addressing (32K words).
* **CPU:** Performs 16-bit ALU operations and handles instruction decoding.
* **Memory:** Separate Instruction Memory (ROM) and Data Memory (RAM).

## How to Run

1.  Ensure you have the **Nand2Tetris Software Suite** installed.
2.  Open the **Hardware Simulator** (`HardwareSimulator.bat` or `.sh`).
3.  Load the `.tst` file for the specific chip (e.g., `projects/05/Computer.tst`).
4.  Run the simulation to verify the output against the compare file.

---
*Developed by 林順義 (111310521).*
