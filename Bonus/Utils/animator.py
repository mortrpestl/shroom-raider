import os
import time


def __clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def __wait(seconds):
    time.sleep(seconds)


def load_in(input_str):
    input_str = input_str.split("\n")
    height = len(input_str)
    wave = []
    for i in range(height):
        temp = []
        for j in input_str[i]:
            temp.append("=" if j != " " else " ")
        wave.append("".join(temp))

    for i in range(height):
        __clear_terminal()
        for j in range(i):
            print(input_str[j])
        k = 0
        for line in range(i, min(height, i + 3)):
            match k:
                case 0:
                    print(wave[line])
                case 1:
                    print(wave[line].replace("=", "-"))
                case 2:
                    print(wave[line].replace("=", "."))
            k += 1

        __wait(0.2)


def main():
    test_str = r"""
          +#:                                                         
 .:..:-.  =#-:.:::   .--:.::      :::::      .::::.     :-.::  ::.::  
=*:   ..  +#=   .**.  *#: .=*-  -*:   -*-  .++.  .*+   +*.  -**=   +*:
*#+-:.    +#:    :#+  +#.  -#+ -#=     +#: *#     :#+ =#:    ##     #*
 :=++**=  +#:    -#+  +#.:-=-  =#-     =#: #*     .#* =#:    **    .#*
      ##. +#:   .*+.  *#.=#-   .**    .#+  =#:    =#: .#*    *#    +*.
==:..-=.  +*-  .=-   .+*: :*+:  .==..:=-    :+:..-+.   :++.  **   --  
                                         :                          
                                         ++.                          
           .==:.:-.    .==.     :==.    .-+*+:     .::.:=: :==:.:-.   
            ##.  =#-    .#*.    .#*   :+=.  =#=   =*:   .: .##   +*:  
            *#   =#=    :+*+    .#*  -#=     =#= =#-   .    #*   +#-  
            **.-=-:    :#.-#=   .#*  *#:     :#+ *#: ..:-   #*.-=-.   
            *# =#-    .*=..=#=   #*  -#+     +*. -#+        #* =#-    
           .+*: :*+:.:=:    =*-.:*+.  :++-::--    .=+-:::. :*+. :*+:  
"""
    load_in(test_str)


main()
