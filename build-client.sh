cd client
cython client.py --embed
gcc -Os -I /usr/include/python3.6m -o client client.c -lpython3.6m -lpthread -lm -lutil -ldl
