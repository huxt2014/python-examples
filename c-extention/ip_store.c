/*     A simple database implemented by array that store and retrieve ip
 * information. Each record has four columns: begin, end, area, isp. The
 * [begin, end] are ip range. Ip address are represented as network integer.
 * Just as following:
 *
 *      (1,     10,         area1, isp2),
 *      (11,    21,         area2, isp2),
 *      ...
 *      (10000, 4294967295, area*, isp*)
 *
 *    Use binary search to retrieve ip information. */

#include <Python.h>
#include <arpa/inet.h>

#if PY_MAJOR_VERSION >= 3
#define IS_PY3K
#endif

typedef struct{
    unsigned long begin;
    unsigned long end;
    PyObject * area;
    PyObject * isp;
}ip_seg;

static ip_seg* ipdb = NULL;
static Py_ssize_t ipdb_size = 0;


static int
inner_atohl(PyObject *o, unsigned long *ip_ul){
    struct in_addr buf;
    char *ip_addr;

#ifdef IS_PY3K
    if(PyUnicode_CheckExact(o)){
        ip_addr = PyUnicode_AsUTF8(o);
    } else if (PyBytes_CheckExact(o)){
        ip_addr = PyBytes_AsString(o);
    } else if (PyByteArray_CheckExact(o)){
        ip_addr =  PyByteArray_AsString(o);
#else
    if(PyUnicode_CheckExact(o) || PyString_CheckExact(o)){
        ip_addr =  PyString_AsString(o);
    } else if (PyByteArray_CheckExact(o)){
        ip_addr = PyByteArray_AsString(o);
#endif
    } else {
        PyErr_SetString(PyExc_TypeError, "should be built-in string/bytes/byte array");
        return 0;
    }

    if (ip_addr == NULL){
        return 0;
    }

    if (inet_aton(ip_addr, &buf)){
        *ip_ul = ntohl(buf.s_addr);
        return 1;
    }else{
        PyErr_SetString(PyExc_ValueError,
                        "illegal IP address string");
        return 0;
    }
}


static PyObject *
ip_store_atohl(PyObject *self, PyObject *o){

    unsigned long ip_ul;

    if(inner_atohl(o, &ip_ul)){
        return PyLong_FromUnsignedLong(ip_ul);
    }else{
        return NULL;
    }
}


static void
free_db(ip_seg* db, Py_ssize_t size){
    Py_ssize_t i;

    for(i = 0; i < size; i++){
        Py_XDECREF(db[i].area);
        Py_XDECREF(db[i].isp);
    }
    PyMem_Free(db);
}


static PyObject *
build_record(ip_seg seg){
    PyObject *begin, *end, *record;

    record = PyTuple_New(4);
    if (record == NULL){
        return NULL;
    }

#ifdef IS_PY3K
    begin = PyLong_FromUnsignedLong(seg.begin);
    end = PyLong_FromUnsignedLong(seg.end);
#else
    begin = PyInt_FromLong(seg.begin);
    end = PyInt_FromLong(seg.end);
#endif
    if(begin == NULL || end == NULL){
        Py_XDECREF(begin);
        Py_XDECREF(end);
        Py_XDECREF(record);
        return NULL;
    }
    Py_INCREF(seg.area);
    Py_INCREF(seg.isp);

    PyTuple_SetItem(record, 0, begin);
    PyTuple_SetItem(record, 1, end);
    PyTuple_SetItem(record, 2, seg.area);
    PyTuple_SetItem(record, 3, seg.isp);

    return record;
}


static PyObject *
ip_store_load(PyObject *self, PyObject *o){

    PyObject *record, *item, *item2;
    Py_ssize_t size, i, j;
    unsigned long ip_ul;
    ip_seg* new_db = NULL;

    if(!PySequence_Check(o)){
        PyErr_SetString(PyExc_TypeError, "need sequence");
        return NULL;
    }

    size = PySequence_Length(o);
    if(size < 0){
        return NULL;
    }else if (size == 0){
        goto finish;
    }

    new_db = (ip_seg*)PyMem_Malloc(size * sizeof(ip_seg));
    if(new_db == NULL){
        return PyErr_NoMemory();
    }else{
        for(i = 0; i < size; i++){
            new_db[i].area = NULL;
            new_db[i].isp = NULL;
        }
    }

    for(i = 0; i < size; i++){
        record = PySequence_GetItem(o, i);
        if (!PySequence_Check(record)){
            PyErr_SetString(PyExc_TypeError, "need sequence for each record");
            goto record_failed;
        }

        for(j = 0; j < 2; j++){
            item = PySequence_GetItem(record, j);
            if(item == NULL){
                goto record_failed;
            }
#ifdef IS_PY3K
            if(!PyLong_Check(item)){
#else
            if(!PyInt_CheckExact(item)){
#endif
                Py_DECREF(item);
                PyErr_Format(PyExc_TypeError,
                             "expected int, %s found",
                             Py_TYPE(item)->tp_name); 
                goto record_failed;
            }

#ifdef IS_PY3K
            ip_ul = PyLong_AsUnsignedLong(item);
            if (ip_ul == (unsigned long) -1 && PyErr_Occurred()){
                Py_DECREF(item);
                goto record_failed;
            }
#else
            ip_ul = PyInt_AsUnsignedLongMask(item);
#endif

            ((unsigned long *)(new_db + i))[j] = ip_ul;
            Py_DECREF(item);
        }

        item = PySequence_GetItem(record, 2);
        item2 = PySequence_GetItem(record, 3);
        if(item == NULL || item2 == NULL){
            Py_XDECREF(item);
            Py_XDECREF(item2);
            goto record_failed;
        }
        new_db[i].area = item;
        new_db[i].isp = item2;
    }
    
finish:    
    free_db(ipdb, ipdb_size);
    ipdb_size = size;
    ipdb = new_db;
    Py_RETURN_NONE;
record_failed:
    Py_XDECREF(record);
    free_db(new_db, size);
    return NULL;
}


static PyObject *
ip_store_get(PyObject *self, PyObject *o){

    Py_ssize_t i;

#ifdef IS_PY3K
    if(!PyLong_Check(o)){
#else
    if(!PyInt_CheckExact(o)){
#endif
        PyErr_SetString(PyExc_TypeError, "need int");
        return NULL;
    }

#ifdef IS_PY3K
    i = PyLong_AsSsize_t(o);
    if(PyErr_Occurred()){
        return NULL;
    }
#else
    i = PyInt_AsSsize_t(o);
#endif

    if (i < 0 || i > ipdb_size -1){
        PyErr_SetString(PyExc_IndexError, "");
        return NULL;
    }

    return build_record(ipdb[i]);
}


static PyObject *
ip_store_search(PyObject *self, PyObject *o){

    int found = 0;
    unsigned long ip_ul;
    Py_ssize_t begin = 0, end = ipdb_size -1, mid;
    ip_seg *m_record;
    PyObject *result;

    if (ipdb_size == 0){
        Py_RETURN_NONE;
    }

    if(!inner_atohl(o, &ip_ul)){
        return NULL;
    }

    /* releasing GIL has been tested in the situation where there is
     * no IO operation. The result is that releasing GIL make worse
     * performance */

    /*
    Py_INCREF(o);
    Py_BEGIN_ALLOW_THREADS */

    while(begin <= end){
        mid = (begin + end)/2;
        m_record = ipdb + mid;

        if (ip_ul < m_record->begin){
            end = mid - 1;
        } else if (ip_ul > m_record->end){
            begin = mid + 1;
        } else{
            if (ip_ul <= m_record->end && ip_ul >= m_record->begin){
                found = 1;
            }
            break;
        }
    }

    /*
    Py_END_ALLOW_THREADS
    Py_DECREF(o); */

    if (found){
        result = PyTuple_New(2);
        if (result == NULL){
            return NULL;
        }

        Py_INCREF(m_record->area);
        Py_INCREF(m_record->isp);
        PyTuple_SetItem(result, 0, m_record->area);
        PyTuple_SetItem(result, 1, m_record->isp);

        return result;
    } else {
        Py_RETURN_NONE;
    }
}

static PyObject *
ip_store_size(PyObject *self){
#ifdef IS_PY3K
    return PyLong_FromSsize_t(ipdb_size);
#else
    return PyInt_FromSsize_t(ipdb_size);
#endif
}

static PyMethodDef methods[] = {
    {"atohl",  (PyCFunction)ip_store_atohl, METH_O,
     "convert an ip address in dotted format to host long integer."},
    {"load",  (PyCFunction)ip_store_load, METH_O,
     "load ipdb."},
    {"search",  (PyCFunction)ip_store_search, METH_O,
     "search by ip."},
    {"size",  (PyCFunction)ip_store_size, METH_NOARGS,
     "current size of db_store."},
    {"get",  (PyCFunction)ip_store_get, METH_O,
     "get one record by positive index"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

#ifdef IS_PY3K
static struct PyModuleDef spammodule = {
   PyModuleDef_HEAD_INIT,
   "ip_store",   /* name of module */
   "empty",      /* module documentation, may be NULL */
   -1,           /* size of per-interpreter state of the module,
                    or -1 if the module keeps state in global variables. */
   methods
};
#define INITERROR return NULL

PyMODINIT_FUNC
PyInit_ip_store(void)
#else

#define INITERROR return

PyMODINIT_FUNC
initip_store(void)
#endif
{
    #ifdef IS_PY3K
    PyObject *module = PyModule_Create(&spammodule);
    #else
    PyObject *module = Py_InitModule("ip_store", methods);
    #endif

    if (module == NULL)
        INITERROR;

#ifdef IS_PY3K
    return module;
#endif
}
