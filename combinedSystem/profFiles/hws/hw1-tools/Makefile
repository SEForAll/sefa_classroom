GCC=gcc
CFLAGS=-std=c99 -g -Wall -Wshadow --pedantic -Wvla -Werror
EXEC = sort
TESTFLAGS = -DASCENDING

sort: main.c sort.c
	$(GCC) $(CFLAGS) -o $(EXEC) main.c sort.c
	
# Fix the gcc command for the target ascending by fill in the missing part
ascsort: main.c sort.c
	$(GCC) $(CFLAGS) $(TESTFLAGS)  -o $(EXEC) main.c sort.c
	
testall: test1 test2 test3 test4 test5 test6

test1: sort
	./sort inputs/test1 > output1
	diff output1 expected/expected1 > grade.txt

test2: sort
	./sort inputs/test2 > output2
	diff output2 expected/expected2 > grade.txt

test3: sort
	./sort inputs/test3 > output3
	diff output3 expected/expected3 > grade.txt

test4: ascsort
	./ascsort inputs/test1 > output4
	diff output4 expected/expected4 > grade.txt

test5: ascsort
	./ascsort inputs/test2 > output5
	diff output5 expected/expected5 > grade.txt

test6: ascsort
	./ascsort inputs/test3 > output6
	diff output6 expected/expected6 > grade.txt


testfor: sort  # same as testall
	for case in 1 2 3; do \
	echo $$case; \
	./sort inputs/test$$case > output$$case; \
	diff output$$case expected/expected$$case; \
	done

clean: # remove all machine generated files
	rm -f sort *.o output?
	
clean:
	rm -f $(EXEC)
	rm -f *.o