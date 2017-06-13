
#include <stdio.h>

/*****************************************************************************
                                declaration
 *   By declaring variables and functions, we furnish vital information that the
 * compiler will need in order to check a program for potential errors and
 * translate it into object code. In general, a declaration has the following
 * appearance:
       declaration-specifiers declarators;
 *   Declaration specifiers describe the properties of the variables or
 * functions being declared. These specifiers fall into four categories:
       1 Storage classes. There are four storage classes: auto,
         static, extern, and register. At most one storage class
         may appear in a declaration; if present, it should come
         first.
       2 Type qualifiers. In C89, there are only two type of
         qualifiers: const and volatile. C99 has a third type
         qualifier, restrict. A declaration may contain zero or
         more type qualifiers.
       3 Type specifiers. The keywords void, char, short, int,
         long, float, double, signed, and unsigned are all type
         specifiers. The order in which they appear doesn't
         matter. Type specifiers also include specifications
         of structures, unions, and enumerations.
       4 function specifier. Only in C99, used only in function
         declaration. This category has just one member, the
         keyword inline.
 *   Declarators include identifiers (names of simple variables), identifiers
 * followed by [] (array names), identifiers preceded by * (pointer names), and
 * identifiers followed by () (function names). Declarators are separated by
 * commas. A declarator that represents a variable may be followed by an
 * initializer.
 *   A variable can have many declarations in a program but should have only one
 * definition.

                           Properties of Variables
 *   Every variable in a C program has three properties:
       1 Storage duration. The storage duration of a variable
         determines when memory is set aside for the variable and
         when that memory is released. Storage for a variable with
         automatic storage duration is allocated when the
         surrounding block is executed, and is deallocated when
         the block terminates. A variable with static storage
         duration stays at the same storage location as long as
         the program is running.
       2 Scope. The scope of a variable is the portion of the
         program text in which the variable can be referenced. A
         variable can have either block scope (the variable is
         visible from its point of declaration to the end of the
         enclosing block) or file scope.
       3 Linkage. The linkage of a variable determines the extent
         to which it can be shared by different parts of a program.
         A variable with external linkage may be shared by several
         files in a program. A variable with internal linkage is
         restricted to a single file, but may be shared by the
         functions in that file. A variable with no linkage belongs
         to a single function and can't be shared at all.
 *   Variables declared inside a block (including a function body) have
 * automatic storage duration, block scope, and no linkage. Variables declared
 * outside any block, at the outermost level of a program, have static storage
 * duration, file scope and external linkage.
 ****************************************************************************/

/* static storage, file scope, external linkage.
 * Visible from its point of declaration to the end of
 * enclosing file.
 */
int outer1 = 1;
extern int outer2 = 1;

/* static storage, file scope, internal linkage. */
static int outer3 = 1;

/* extern storage, file scope, external linkage. */
extern int outer4;


void func1(void){
    /* auto storage, block scope, no linkage.
     * It is visible from its point of declaration to the
     * end of the enclosing function body. */
    float var_f1, tmp;
    /* With initializer. A good style that appending type
     * information to a constant */
    float var_f2 = 2017.5f;
    /* hide the external varibale*/
    int outer1;

    /* static storage, block scope, no linkage.
     * Initialized only once, prior to program execution.*/
    static float var_f3 = 1;

    /* register storage.
     * can not refer the address. */
    register int var_f4;

    if (1) {
        /* BLOCK SCOPE, hide the outer tmp*/
        int tmp = 1;
    }

    /* In C99, the first expression in a for statement can be
     * replaced by a declaration. Compiler will allocate a new
     * address for it, and it is not visible outside the
     * loop. */
    for (int i = 5; i > 0; i--){
        ;
    }
}

/* external linkage */
void func2(void);
extern void func3(void);

/* internal linkage */
static void func4(void);

/*   Always read declarators from the inside out. In other
 * words, locate the identifier that‟s being declared, and
 * start deciphering the declaration from there.
 *   When there's a choice, always favor [] and () over *.
 */
int *ap[10];             /* array of pointer */
float *func5(float);     /* function */
void (*pf)(int);         /* pointer to function */
int *(*apf[10])(void);   /* array of pointer to function */

/*****************************************************************************
 *                        operaotors and expression
 ****************************************************************************/

void arithmetic(void){
    int a=5, b=-2, c=7;

    /* In C89, the result depends on the implementation.
     * In C99, the result of a division is always truncated
     * toward zero, and the value of i % j has the same sign
     * as i.
     */
    a = b/c;
    a = b%c;

    /* assignment is an operator. The value of v=e is the
     * value of v after the assignment. This is an example
     * of expression's side effect: evaluation a=1 produce
     * the result 1, and assigning 1 to a is a side effect.
     */
    if (a==1)
        ;

    /* C doesn't define the order in which subexpressions
     * are evaluated. If the subexpressions have side effects,
     * the result depends on how compiler evaluate the
     * subexpressions.
     */
    c = (b = a+2) - (a = 1);

    /* any expression can be used as a statement */
    a++, a;

    /* comma expression. Subexpression is evaluated from left
     * to right. The value of the expression is the value of
     * the last subexpression */
    a, b;

}

/*****************************************************************************
 *                        selection statement
 ****************************************************************************/

void statement_if(void){

    int a=1, b=2;

    /* The parentheses are part of the if statement, not
     * part of the expression. */
    if (a == b)
        /* expect a single statement; */
        ;

    if (a == b){
        /* treat compound statement as single statement*/
        ;
    } else
        ;

    /* C follows the rule that an else clause belongs to the
     * nearest if statement that hasn't already been paired
     * with an else.*/
    if (a == b)
        ;
    else if (a > b)
        ;
    else
        ;
}

void statement_switch(void){

    int grade = 0;

    /* the controlling expression should generate an integer.
     * Character can by tested, but not float or string. */
    switch (grade){
    /* constant expression is required, not variables or
     * function call. Duplicate case labels aren't allowed.
     * The order of the case dosen't matter. */
    case 4: 
        /* any number of statements. no braces are required. */
        printf("4");
        break;
    case 3: 
        printf("3");
        break;
    case 2:
    case 1:
        /* switch statement is really a form of jump. If no
         * break, the following statements in other case
         * or default will be executed.*/
        printf("2 or 1");
    /* default case doesn't need to come last. Defalut case
     * can be missing. */
    default:
        printf("unknown");
        break;
    }

}


/*****************************************************************************
 *                         loop statement
 ****************************************************************************/

void statement_loop(void){

    int i;

    /* has the same effect as the following while statement */
    for (i = 10; i > 0; i--){
        ;
    }

    i = 10;
    while (i > 0){
        i--;
    }

    i = 10;
    do {
        i--;
    } while (i > 0);


    /* junp inside a function. In C99, goto can not bypass the
     * declaration of a viriable-length array. */
    goto done;
    i = 10;   /* skipped */

    done:
    return;
}

/*****************************************************************************
 *                         scope rule 
 *   In C99, selection statements (if and switch) and iteration statements
 * (while, do, and for), along with the "inner" statements that they control,
 * are considered to be blocks.
 ****************************************************************************/



int main(void){
    printf("hello world.\n");

    /* if no return statement exist, the compiler will 
     * complain about it. */
    return 0;
}

/*
 * conversion specification: %m.pX 
 *
 * m
 *   The minimum field width, integer. Specifying the minimum number of
 * characters to print. Right-justified by default. If m is negative, then 
 * Left-justified is applied.
 *
 * X
 *   d, display an integer in decimal form. p indecates the minimum number of
 * digits to display, and extra zeros may be added.
 *   e, display a floating-point number in exponential format. p indicates how
 * many digits should appear after the dicimal point. The default is 6.
 *   f, display a floating-point number in fixed decimal format. p has the same
 * meaning as for the e specifier.
 *   g, display a floating-point number in either exponential format of fixed
 * decimal format, depending on the number's size. p indicate the maximum number
 * of significant digits to be display.
 *   u, unsigned integer.
 *   o, unsigned integer in actal.
 *   x, unsigned integer in hexadecimal.
 *   c, single char.
 *   hd, hu, ho, hx, short.
 *   ld, lu, lo, lx, long.
 *   le, lf, lg, double.
 *   Le, Lf, Lg, long double.
 *
 */
