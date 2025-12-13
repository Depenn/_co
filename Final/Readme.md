# Hack Computer Software Hierarchy (Nand2Tetris Projects 6-12)

**Implementation of a modern software compiler and operating system hierarchy atop the Hack hardware platform.**

This section of the repository focuses on the *Nand2Tetris* Part II software stack. Having built the hardware in Part I, this phase bridges the gap between the bare metal machine language and high-level object-oriented programming. The stack is built layer-by-layer, including a custom Assembler, a Virtual Machine backend, a Compiler for the Jack language, and a standard Operating System library.

## Software Stack Overview

The software hierarchy transforms high-level abstractions into executable binary:
* **High-Level Language (Jack):** An object-oriented, Java-like language with static typing.
* **Virtual Machine (VM):** A stack-based architecture that abstracts the underlying hardware implementation, allowing for two-tier compilation.
* **Assembly Language:** Symbolic representation of the machine instructions (`@value`, `D=M+1`, etc.).
* **Binary Code:** The final 16-bit instructions executed by the Hack CPU constructed in Part I.

## Modules Breakdown

### Project 6: The Assembler
**Goal:** Develop a program to translate symbolic Hack Assembly (`.asm`) into binary machine code (`.hack`).
* **Symbol Handling:** Implemented a symbol table to manage predefined symbols, labels (loops/jumps), and variables.
* **Translation:** Parses A-instructions (addressing) and C-instructions (computation) into their corresponding 16-bit binary format.
* **Result:** Enables writing software using human-readable symbols instead of raw binary.

### Project 7 & 8: Virtual Machine Translator
**Goal:** Build a backend translator that converts stack-based VM code into Hack Assembly.
* **Stack Arithmetic:** Implemented push/pop operations, logical comparisons (`eq`, `gt`, `lt`), and arithmetic (`add`, `sub`, `neg`).
* **Memory Access:** Mapped VM memory segments (`local`, `argument`, `this`, `that`, `temp`) to the host RAM.
* **Program Control:** Implemented branching (`label`, `goto`, `if-goto`) and function call/return protocols to support recursion and stack frame management.

### Project 9: High-Level Language Application
**Goal:** Create an interactive application or game using the Jack programming language to test the system.
* **Application:** *[Catch Fruit]*.
* **Features:** Demonstrates standard library usage, graphical output, and user input handling on the Hack platform.

### Project 10: Compiler I (Syntax Analysis)
**Goal:** Build the front-end of the Jack Compiler (Tokenizer and Parser).
* **Tokenizer:** Breaks raw Jack source code into a stream of meaningful tokens (keywords, identifiers, symbols).
* **Parser:** Analyzes the grammatical structure of the token stream based on the Jack language grammar (LL(1)).
* **Output:** Generates a structured XML representation of the code (Parse Tree) for debugging and logic verification.

### Project 11: Compiler II (Code Generation)
**Goal:** Build the back-end of the Jack Compiler to generate executable VM code.
* **Symbol Table:** Manages identifier scope (class-level vs. subroutine-level) and type information.
* **Code Generation:** Traverses the parse tree and emits the corresponding VM stack commands.
* **Object Handling:** Manages object construction (`new`), method calls, and array manipulation.

### Project 12: The Operating System
**Goal:** Develop the standard library (API) for the Jack language to bridge software and hardware.
* **Mathematical Operations:** Efficient implementation of multiplication, division, and square root (as the ALU only supports addition/subtraction).
* **Memory Management:** Implemented `Memory.alloc` and `Memory.dealloc` (heap management) using a free-list algorithm.
* **Drivers:** `Screen` (raster graphics drawing), `Keyboard` (input handling), `Output` (bitmap font rendering), and `String` manipulation.

## Technology & Tools

* **Implementation Language:** Python / Java / C++ (Used to build the Assembler & Compiler tools).
* **Jack Language:** The high-level object-oriented language designed for this course.
* **VM Emulator:** Visualizes the stack-based execution of the intermediate code.
* **CPU Emulator:** Simulates the final binary execution on the Hack architecture.

## How to Run

1.  **Assembler:** Run the custom assembler script on an `.asm` file to generate `.hack`.
2.  **VM Translator:** Run the translator on `.vm` files to generate `.asm`.
3.  **Jack Compiler:** Pass a directory of `.jack` files to the compiler to generate `.vm` files.
4.  **Simulation:** Use the **VM Emulator** to run the compiled `.vm` code or the **CPU Emulator** to run the final assembled `.hack` code.

---
*Developed by 林順義.*