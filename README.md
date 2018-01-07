# fruit-rage
A game playing agent that does Adversarial Search using Minimax Algorithm with Alpha Beta Pruning. 


Description
-----------
"The Fruit Rage!" is a zero sum two player game with strict limitation on allocated time for reasoning. The software agent created in Python 2.7 can play this game against a human or another similar agent. The code has implementation of Minimax Algorithm with Alpha Beta Pruning for efficient game playing.

Complete project description can be found here:
https://drive.google.com/file/d/151ADWbXu1G9kZzLHu7KCwR8E7Ob03m14/view?usp=sharing


Input
-----
The program reads a text file "input.txt" in the current directory. This file contains the problem description in the format:

- First line:   Integer n, the width and height of the square board (0 < n <= 26)
- Second line:  Integer p, the number of fruit types (0 < p <= 9)
- Third line:   Strictly positive floating point number, the remaining time in seconds
- Next n lines: The n x n board, with one board row per input file line, and n characters (plus end-of-line marker) on each line. Each character can be either a digit from 0 to p-1, or a * to denote an empty cell.

An example "input.txt" and the corresponding "output.txt" are uploaded in the repository.


Output
------
Solution is written to "output.txt" in the current directory. The format is as follows:

- First line: The selected move, represented as two characters:
              (1) A letter from A to Z representing the column number (where A is the leftmost column, B is the next one to the right, etc)
              (2) A number from 1 to 26 representing the row number (where 1 is the top row, 2 is the row below it, etc).
- Next n lines: The n x n board just after the selected move and after gravity has been applied to make any fruits fall into holes created by the move taking away some fruits.

How to Run?
-----------
Needs Python 2.7 interpreter
> python fruitRage.py
