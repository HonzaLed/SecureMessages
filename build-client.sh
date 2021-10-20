cd client
cython clientCpl.py --embed
gcc -Os -I /usr/include/python3.6m -o client clientCpl.c -lpython3.6m -lpthread -lm -lutil -ldl
