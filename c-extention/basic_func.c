
/*

OBJECTS

    Almost all Python objects live on the heap: you never declare an automatic
or static variable of type PyObject. Only pointer variables of type PyObject*
can be declared. The sole exception are the type objects; since these must never
be deallocated, they are typically static PyTypeObject objects.

    All Python objects (even Python integers) have a type and a reference count. 


REFERENCE COUNTS

    Nobody “owns” an object; however, you can own a reference to an object. The
owner of a reference is responsible for calling Py_DECREF() when the reference
is no longer needed. 

    Ownership of a reference can be transferred, meaning that the code that 
receives ownership of the reference then becomes responsible for eventually
decref’ing. 

    It is also possible to borrow a reference to an object. The borrower of a 
reference should not call Py_DECREF(). The borrower must not hold on to the 
object longer than the owner from which it was borrowed. A borrowed reference 
can be changed into an owned reference by calling Py_INCREF().

    Stealing a reference means that when you pass a reference to a function,
that function assumes that it now owns that reference, and you are not
responsible for it any longer. Before call a function that will steal the
reference, the caller should own a reference first.

FUNCTION

    For module function, the first parameters passed in will always be NULL or
a pointer selected while initializing the module. The second parameters passed
in will always be a tuple.

    When a function passes ownership of a reference on to its caller, the caller
is said to receive a new reference. When no ownership is transferred, the caller
is said to borrow the reference. 

    Conversely, when a calling function passes in a reference to an object,  
there are two possibilities: the function steals a reference to the object, or
it borrows a reference.

    PyTuple_SetItem() and PyList_SetItem() steal a reference to the item (but 
not to the tuple or list). These functions take over ownership of the item
passed to them, even if they fail! When you want to keep using an object
although the reference to it will be stolen, use Py_INCREF() to grab another
reference before calling the reference-stealing function.

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

/* for PY2 and PY3 compatible */
struct module_state {
    PyObject *error;
};

#if PY_MAJOR_VERSION >= 3
#define IS_PY3K
#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
#else
#include <bytesobject.h>         /* map PyBytes names to PyString ones*/
#define GETSTATE(m) (&_state)
static struct module_state _state;
#endif

/* end PY2 and PY3 compatible */

/* For Python 3, the module-level function's first argument self
 * is the module object. For Python 2, self is NULL or a pointer
 * selected while initializing the module. */
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
    Py_ssize_t i, len;
    int write_err;

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
inspect_type(PyObject *self, PyTypeObject *type){

    PyObject *o_null;
    char *name_call=NULL, *name_alloc=NULL, *name_new=NULL, *name_init=NULL,
         *name_get=NULL, *name_gc=NULL, *name_clear=NULL;

    if (!PyType_Check(type)){
        PyErr_SetString(PyExc_TypeError, "object is not a type or a class");
        return NULL;
    }

    o_null = PyUnicode_FromString("NULL");

    /* tp_call */
    if (type->tp_call == PyType_Type.tp_call)
        name_call = "type_call";
    else if (type->tp_call == NULL)
        name_call = "NULL";

    /* tp_alloc*/
    if (type->tp_alloc == PyType_GenericAlloc)
        name_alloc = "PyType_GenericAlloc";
    else if (type->tp_alloc == NULL)
        name_alloc = "NULL";

    /* tp_new */
    if (type->tp_new == PyType_Type.tp_new)
        name_new = "type_new";
    else if (type->tp_new == PyBaseObject_Type.tp_new)
        name_new = "object_new";
    else if (type->tp_new == NULL)
        name_new = "NULL";

    /* tp_init */
    if (type->tp_init == PyType_Type.tp_init)
        name_init = "type_init";
    else if (type->tp_init == PyBaseObject_Type.tp_init)
        name_init = "object_init";
    else if (type->tp_init == NULL)
        name_init = "NULL";

    /* tp_getattro*/
    if (type->tp_getattro == PyType_Type.tp_getattro)
        name_get = "type_getattro";
    else if (type->tp_getattro == PyObject_GenericGetAttr)
        name_get = "PyObject_GenericGetAttr";
    else if (type->tp_getattro == NULL)
        name_get = "NULL";

    /* tp_is_gc */
    if (type->tp_is_gc == PyType_Type.tp_is_gc)
        name_gc = "type_is_gc";
    else if (type->tp_is_gc == NULL)
        name_gc = "NULL";

    /* tp_clear */
    if (type->tp_clear == PyType_Type.tp_clear)
        name_clear = "type_clear";
    else if (type->tp_clear == NULL)
        name_clear = "NULL";

    PyObject *content = PyUnicode_FromFormat(
                            "ob_type: %S\n"
                            "tp_basicsize: %zi\ntp_itemsize: %zi\n"
                            "tp_call: %s\ntp_getattro: %s\n"
                            "tp_clear: %s\ntp_weaklistoffset: %zi\n"
                            "tp_base: %S\ntp_dict: %S\ntp_dictoffset: %zi\n"
                            "tp_init: %s\ntp_alloc: %s\ntp_new: %s\n"
                            "tp_is_gc: %s\n"
                            "tp_bases: %S\n",
                            (PyObject *)Py_TYPE(type),
                            type->tp_basicsize, type->tp_itemsize,
                            name_call == NULL ? "unknown" : name_call,
                            name_get == NULL ? "unknown" : name_get,
                            name_clear == NULL ? "unknown" : name_clear,
                            type->tp_weaklistoffset,
                            type->tp_base == NULL ? o_null:(PyObject *)(type->tp_base),
                            type->tp_dict == NULL ? o_null:(PyObject *)(type->tp_dict),
                            type->tp_dictoffset,
                            name_init == NULL ? "unknown" : name_init,
                            name_alloc == NULL ? "unknown" : name_alloc,
                            name_new == NULL ? "unknown" : name_new,
                            name_gc == NULL ? "unknown" : name_gc,
                            (PyObject *)(type->tp_bases)
                        );

    PyObject_Print(content, stdout, Py_PRINT_RAW);
    fflush(stdout);

    Py_DECREF(o_null);
    Py_RETURN_NONE;
}

PyDoc_STRVAR(inspect_type_doc, "inspect_type(o)\n\
print type, tp_base, tp_bases of a type");

static PyObject *
test(PyObject *self, PyObject *o){
    PyObject *str, *file;

    str = PyBytes_FromString(" ");

    file = PySys_GetObject("stdout");                                       
    if (file == Py_None)                                                    
        Py_RETURN_NONE; 

    PyFile_WriteObject(str, file, Py_PRINT_RAW);

    Py_DECREF(str);
    Py_RETURN_NONE;
}



static PyMethodDef module_methods[] = {
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
    {"inspect_type",  (PyCFunction)inspect_type, METH_O,
     inspect_type_doc},
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
#ifdef IS_PY3K

static int basic_func_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int basic_func_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}


/* PY3 should hove a module definition structure */
static struct PyModuleDef basic_func_module = {
    PyModuleDef_HEAD_INIT,
    "basic_func",                  /* module name */
    "doc for basic func",          /* may be NULL */
    sizeof(struct module_state),   /* size of per-interpreter state of the
                                      module. -1 if module keeps state in global
                                      variables */
    module_methods,                /* module level function */
    NULL,
    basic_func_traverse,
    basic_func_clear,
    NULL
};

#define INITERROR return NULL

PyMODINIT_FUNC      /* PyObject * in PY3*/
PyInit_basic_func(void)

#else
#define INITERROR return

PyMODINIT_FUNC      /* void in PY2 */
initbasic_func(void)
#endif
{

#ifdef IS_PY3K
    PyObject *module = PyModule_Create(&basic_func_module);
#else
    PyObject *module = Py_InitModule("basic_func", module_methods);
#endif

    if (module == NULL)
        INITERROR;
    struct module_state *st = GETSTATE(module);
    st;

#ifdef IS_PY3K
    /* PY3 should return the module object */
    return module;
#endif
}

