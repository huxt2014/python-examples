
/*
REFERENCE COUNTS

    Nobody “owns” an object; however, you can own a reference to an object. The
owner of a reference is responsible for calling Py_DECREF() when the reference
is no longer needed. 

    Ownership of a reference can be transferred. There are three ways to dispose 
of an owned reference: pass it on, store it, or call Py_DECREF().

    It is also possible to borrow a reference to an object. The borrower of a 
reference should not call Py_DECREF(). The borrower must not hold on to the 
object longer than the owner from which it was borrowed. A borrowed reference 
can be changed into an owned reference by calling Py_INCREF().

    Almost all Python objects live on the heap: you never declare an automatic
or static variable of type PyObject, only pointer variables of type PyObject*
can be declared. The sole exception are the type objects; since these must never
be deallocated, they are typically static PyTypeObject objects.


FUNCTION

    For module function, the first parameters passed in will always be NULL or
a pointer selected while initializing the module. The second parameters passed
in will always be a tuple.

    When a C function is called from Python, it borrows references to its
arguments from the caller. 

    When you pass an object reference into another function, in general, the 
function borrows the reference from you, for example, PyArg_Parse* functions. 
There are exactly two important exceptions to this rule: PyTuple_SetItem() and 
PyList_SetItem(). These functions take over ownership of the item passed to
them, even if they fail! 

    Most functions that return a reference to an object pass on ownership with
the reference. Many functions that extract objects from other objects also
transfer ownership with the reference.


METHOD
*/




/*
    All function, type and macro definitions needed to use the Python/C API are
included in your code by the following line.
    This implies inclusion of the following standard headers: <stdio.h>,
<string.h>, <errno.h>, <limits.h>, <assert.h> and <stdlib.h> (if available).
    Since Python may define some pre-processor definitions which affect the
standard headers on some systems, you must include Python.h before any standard
headers are included.*/
#include <Python.h>




static PyObject *
print_s(PyObject *self, PyObject *args){

    const char *string;

    /* parse positional parameters, only one Python string or Unicode object.
     * The Python string must not contain embedded NUL bytes, or a TypeError 
     * exception is raised. Unicode objects are converted to C strings using the
     * default encoding. If this conversion fails, a UnicodeError is raised.
        
     * PyArg_Parse* cannot check the validity of the addresses of C variables
     * passed to it.
     
     * You won’t have to release any memory returned by PyArg_Parse* yourself, 
     * except with the es, es#, et and et# formats.
     */
    if(!PyArg_ParseTuple(args, "s", &string))
        /* When a function f that calls another function g detects that the 
         * latter fails, f should itself return an error value (usually NULL or
         * -1). It should not call one of the PyErr_*() functions — one has 
         * already been called by g. The most detailed cause of the error was 
         * already reported by the function that first detected it.
         */
        return NULL;

    printf("%s\n", string);

    /* If you have a C function that returns no useful argument (a function
     * returning void), the corresponding Python function must return None.
     * This function does not own a reference to Py_None, but The caller will 
     * own the reference after this function return, so Py_INCREF is needed.*/
    Py_INCREF(Py_None);
    return Py_None;
}

PyDoc_STRVAR(print_s_doc,  "print_s(s)\nprint a string. ");




static PyObject *
print_two_s(PyObject *self, PyObject *args){

    const char *string1, *string2;

    /* parse positional parameters, only two strings */
    if(!PyArg_ParseTuple(args, "ss", &string1, &string2))
        return NULL;

    printf("%s\n%s\n", string1, string2);

    /* #define Py_RETURN_NONE return Py_INCREF(Py_None), Py_None */
    Py_RETURN_NONE;
}

PyDoc_STRVAR(print_two_s_doc, "print_s(s1, s2)\nprint two strings.");



static PyObject *
print_kwargs(PyObject *self, PyObject *args, PyObject *kwargs){

    int i;
    const char *s1=NULL, *s2=NULL;
    static char *kwlist[] = {"i", "s1", "s2", NULL};
    
    if(!PyArg_ParseTupleAndKeywords(args, kwargs, "|iss", kwlist,
                                    &i, &s1, &s2))
        return NULL;

    printf("i=%d\ns1=%s\ns2=%s\n", i, s1, s2);

    Py_RETURN_NONE;
}
PyDoc_STRVAR(print_kwargs_doc, "print_kwargs([i[, s1[, s2]]])\n\
print an integer and two string");



static PyObject *
inspect_dict(PyObject *self, PyObject *o){

    PyObject *file, *keys, *key, *value; 
    Py_ssize_t num_keys;
    int write_err, key_i;

    if (!PyDict_Check(o)) {                        
        /* It seems that PyDict_Check does not set exception when failed*/
        PyErr_SetString(PyExc_TypeError, "object is not a dict");
        return NULL;                                                            
    }

    /* borrowed reference */
    file = PySys_GetObject("stdout");                                       
    if (file == Py_None)                                                    
        /* sys.stdout may be None when FILE* stdout isn't connected */          
        Py_RETURN_NONE; 

    /* new reference, get a PyListObject */
    keys = PyDict_Keys(o);
    if(keys == NULL)
        return NULL;

    num_keys = PyList_Size(keys);
    for(key_i = 0; key_i < num_keys; key_i++){
        /* borrowed reference */
        key = PyList_GetItem(keys, key_i);

        write_err = PyFile_WriteObject(key, file, Py_PRINT_RAW);
        if(write_err){
            Py_DECREF(keys);
            return NULL;
        }
        printf("%s", "=>");

        /* borrowed reference, assume always succeed */
        value = PyDict_GetItem(o, key);
        write_err = PyFile_WriteObject(value, file, Py_PRINT_RAW);
        if(write_err){
            Py_DECREF(keys);
            return NULL;
        }

        printf("%s", "\n");
    }

    Py_DECREF(keys);
    Py_RETURN_NONE;
}

PyDoc_STRVAR(inspect_dict_doc, "inspect_dict(o)\n\
print a dict object");



static PyObject *
inspect_list(PyObject *self, PyObject *o){

    PyObject *item, *file;
    int i, len, write_err;

    if (!PyList_Check(o)) {                        
        PyErr_SetString(PyExc_TypeError, "object is not a list");
        return NULL;                                                            
    }

    file = PySys_GetObject("stdout");                                       
    if (file == Py_None)                                                    
        Py_RETURN_NONE; 

    len = PyList_Size(o);
    for(i = 0; i < len; i++){
        /* borrowed reference */
        item = PyList_GetItem(o, i);

        write_err = PyFile_WriteObject(item, file, Py_PRINT_RAW);
        if(write_err){
            return NULL;
        }

        if(i < len - 1)
            printf("%s", ", ");
    }

    printf("%s", "\n");
    Py_RETURN_NONE;

}


PyDoc_STRVAR(inspect_list_doc, "inspect_list(o)\n\
print a list object");



static PyObject *
test(PyObject *self, PyObject *o){
    PyObject *str, *file;

    str = PyString_FromString(" ");

    file = PySys_GetObject("stdout");                                       
    if (file == Py_None)                                                    
        Py_RETURN_NONE; 

    PyFile_WriteObject(str, file, Py_PRINT_RAW);

    Py_DECREF(str);
    Py_RETURN_NONE;
}



static PyMethodDef BasicFuncMethods[] = {
    {"print_s",  print_s, METH_VARARGS,
     print_s_doc},
    {"print_two_s",  print_two_s, METH_VARARGS,
     print_two_s_doc},
    /* The cast of the function is necessary since PyCFunction values only take 
     * two PyObject* parameters, and print_kwargs) takes three.
     */ 
    {"print_kwargs",  (PyCFunction)print_kwargs, METH_VARARGS | METH_KEYWORDS,
     print_kwargs_doc},
    {"inspect_dict",  (PyCFunction)inspect_dict, METH_O,
     inspect_dict_doc},
    {"inspect_list",  (PyCFunction)inspect_list, METH_O,
     inspect_list_doc},
    {"test",  test, METH_VARARGS,
     NULL},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};



/*
    When the Python program imports module for the first time, initbasic_func()
is called. The initialization function must be named initname(), where name is
the name of the module, and should be the only non-static item defined in the 
module file.
*/
PyMODINIT_FUNC
initbasic_func(void){
    (void) Py_InitModule("basic_func", BasicFuncMethods);
}

