#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "sort.h"

/* Do not modify any of the code in this file. Only modify code in sort.c */

/* Return true if the input array is sorted.

   Parameters:
   arr: pointer to integer array
   size: size of array
   asc: true if array is supposed to be ascending, false if descending

   Returns:
   true if array is sorted, false otherwise
*/
bool isSorted(int * arr, int size, bool asc) {
	if (size == 1) return true; // if there is only one element, array is sorted
	
	for (int i = 1; i < size; i++) {
		if (asc) { //in ascending order
			if (arr[i - 1] > arr[i]) return false; //later element is smaller
		} else {
			if (arr[i - 1] < arr[i]) return false; //later element is bigger
		}
	}	
	return true;
}

/* Print out array

   Parameters:
   arr: pointer to integer array
   size: size of array
*/
void printArray(int * arr, int size) {
	for (int i = 0; i < size; i++) {
		fprintf(stdout, "%d ", arr[i]);
	}
	fprintf(stdout, "\n");
}

int main(int argc, char * * argv) {
	// read input file
    if (argc != 2) {
        fprintf(stderr, "need the name of input file\n");
        return EXIT_FAILURE;
    }
    
	// open file to read
    FILE * fptr = fopen(argv[1], "r"); 
    if (fptr == NULL) {
        fprintf(stderr, "fopen fail\n");
        // do not fclose (fptr) because fptr failed
        return EXIT_FAILURE;
    }
    
	// count the number of integers
    int value;
    int count = 0;
    
	while (fscanf(fptr, "%d", & value) == 1) {
        count ++;
    }
    fprintf(stdout, "The file has %d integers\n", count);
    
	// allocate memory to store the numbers
    int * arr = malloc(sizeof(int) * count);
    if (arr == NULL) {// malloc fail
        fprintf(stderr, "malloc fail\n");
        fclose (fptr);
        return EXIT_FAILURE;
    }
    
	// return to the beginning of the file
    fseek (fptr, 0, SEEK_SET);
    int ind = 0;
    while (ind < count) {
        if (fscanf(fptr, "%d", & arr[ind]) != 1) {
  	        fprintf(stderr, "fscanf fail\n");
  			fclose (fptr);
  			free (arr);
  			return EXIT_FAILURE;
  		}
        ind ++;
    }
    fclose(fptr);
	
	//Sort array
	ssort(arr, count);
	
	//conditional compilation: if ASCENDING defined, will sort ascending, otherwise descending
#ifdef ASCENDING
	bool asc = true;
#else
	bool asc = false;
#endif
	
	if (isSorted(arr, count, asc) == false) {
		fprintf(stdout, "array not sorted!");
	}
	
	printArray(arr, count);
	
	free(arr);
	return EXIT_SUCCESS;
}
