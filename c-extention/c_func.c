


/* Function can only return one value, can not return array.
 * Return struct is permitted. If the struct contains array,
 * the array will be copied, too.

 * Arguments are always passed by value.
 */

/* Without function prototype, the compiler will perform
 * the default argument promotions, which always is not
 * what we want, and will cause error later.  */
double func0(double a, double b);



/*****************************************************************************
 *                             const parameters
 *****************************************************************************/

/* the content that p points to can not be modified,
 * p itself can be changed(point to another int). */
void func11(const int *p);

/* p itself can not be changed. the content that p
 * points to can be modified. This feature isn't used
 * very often, since function pass arguments by value.
 * This may be useful in C++ pass by reference. */
void func12(int * const p);

/* the content of the array can not be changed. The
 * compiler will check that no assignment appears. */
int func22(const int a[], int len);

/* if passed in an array or string, the const will not
 * prevent the content be changed. */
int func23(const char *s);

/*****************************************************************************
 *                     array parameters and arguments
 *****************************************************************************/

/* When the parameter is a one-dimensional array, the 
 * length of the array can be left unspecified. But C
 * doesn't provide any easy for a function to  determine
 * the length.
 * 
 * Actually, when called, the pointer to the first element
 * of array is passed in. So, the content of the array can
 * be changed in the function.
 *
 * Further more, you can alse pass in a pointer to any
 * element of an array.
 * */
int func2(int a[], int len);
int func21(int *a, int len);         /* same effect */


/* When the parameter is multidimensional array, only 
 * the first dimension may be ommitted.
 */
int func3(int a[][5], int len);
int func31(int (*a)[5], int len);


/* C99 allow specify the array's length. For one dimensional
 * array, this does not provide additional error-checking.
 * It may be useful for multidimensional array.
 */
int func41(int n, int a[n]);
int func42(int n, int a[*]);
int func43(int, int a[*]);
int func44(int m, int n, int a[m], int b[n], int c[m+n]);
int func45(int m, int n, int a[m][n]);

/* C99 use static to specify the smallest allowed length.
 * This has no effect on the behavior of the program. It
 * just help compiler generating faster instructions.
 */
int func5(int a[static 3], int n);

/*****************************************************************************
 *                        function pointer
 *   When a function name isn't followed by parentheses, the C compiler produces
 * a pointer to the function instead of generating code for a function call.
 *****************************************************************************/
double func61(double (*f)(double, double), double a, double b);
void func62(double f(double, double), double a, double b){

    /* declare a pointer to a function */
    void (*pf1)(int);

    /* call function */
    f(a, b);
    (*f)(a, b);

}

/*****************************************************************************
 *                            inline function (C99)
 *   The word "inline" suggests an implementation strategy in which the compiler
 * replaces each call of the function by the machine instructions for the
 * function. This technique avoids the usual overhead of a function call,
 * although it may cause a minor increase in the size of the compiled program.
 *   Declaring a function to be inline doesn"t actually force the compiler to
 * "inline" the function, however. It merely suggests that the compiler should
 * try to make calls of the function as fast as possible, perhaps by performing
 * an inline expansion when the function is called.
 *****************************************************************************/


/*****************************************************************************
 *                             main
 *****************************************************************************/
/* argv[0] points to the name of the program. argv[1] through
 * argv[argc-1] are command-line arguments. argv[argc] is NULL.
 *
 * main should return 0 if the program terminates normally.
 */

int main(int argc, char *argv[]){
    return 0;
}
