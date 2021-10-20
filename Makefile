
PYLIB=-o app
PYINC=-I-I/usr/include -I/usr/include -I/usr/include/python3.6 -I/usr/include/python3.6 
LIBS=-L/usr/lib -L/usr/lib -lpthread -ldl  -lutil -lm
OPTS=-DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes
PROGRAMS=app 
all: $(PROGRAMS)

app: app.o
	gcc app.o $(LIBS) $(PYLIB) -o app
app.o: app.c
	gcc app.c -c $(PYINC) $(OPTS)
clean:
	rm -f $(PROGRAMS) *.o *.pyc core
