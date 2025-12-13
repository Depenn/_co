# Hack Computer Hardware Implementation (Nand2Tetris Projects 1-5)

**Implementation of a 16-bit Von Neumann computer architecture starting from a single NAND gate.**

This repository contains the hardware logic layer constructed as part of the *Nand2Tetris* (The Elements of Computing Systems) course. The system is built from the ground up, starting with elementary logic gates, progressing to an Arithmetic Logic Unit (ALU), memory systems (RAM), and culminating in a fully functional CPU and Computer capable of running machine language.

## Architecture Overview

The Hack computer is a 16-bit architecture consisting of:
* **Data Bus:** 16-bit.
* **Address Space:** 15-bit addressing (32K words).
* **CPU:** Performs 16-bit ALU operations and handles instruction decoding (A-instruction & C-instruction).
* **Memory:** Separate Instruction Memory (ROM) and Data Memory (RAM) - Harvard Architecture externally, but functions as Von Neumann internally regarding the program counter logic.

## Modules Breakdown

### Project 1: Boolean Logic
**Goal:** Build elementary logic gates using only `NAND`.
* **Elementary:** `Not`, `And`, `Or`, `Xor`, `Mux`, `DMux`.
* **16-bit Variants:** `Not16`, `And16`, `Or16`, `Mux16`.
* **Multi-Way Variants:** `Or8Way`, `Mux4Way16`, `Mux8Way16`, `DMux4Way`, `DMux8Way`.
* *Key Challenge:* Optimizing gate count and understanding the universality of the NAND gate.

### Project 2: Boolean Arithmetic & ALU
**Goal:** Implement binary addition and the core Arithmetic Logic Unit.
* **Adders:** `HalfAdder`, `FullAdder`, `Add16`, `Inc16`.
* **The ALU:** A combinational chip that computes a function on two 16-bit inputs. It supports 18 different functions controlled by 6 control bits (`zx`, `nx`, `zy`, `ny`, `f`, `no`) and outputs status flags (`zr`, `ng`).


### Project 3: Sequential Logic (Memory)
**Goal:** Introduce state/time preservation using Data Flip-Flops (DFF).
* **Basic Memory:** `Bit` (1-bit register), `Register` (16-bit).
* **RAM:** `RAM8`, `RAM64`, `RAM512`, `RAM4K`, `RAM16K`. Recursive construction of memory banks.
* **Program Counter (PC):** A 16-bit counter with load, increment, and reset functionalities essential for the fetch-execute cycle.

### Project 4: Machine Language (Assembly)
**Goal:** Write low-level Assembly software to test the hardware's capabilities before the CPU is even built.
* **Mult.asm:** Performs multiplication (which is not native to the Hack ALU) using a loop-based addition algorithm ($O(n)$ complexity).
* **Fill.asm:** I/O interaction test. Listens to the keyboard memory map and manipulates the screen memory map to black out or clear the screen. Demonstrates direct memory access (DMA) concepts.

### Project 5: Computer Architecture
**Goal:** Integrate all previous chips into a functioning computer.
* **Memory.hdl:** Composes RAM16K, Screen memory map, and Keyboard memory map into a single addressable unit.
* **CPU.hdl:** The brain. Decodes instructions, routes data to the ALU or Registers (A/D), and manages the Program Counter based on jump conditions.
* **Computer.hdl:** The top-level chip connecting the ROM (Instruction Memory), CPU, and RAM (Data Memory).


## Technology & Tools

* **HDL (Hardware Description Language):** Used to define the chip logic and wiring.
* **Hack Assembly:** Low-level symbolic language used for testing.
* **Hardware Simulator:** Java-based tool provided by Nand2Tetris to simulate the HDL and clock cycles.

## How to Run

1.  Ensure you have the **Nand2Tetris Software Suite** installed.
2.  Open the **Hardware Simulator** (`HardwareSimulator.bat` or `.sh`).
3.  Load the `.tst` file for the specific chip you want to verify (e.g., `projects/05/Computer.tst`).
4.  Run the simulation to verify the output against the compare file.

---
*Developed by 林順義.*