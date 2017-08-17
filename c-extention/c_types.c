
#include <stddef.h>
#include <string.h>
#include <stdlib.h>

/* typedef cause the compiler to add NewType to the list
 * of type names that it recognizes. The NewType can be
 * used in the same way as the built-in type. */

typedef int NewType;


/*****************************************************************************
 *                            integer
 ****************************************************************************/

void type_int(void){

    /* the word int may be optional. The order of the
     * specifiers does not matter. 
     *
     * C standard requires that short int, int and long
     * int each cover a certain minimum range of values.
     * It also requires that int should not be shorter
     * than short int, and similar for long and int
     *
     * One way to determine the ranges of the integer
     * types for a particular implementation is to check
     * the <limit.h> header.*/
    short int a;
    unsigned short b;

    int c;
    unsigned d;
    long e;
    unsigned long f;

    /* C99 provides two additional integer types, 
     * long long int and unsigned long long in. It also
     * support implementation-defined extended integer
     * types. */
    long long g;

    /* decimal contant must not begin with a zero. If type
     * is not specify, the compiler try to store it in int,
     * long, and then unsigned long. */
    c = 789;
    e = 789L;              /* force to long */
    d = 789U;              /* force to unsigned */
    
    /* octal contant must begin with a zero. If the type
     * if not specify, compiler will go through int, 
     * unsigned int, long,and unsigned long. */
    c = 0123;

    /* hexadecimal contant always begin with 0x. The type
     * determination is similar to octal contant. */
    c = 0xab;

    /* When overflow occurs during an operation on signed
     * integers, the behavior is undefined. For unsigned
     * integers, the higher bits is truncated. */
    a = c*1000;
}

void logical(void){

    /* C99 provides the _Bool type. This is an unsigned
     * integer type, and will only store 0 and 1. In
     * addition, <stdbool.h> providers more things. */
    _Bool flag;

}


/*****************************************************************************
 *                            float
 ****************************************************************************/
void type_float(void){

    /* The C standard doesn't state how float and double
     * is stored. Most modern computers follow the
     * specification in IEEE Standard 754 (IEC 60559) */

    float a;
    double b;

    /* by defalut, floating contants are stored as double.*/
    b = 75.;
    b = 7.5e1;
    b = 0.75e2;
}

/*****************************************************************************
 *                            character
 ****************************************************************************/

void type_character(void){

    char a;
    int i;

    /* C standard doesn't specify whether ordinary char
     * is signed or unsigned.*/
    signed char b;
    unsigned char c;

    a = 'a';

    /* C treats characters as small integers. When a
     * character appears in a computation, C simply uses
     * its integer value.  */
    i = 'a';
    i = a;
    a = i + 1;
    a++;
    i = a <= 'b' && a <= 20;    /* may not be portable.*/

    a = '\n';                   /* escape */
    a = '\22';                  /* octal value */
    a = '\x1b';                 /* hexadecimal value */
}


/*****************************************************************************
 *                            string
 ****************************************************************************/
void type_string(void){

    /* no extra string type, use pointer or array instead.
    * The string stored in array can be changed. The
    * string literal pointed by a pointer can not be
    * changed. */
    char *p, ch;
    char s1[8] = "hello";   /* valid only in initializing*/

    p = "abc";
    ch = "abc"[0];


    /* An octal escape ends after three digits or with
     * the first non-octal character. A hexadecimal escape
     * doesn't end until the first non-hex character.*/
    p = "/1234";                  /* /123 and 4 */
    p = "/189";                   /* /1, 8 and 9 */
    p = "/xfcber";                /* /xfcbe and r */

    /* when two or more string literals are adjacent, the 
    * compiler will join them into a single string. */
    p = "hello "  "world";

}


/*****************************************************************************
 *                            array
 ****************************************************************************/
void type_array(void){

    /* one-dimensional array*/
    int a[10];
    int b[5] = {1, 2, 3, 4, 5};
    int c[5] = {1};
    int d[ ] = {1, 2, 3, 4, 5};

    /* C99 support designated initializers */
    int e[15] = {[2]=1, [14]=1, [9]=1};
    int f[ ] = {[2]=1, [15]=1};        /* length = 16 */
    int g[ ] = {1, 2, [6]=3, 4, [11]=1}; 

    /* get size */
    size_t len = sizeof(a) / sizeof(a[0]);

    /* the content of the array can not be modified,
     * the compiler will check it */
    const char c_1[] = {'a', 'b', 'c'};

    /* multidimensional array. C stores it in row-major
     * order. */
    int aa[3][3] = {{1, 1, 1},
                    {1, 1, 1},
                    {1, 1, 1}};
    int bb[3][3] = {{1, 1, 1},
                    {1, 1, 1}};
    int cc[3][3] = {{1, 1, 1},
                    {1},
                    {1}};
    int dd[3][3] = {1, 1, 1, 1, 1};
    int ee[3][3] = {[0][0]=1, [1][1]=1};

}


/*****************************************************************************
 *                            pointer
 ****************************************************************************/
void type_pointer(void){

    int i = 0, a[10] = {0}, aa[4][3] = {0}, r;
    int *p, *q;            /* declare a pointer */
    int (*pp)[3];
    p = &i;                /* address of i */
    i = *p;                /* get content */
    *q = i;                /* change content */


    /* point arithmetic, meaningful only when used with
     * array. */
    p = &a[0];
    q = &a[3];
    r = *(p + 3) == a[3];
    r = *(q - 3) == a[0];
    r = q - p == 3;
    r = p > q;

    /* the name of an array can be used as a pointer to
     * the first element in the array, but it can't be
     * changed. */
    *a = 0;
    *(a+1) = 1;
    r = p < a+1;
    p = a, p++;           /* valid */

    /* For multidimensional array, it is similar.
     * aa is a pointer to an array, not a pointer to a pointer */
    pp = aa;
    p = aa[0];            /* treated as one dimensional array */
    p = aa[1];
    p = &aa[1][0];        /* point to the second row*/

    /* a pointer can be used as an array name*/
    p = a;
    i = p[0];             /* valid */

    /* &a[10] is valid since it doesn't evaluate the
     * value. ++ takes precedence over *. */
    p = &a[0];
    while (p < &a[10])
        i += *p++;

    /* with C99 compound literal */
    p = (int []){1, 2, 3};
    
}


/*****************************************************************************
 *                            struct
 *   struct {...} specifies a type.
 *   The members of a struct are stored in memory in the order in which they're
 * declared. There are no gaps between the numbers. Each struct has a seperate
 * namespace for its members.
 ****************************************************************************/

/* use structure tag to identify a particular kind of
 * structure. Structure tags aren't recognized unless
 * preceded by the word struct, and they don't conflict
 * with other names used in a program.  */
struct st_type1 {
    int number;
    char name[10];
};

struct st_type1 s1, s2;

/* use typedef to define a new type. */
typedef struct {
    int number;
    char name[10];
} st_type2;

st_type2 s3, s4;

void type_struct(void){

    int i;
    st_type2 s5 = {1, "Hello"};      /* like array */

    /* An initializer can have fewer members than the structure
     * it's initializing; as with arrays, any “leftover‟‟ members
     * are given 0 as their initial value.*/
    st_type2 s6 = {1};

    /* C99 support designated initializers */
    st_type2 s7 = {.number = 1, .name="hello"};

    /* The members of a structure are lvalues */
    i = s7.number;
    s7.number = 10;

    /* copy using =. An array embedded within a structure is
     * copied when the enclosing structure is copied.  */
    s7 = s6;

    /* C99 support compound literal */
    s7 = (st_type2) {1, "hello"};

}

/*****************************************************************************
 *                              union
 *   A union consists of one or more members, possibly of different types.
 * However, the compiler allocates only enough space for the largest of the
 * members,
 *   It's not a good idea to store a value into one member of a union and then
 * access the data through a different member. However, the C standard mentions
 * a special case: two or more of the members of the union are structures, and
 * the structures begin with one or more matching members.
 ****************************************************************************/

struct catalog_item {
    int stock_number;
    double price;
    int item_type;
    union {
        struct {
            char title[20];
            char author[20];
            int num_pages; } book;
        struct {
            char design[40]; } mug;
        struct {
            char design[40];
            int colors;
            int sizes;} shirt;
    } item;
};

typedef struct {
    int kind;
    union {
        int i;
        double d;
    } u;
} Number;

void type_union(void){

    char *p;
    /* mixed data structure */
    Number number_array[1000];

    struct catalog_item c1, c2;
    strcpy(c1.item.mug.design, "Cats");
    p = c1.item.shirt.design;   /* valid */

}


/*****************************************************************************
 *                              enum
 *   Behind the scenes, C treats enumeration variables and constants as 
 * integers. We're free to choose different values for enumeration constants if
 * we like.
 *   The names of enumeration constants must be different from other identifiers
 * declared in the enclosing scope. Enumeration constants are subject to C's
 * scope rules: if an enumeration is declared inside a function, its constants
 * won't be visible outside the function.
 ****************************************************************************/

enum suit {CLUBS, DIAMONDS, HEARTS, SPADES};
enum dept {RESEARCH = 20, PRODUCTION = 10, SALES = 25};

void type_enum(void){

    enum suit s1;
    s1 = CLUBS;
    s1 = 1;
    s1++;
}

/*****************************************************************************
 *                             others
 ****************************************************************************/

void dynamic_memory(void){

    void *p1;                   /* "generic" pointer*/
    void *p2 = NULL;            /* NULL is a macro */

    /* allocate space for a string. Not cleared or
     * initialized. Type cast is optimal. */
    char *s1 = (char *) malloc(20);

    /* a list of int. */
    int *a1 = malloc(20*sizeof(int));

    /* all bits set to 0 */
    int *a2 = calloc(20, sizeof(int));

    void *r;

    /* Expanded memory block will not be initialized.
     * If failed, old memory is unchanged, return NULL.
     * If the first argument is NULL, behaves like malloc.
     * If the second argument is 0, then free the memory */
    r = realloc(a1, 15);       /* smaller */
    r = realloc(a2, 25);       /* larger */

    if (p2) {
        /* All non-null pointers test true; only null
         * pointers are false.*/
        ;
    }

    free(s1);
    free(a1);
    free(a2);
}


void type_size(void){

    int a;
    size_t len;

    len = sizeof(int);
    len = sizeof(a);
    len = sizeof(a + 1);
    len = sizeof(1 + 1);
}


void type_conversion(void){

    /* Implicit conversion are performed in the following
     * situations:
     *   1. When the operand in an arithmetic or logical
     * expression don't have the same type.
     *   2. When the type of the expression on the right
     * side of an assignment doesn't match the type of the
     * variable on the left side.
     *   3. When the type of argument in a function does
     * not match the type of the corresponding parameters.
     *   4. When the type of expression in a return statement
     * doesn't match the function's return type.
     * */


    /* The strategy behind the usual arithmetic conversions
     * is to convert operands to the “narrowest” type that
     * will safely accommodate both values.
     * 
     * When a signed operand is combined with an unsigned 
     * operand, the signed operand is converted to an 
     * unsigned value.*/


    /* For assignment, C follows the simple rule that the
     * expression on the right side of the assignment is 
     * converted to the type of the variable on the left
     * side.*/

    /* For argument conversion, if the compiler has 
     * encountered a prototype prior to the call, the 
     * conversion is like assignment. If not, the compiler
     * performs the default argument promotions: float are
     * converted to double, integral promotions are
     * performed. */

    ;
}


int main(void){
    ;
}
