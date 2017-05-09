

#include <Python.h>


static PyObject *
insertion_sort(PyObject *self, PyObject *o){

    PyObject *new_list, *item_i, *item_j;
    Py_ssize_t len, i, j;
    int greater_than;

    new_list = PySequence_List(o);
    if (new_list == NULL)
        return NULL;

    len = PyList_Size(new_list);

    for(j = 1; j < len; j++){
        item_j = PyList_GetItem(new_list, j);
        // should own the reference
        Py_INCREF(item_j);
        i = j - 1;

        while (i >= 0){
            item_i = PyList_GetItem(new_list, i);
            Py_INCREF(item_i);

            greater_than = PyObject_RichCompareBool(item_i, item_j, Py_GT);

            if (greater_than == -1){
                Py_DECREF(item_i);
                Py_DECREF(item_j);
                Py_DECREF(new_list);
                return NULL;
            } else if (greater_than == 1){
                PyList_SetItem(new_list, i+1, item_i);
                i--;
            } else {
                break;
            }
        }

        // when break happened, decrease the reference.
        if (i >= 0)
            Py_DECREF(item_i);
        PyList_SetItem(new_list, i+1, item_j);
    }

    return new_list;
}

PyDoc_STRVAR(insertion_sort_doc,  "insertion sort.");


static PyMethodDef methods[] = {
    {"insertion_sort", (PyCFunction)insertion_sort, METH_O,
     insertion_sort_doc},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};


static struct PyModuleDef module = {
   PyModuleDef_HEAD_INIT,
   "sort_example",            /*  name of module */
   "sort example",            /*  module documentation, may be NULL */
   -1,                        /*  size of per-interpreter state of the module,
                                  or -1 if the module keeps state in global 
                                  variables. */
   methods
};


PyMODINIT_FUNC
PyInit_sort_example(void){
    return PyModule_Create(&module);
}

