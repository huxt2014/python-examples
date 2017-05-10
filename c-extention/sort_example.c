

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


static int _merge_sort(PyObject *o, Py_ssize_t l, Py_ssize_t r);
static int _merge(PyObject *o, Py_ssize_t l, Py_ssize_t m, Py_ssize_t r);

static PyObject *
merge_sort(PyObject *self, PyObject *o){

    Py_ssize_t len;
    PyObject *new_list;
    int result;

    new_list = PySequence_List(o);
    if (new_list == NULL)
        return NULL;

    len = PyList_Size(new_list);
    if (len < 2)
        return new_list;
    else {
        result = _merge_sort(new_list, 0, len-1);
        if (result == -1){
            Py_DECREF(new_list);
            return NULL;
        }
        else {
            return new_list;
        }
    }

}

PyDoc_STRVAR(merge_sort_doc,  "merge sort.");

static int
_merge_sort(PyObject *o, Py_ssize_t l, Py_ssize_t r){
    
    Py_ssize_t m;

    if (l < r){
        m = (l+r)/2;
        if ( _merge_sort(o, l, m) == -1)
            return -1;
        if ( _merge_sort(o, m+1, r) == -1)
            return -1;
        if ( _merge(o, l, m, r) == -1)
            return -1;

        return 0;
    }
    else {
        return 0;
    }
}

static int
_merge(PyObject *o, Py_ssize_t l, Py_ssize_t m, Py_ssize_t r){

    PyObject *list_l, *list_r, *item, *item_l, *item_r;
    Py_ssize_t index_l, index_r, i;
    int less_or_equal;

    list_l = PyList_New(m-l+1);
    if (list_l == NULL)
        return -1;

    list_r = PyList_New(r-m);
    if (list_r == NULL){
        Py_DECREF(list_l);
        return -1;
    }

    for (index_l = l; index_l <= m; index_l++){
        item = PyList_GetItem(o, index_l);
        Py_INCREF(item);
        PyList_SetItem(list_l, index_l-l, item);
    }

    for (index_r = m+1; index_r <= r; index_r++){
        item = PyList_GetItem(o, index_r);
        Py_INCREF(item);
        PyList_SetItem(list_r, index_r-m-1, item);
    }

    index_l = index_r = 0;

    for (i = l; i <= r; i++){
        if ( index_l > m-l) {
            item_r = PyList_GetItem(list_r, index_r);
            Py_INCREF(item_r);
            PyList_SetItem(o, i, item_r);
            index_r++;
        } else if ( index_r > r-m-1){
            item_l = PyList_GetItem(list_l, index_l);
            Py_INCREF(item_l);
            PyList_SetItem(o, i, item_l);
            index_l++;
        } else {
            item_l = PyList_GetItem(list_l, index_l);
            item_r = PyList_GetItem(list_r, index_r);
            less_or_equal = PyObject_RichCompareBool(item_l, item_r, Py_LE);

            if (less_or_equal == -1){
                Py_DECREF(list_l);
                Py_DECREF(list_r);
                return -1;
            } else if (less_or_equal == 1){
                Py_INCREF(item_l);
                PyList_SetItem(o, i, item_l);
                index_l++;
            } else {
                Py_INCREF(item_r);
                PyList_SetItem(o, i, item_r);
                index_r++;
            }
        }
    }

    Py_DECREF(list_l);
    Py_DECREF(list_r);
    return 0;

}




static PyMethodDef methods[] = {
    {"insertion_sort", (PyCFunction)insertion_sort, METH_O,
     insertion_sort_doc},
    {"merge_sort", (PyCFunction)merge_sort, METH_O,
     merge_sort_doc},
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

