
#include <Python.h>

#define LEFT 0
#define RIGHT 1
#define CHILD(node, d) (node->children[d])
#define LEFT_NODE(node) (node->children[LEFT])
#define RIGHT_NODE(node) (node->children[RIGHT])

typedef struct tree_node node_t;

struct tree_node {
    node_t *children[2];
    PyObject *key;
    PyObject *value;
    int xdata;
};

typedef struct {
    PyObject_HEAD
    node_t *root;
    Py_ssize_t size;
    int d_flag;
}base_tree;

typedef enum{KEY, VALUE, ITEM} content_type;

static void
_delete_tree(node_t *root){
    if (root == NULL){
        return;
    }
    if (LEFT_NODE(root) != NULL){
        _delete_tree(LEFT_NODE(root));
    }
    if (RIGHT_NODE(root) != NULL){
        _delete_tree(RIGHT_NODE(root));
    }
    Py_XDECREF(root->key);
    Py_XDECREF(root->value);
    PyMem_Free(root);
}


static node_t *
_new_node(PyObject *key, PyObject *value){
    node_t * node = PyMem_Malloc(sizeof(node_t));
    if (node != NULL){
        LEFT_NODE(node) = NULL;
        RIGHT_NODE(node) = NULL;
        Py_INCREF(key);
        Py_INCREF(value);
        node->key = key;
        node->value = value;
    }
    return node;
}


static void
_delete_node(node_t *node){
    if (node != NULL){
        Py_XDECREF(node->key);
        Py_XDECREF(node->value);
        PyMem_Free(node);
    }
}

static void
_swap_node_data(node_t *n1, node_t *n2){
    PyObject *tmp_p;
    int tmp_i;

    tmp_p = n1->key;   n1->key = n2->key;  n2->key = tmp_p;
    tmp_p = n1->value;   n1->value = n2->value;  n2->value = tmp_p;
    tmp_i = n1->xdata;   n1->xdata = n2->xdata;  n2->xdata = tmp_i;
}


/* return -1: key1 < key2
 * return 1:  key1 > key2
 * return 0:  key1 == key2 or error*/
static int
_compare(PyObject *key1, PyObject *key2){
    int res;

    res = PyObject_RichCompareBool(key1, key2, Py_LT);
    if (res > 0){
        return -1;
    } else if (res < 0){
        /* should check error indicator later */
        PyErr_SetString(PyExc_TypeError, "invalid type for key");
        return 0;
    }

    /* return 0 or 1. If get -1, it should have happened at
    * the first compare*/
    return PyObject_RichCompareBool(key1, key2, Py_GT);
}


/* if get a key or a value, return a borrowed reference,
 * if get a key-value pair, return a new reference,
 * if failed, return NULL */
static PyObject *
_get_object(node_t *node, content_type t){
    PyObject *item;

    if(t == KEY){
        return node->key;
    } else if (t == VALUE){
        return node->value;
    } else {
        item = PyTuple_New(2);
        if (item != NULL){
            PyTuple_SET_ITEM(item, 0, node->key);
            PyTuple_SET_ITEM(item, 1, node->value);
            Py_INCREF(node->key);
            Py_INCREF(node->value);
        }
        return item;
    }
}


static int
_inorder_walk(node_t *node, PyObject *list, content_type t){
    PyObject *item;
    int res;

    if (node != NULL){
        if (_inorder_walk(CHILD(node, LEFT), list, t) < 0)
            return -1;

        item = _get_object(node, t);
        if (item == NULL)
            return -1;
        res = PyList_Append(list, item);
        if (t == ITEM)
            Py_DECREF(item);
        if (res < 0)
            return -1;
    
        if(_inorder_walk(CHILD(node, RIGHT), list, t) < 0)
            return -1;
    }

    return 0;
}


static void
_min_or_max(node_t *node, node_t **target, node_t **parent, int is_max){

    int direction = is_max ? RIGHT : LEFT;
    *target = node;
    *parent = NULL;

    if (node == NULL){
        return;
    }

    while(CHILD(node, direction) != NULL){
        *parent = node;
        node = *target = CHILD(node, direction);
    }
    return;
}


static void
dealloc_tree(base_tree *self){
    _delete_tree(self->root);
    self->root = NULL;
}


static PyObject *
tree_root(base_tree *self){
    if (self->root == NULL){
        return NULL;
    } else {
        Py_INCREF(self->root->value);
        return self->root->value;
    }
}


static PyObject *
tree_subscript(base_tree *self, PyObject *key){

    int cmp_res;
    node_t *node = self->root;

    while(node != NULL){
        cmp_res = _compare(key, node->key);
        if (cmp_res == 0){
            if (PyErr_Occurred())
                return NULL;
            Py_INCREF(node->value);
            return node->value;
        }
        node = CHILD(node, (cmp_res > 0) ? RIGHT : LEFT);
    }
    _PyErr_SetKeyError(key);
    return NULL;
}

#define DEFINE_GET_ALL(PREFIX,C_TYPE) \
    static PyObject * \
    tree_##PREFIX(base_tree *self){ \
        PyObject *list = PyList_New(0); \
        if (self->size == 0){ \
            return list; \
        } else { \
            if (list == NULL){ \
                return NULL; \
            } \
            if (_inorder_walk(self->root, list, C_TYPE) < 0){ \
                Py_DECREF(list); \
                return NULL; \
            } \
            return list; \
        } \
    } \

DEFINE_GET_ALL(keys, KEY)
DEFINE_GET_ALL(values, VALUE)
DEFINE_GET_ALL(items, ITEM)

static Py_ssize_t
tree_length(base_tree *self){
    return self->size;
}

static int
binary_insert(base_tree *self, PyObject *key, PyObject *value){

    node_t *node, *p;
    int cmp_res, child;

    if (self->root == NULL){
        node = _new_node(key, value);
        if (node == NULL)
            return -1;
        self->root = node;
        self->size = 1;
        return 0;
    }

    p = NULL;
    node = self->root;
    while(1){
        if (node == NULL){
            node = _new_node(key, value);
            if (node == NULL)
                return -1;
            CHILD(p, child) = node;
            self->size += 1;
            return 0;
        }

        cmp_res = _compare(key, node->key);
        if (cmp_res == 0){
            if (PyErr_Occurred())
                return -1;
            Py_INCREF(value);
            Py_DECREF(node->value);
            node->value = value;
            return 0;
        }
        p = node;
        child = (cmp_res > 0) ? RIGHT : LEFT;
        node = CHILD(node, child);
    }
}


static PyMappingMethods binarytree_as_mapping = {
    (lenfunc)tree_length,            /*mp_length*/
    (binaryfunc)tree_subscript,      /*mp_subscript*/
    (objobjargproc)binary_insert,    /*mp_ass_subscript*/
};


PyDoc_STRVAR(pop__doc__,
"D.pop(k[,d]) -> v, remove specified key and return the corresponding value.\n\
If key is not found, d is returned if given, otherwise KeyError is raised");


static PyObject *
binary_pop(base_tree *self, PyObject *args){

    PyObject *key, *deflt = NULL;
    node_t *node = self->root, *p = NULL, *t = NULL, *tp = NULL;
    int cmp_res, chd;

    if(!PyArg_UnpackTuple(args, "pop", 1, 2, &key, &deflt))
        return NULL;

    while (node != NULL) {
        cmp_res = _compare(key, node->key);
        if (cmp_res == 0){
            if (PyErr_Occurred())
                return NULL;

            /* found */
            deflt = node->value;
            self->size --;

            if (CHILD(node, LEFT) != NULL && CHILD(node, RIGHT) != NULL ){
                /* replace node by successor or predecessor in turn */
                _min_or_max(CHILD(node, self->d_flag), &t, &tp,
                            1 - self->d_flag);
                _swap_node_data(node, t);
                if (tp == NULL){
                    /* successor or predecessor is direct child */
                    CHILD(node, self->d_flag) = CHILD(t, self->d_flag);
                } else {
                    CHILD(tp, 1 - self->d_flag) = CHILD(t, self->d_flag);;
                }
                self->d_flag = 1 - self->d_flag;
                _delete_node(t);
            } else {
                cmp_res = (CHILD(node, LEFT) == NULL) ? RIGHT : LEFT;
                if (p == NULL){
                    /* found on root */
                    self->root = CHILD(node, cmp_res);
                } else {
                    CHILD(p, chd) = CHILD(node, cmp_res);
                }
                _delete_node(node);
            }

            break;
        }

        p = node;
        chd = (cmp_res > 0) ? RIGHT : LEFT;
        node = CHILD(node, chd);
    }

    if (deflt == NULL){
        _PyErr_SetKeyError(key);
    } else {
        Py_INCREF(deflt);
    }
    return deflt;
}


static PyMethodDef binary_methods[] = {
    {"pop", (PyCFunction)binary_pop, METH_VARARGS,
     pop__doc__},
    {"root", (PyCFunction)tree_root, METH_NOARGS,
     "get the value at the root"},
    {"keys", (PyCFunction)tree_keys, METH_NOARGS,
     "get all keys "},
    {"values", (PyCFunction)tree_values, METH_NOARGS,
     "get all values "},
    {"items", (PyCFunction)tree_items, METH_NOARGS,
     "get all key-value pairs"},
    {NULL}  /* Sentinel */
};


static PyTypeObject BinaryTreeType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "tree.BinaryTree",         /* tp_name */
    sizeof(base_tree),         /* tp_basicsize */
    0,                         /* tp_itemsize */
    (destructor)dealloc_tree,  /* tp_dealloc */
    0,                         /* tp_print */
    0,                         /* tp_getattr */
    0,                         /* tp_setattr */
    0,                         /* tp_reserved */
    0,                         /* tp_repr */
    0,                         /* tp_as_number */
    0,                         /* tp_as_sequence */
    &binarytree_as_mapping,    /* tp_as_mapping */
    0,                         /* tp_hash  */
    0,                         /* tp_call */
    0,                         /* tp_str */
    0,                         /* tp_getattro */
    0,                         /* tp_setattro */
    0,                         /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT |
        Py_TPFLAGS_BASETYPE,   /* tp_flags */
    "Binary tree",             /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    binary_methods,            /* tp_methods */
    NULL,                      /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    NULL,                      /* tp_init */
    0,                         /* tp_alloc */
    PyType_GenericNew,         /* tp_new */
};

static PyModuleDef this_module = {
    PyModuleDef_HEAD_INIT,
    "tree",
    "a module that provides tree structure.",
    -1,
    NULL, NULL, NULL, NULL, NULL
};


PyMODINIT_FUNC
PyInit_tree(void)
{
    PyObject* m;

    if (PyType_Ready(&BinaryTreeType) < 0)
        return NULL;

    m = PyModule_Create(&this_module);
    if (m == NULL)
        return NULL;

    Py_INCREF(&BinaryTreeType);
    PyModule_AddObject(m, "BinaryTree", (PyObject *)&BinaryTreeType);
    return m;
}

