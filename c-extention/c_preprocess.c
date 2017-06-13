
/* general rule
 *   1. Space can appear before #. Any space and tab can seperate the tokens in
 * a directive.
 *   2. Directive always end at the first new-line character, unless explicitly
 * continued using backslash.
 *   3. Comments may appear on the same line as a directive.
 *   4. A preprocessing directive doesn't take effect until the line on which
 * it appears. 
 */



/*****************************************************************************
 *                            file inclusion
 *   The #include directive tells the preprocessor to open a specified file and
 * insert its contents into the currenl file.
 *   Header file can include other header file. When a header file is included
 * more than one time, error may occur.
 ****************************************************************************/

/* use angle bracket to include files that belong to C's own
 * library. Make compiler search the directories in which
 * system header files reside. */
#include <>

/* include files that not belong to C's own library. Make
 * compiler search corrent directory first. */
#include "utils.h"
#include "../utils.h"

#if defined IA32
  #define CPU_FILE "ia32.h"
#elif defined AMD64
  #define CPU_FILE "amd64.h"
#endif

#include CPU_FILE

/*****************************************************************************
 *                           macro definition
 *   A macro definition normally remains in effect until the end of file in
 * which it appears.
 *   A macro may not be defined twice unless the new definition is identical
 * to the old one.
 ****************************************************************************/

/* simple macro */
#define PI  3.14

/* For parameterized macros, there must no space between the
 * macro name and the left parenthesis. Parenthesises for 
 * parameters are required. Parameters may be empty, making
 * macro like a function.
 */
#define MAX(x, y)    ((x)>(y)?(x):(y))
#define IS_EVEN(n)   ((n%2==0))
#define getchar()    getc(stdin)

/* A macro's replacement list may contain other macros */
#define TWO_PI  (2*PI)

/* remove a macro. No effect if macro not defined.*/
#undef PI

/* # operator converts a macro argument into a string,
 * literal. It can appear only in the replacement list of a
 * parameterized macro.
 */
#define PRINT_INT(n)  printf(#n " = %d\n", n)

/* ## operator can "paste" two tokens together to form a
 * single token.
 */
#define MK_ID(n)  i##n
int MK_ID(1);                  /* int i1; */

/* predefined macros */
__LINE__;         /* line number */
__FILE__;         /* name of file */
__DATE__;         /* date of compilation */
__TIME__;         /* time of compilation */
__STDC__;         /* 1 if the compiler conforms to C89 or C99 */

/*****************************************************************************
 *                         conditional compilation
 ****************************************************************************/

#define DEBUG 1

#if DEBUG
int i = 0
#endif

/* undefined identifier is treated as macro that have
 * the value 0 */
#if AAA
#endif


/* defined is normally used in conjunction with #if */
#if defined AAA
#endif

#ifdef
#endif

#ifndef
#endif

/* #elif and #else can be used with #if, #ifdef, #ifndef*/
#if
#elif
#else

/* If the preprocessor encounters an #error directive, it
 * prints the following message. Frequently used in conjunction
 * with conditional compilation to check for situations that
 * shouldn't arise during a normal compilation. */
#if INT_MAX<10000
#error int type is too small
#endif



