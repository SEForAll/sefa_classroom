GCC=gcc
CFLAGS=-std=c99 -g -Wall -Wshadow --pedantic -Wvla -Werror

all: main.c sort.c
	$(GCC) $(CFLAGS) -o sort main.c sort.c
	
#add ascending target here
ascending: main.c sort.c
	$(GCC) $(CFLAGS) -o sort main.c sort.c -DASCENDING

testall: test1 test2 test3 test4 test5 test6
	
test1: all
	./sort testcases/inp1 > output1
	diff output1 expected/out1
test2: all
	./sort testcases/inp2 > output2
	diff output2 expected/out2
test3: all
	./sort testcases/inp3 > output3
	diff output3 expected/out3
	
test4: ascending
	./sort testcases/inp1 > output4
	diff output4 expected/out4
test5: ascending
	./sort testcases/inp2 > output5
	diff output5 expected/out5
test6: ascending
	./sort testcases/inp3 > output6
	diff output6 expected/out6
	
clean:
	rm -f sort
	rm -f *.o
	rm -f output*
