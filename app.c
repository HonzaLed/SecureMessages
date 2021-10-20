#include <Python.h>
int main()
{
printf("Loading...\n");
Py_Initialize();
PyRun_SimpleString("import os");
PyRun_SimpleString("print(os.getcwd(),os.listdir())");
/*PyRun_SimpleString("words = string.split('rod jane freddy')");
PyRun_SimpleString("print string.join(words,', ')");
*/
Py_Finalize();
return 0;
}
