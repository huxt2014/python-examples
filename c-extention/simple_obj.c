
#include <Python.h>
/* This include provides declarations that we use to handle attributes */
#include <structmember.h>

/* each instance will contain this struct */
typedef struct {
    /* This head contain a refcount and a pointer to a type object. Should
     * not add semicolon */
    PyObject_HEAD

    /*  Type-specific fields go here. */
    PyObject *first;
    PyObject *last;
    int number;
} Simple;


static void
Simple_dealloc(Simple* self){
    /* should not use Py_DECREF, for the reason that self->first and self->last
     * may be NULL. */
    Py_XDECREF(self->first);
    Py_XDECREF(self->last);
    /* the type of self may be sub-class of Simple */
    Py_TYPE(self)->tp_free((PyObject*)self);

}


static PyObject *
Simple_new(PyTypeObject *type, PyObject *args, PyObject *kwargs){

    Simple *self;

    /* new reference */
    self = (Simple *)type->tp_alloc(type, 0);
    if (self != NULL) {
        /* new reference */
        self->first = PyString_FromString("");
        if (self->first == NULL) {
            Py_DECREF(self);
            return NULL;
        }

        self->last = PyString_FromString("");
        if (self->last == NULL) {
            Py_DECREF(self);
            /* we do not need to call Py_DECREF(self->first) here, because
             * it is called in Simple_dealloc.*/
            return NULL;
        }

        self->number = 0;
    }

    return (PyObject *)self;

}


static int
Simple_init(Simple *self, PyObject *args, PyObject *kwargs) {

    PyObject *first=NULL, *last=NULL, *tmp;
    static char *kwlist[] = {"first", "last", "number", NULL};

    if (! PyArg_ParseTupleAndKeywords(args, kwargs, "|SSi", kwlist,
                                      &first, &last, &self->number))
        return -1;

    /* Initializers can be called multiple times, so be careful when assigning
     * new values. */
    if (first) {
        /* do not decrease the reference to first directly, for the destructor
         * may access the first member. */
        tmp = self->first;
        /* Simple_init get borrowed reference */
        Py_INCREF(first);
        self->first = first;
        Py_XDECREF(tmp);
    }

    if (last) {
        tmp = self->last;
        Py_INCREF(last);
        self->last = last;
        Py_XDECREF(tmp);
    }

    return 0;
}

static PyMemberDef Simple_members[] = {
    {"first", T_OBJECT_EX, offsetof(Simple, first), 0,
     "first name"},
    {"last", T_OBJECT_EX, offsetof(Simple, last), 0,
     "last name"},
    {"number", T_INT, offsetof(Simple, number), 0,
     "number"},
    {NULL}  /*  Sentinel */
};



static PyObject *
Simple_name(Simple *self) {

    static PyObject *format = NULL;
    PyObject *args, *result;

    /* may be NULL when deleted. */
    if (self->first == NULL) {
        PyErr_SetString(PyExc_AttributeError, "first");
        return NULL;
    }

    if (self->last == NULL) {
        PyErr_SetString(PyExc_AttributeError, "last");
        return NULL;
    }

    /* It builds a tuple only if its format string contains two or more format
     * units. If the format string is empty, it returns None; if it contains 
     * exactly one format unit, it returns whatever object is described by that
     * format unit. To force it to return a tuple of size 0 or one, parenthesize
     * the format string. */
    args = Py_BuildValue("OO", self->first, self->last);
    if (args == NULL)
        return NULL;

    format = PyString_FromString("%s %s");
    if (format == NULL) {
        Py_DECREF(args);
        return NULL;
    }

    /* new reference, analogous to format % args, the argument must a tuple
     * or dict */
    result = PyString_Format(format, args);

    Py_DECREF(args);
    Py_DECREF(format);

    return result;

}

static PyMethodDef Simple_methods[] = {
    {"name", (PyCFunction)Simple_name, METH_NOARGS,
     "Return the name, combining the first and last name"},
    {NULL}  /*  Sentinel */
};

/*
 * tp_name will appear in the default textual representation of our objects and
 * in some error messages. Note that the name is a dotted name that includes 
 * both the module name and the name of the type within the module. One side
 * effect of using an undotted name is that the pydoc documentation tool will 
 * not list the new type in the module documentation.
 */

static PyTypeObject SimpleType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "simple_obj.Simple",             /*  tp_name */
    sizeof(Simple),                  /*  tp_basicsize */
    0,                               /*  tp_itemsize */
    (destructor)Simple_dealloc,      /*  tp_dealloc */
    0,                               /*  tp_print */
    0,                               /*  tp_getattr */
    0,                               /*  tp_setattr */
    0,                               /*  tp_compare */
    0,                               /*  tp_repr */
    0,                               /*  tp_as_number */
    0,                               /*  tp_as_sequence */
    0,                               /*  tp_as_mapping */
    0,                               /*  tp_hash */
    0,                               /*  tp_call */
    0,                               /*  tp_str */
    0,                               /*  tp_getattro */
    0,                               /*  tp_setattro */
    0,                               /*  tp_as_buffer */
    Py_TPFLAGS_DEFAULT 
        | Py_TPFLAGS_BASETYPE,       /*  tp_flags */
    "Simple objects",                /*  tp_doc */
    0,                               /*  tp_traverse */
    0,                               /*  tp_clear */
    0,                               /*  tp_richcompare */
    0,                               /*  tp_weaklistoffset */
    0,                               /*  tp_iter */
    0,                               /*  tp_iternext */
    Simple_methods,                  /*  tp_methods */
    Simple_members,                  /*  tp_members */
    0,                               /*  tp_getset */
    0,                               /*  tp_base */
    0,                               /*  tp_dict */
    0,                               /*  tp_descr_get */
    0,                               /*  tp_descr_set */
    0,                               /*  tp_dictoffset */
    (initproc)Simple_init,           /*  tp_init */
    0,                               /*  tp_alloc */
    Simple_new,                      /*  tp_new */
}; 

static PyMethodDef module_methods[] = {
    {NULL}  /*  Sentinel */
};

#ifndef PyMODINIT_FUNC  /*  declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initsimple_obj(void) 
{
    PyObject* m;

    /* enable object creation. On some platforms or compilers, we can’t 
     * statically initialize a structure member with a function defined in 
     * another C module, so, instead, we’ll assign the tp_new slot in the module
     * initialization function just before calling PyType_Ready() */
    // simple_SimpleType.tp_new = PyType_GenericNew;

    /* This initializes the Noddy type, filing in a number of members, including
     * ob_type that we initially set to NULL. */
    if (PyType_Ready(&SimpleType) < 0)
        return;

    m = Py_InitModule3("simple_obj", module_methods,
                       "Example module that creates an extension type.");

    if (m == NULL)
        return;

    Py_INCREF(&SimpleType);

    /* This adds the type to the module dictionary.  */
    PyModule_AddObject(m, "Simple", (PyObject *)&SimpleType);
}




