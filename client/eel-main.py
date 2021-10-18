import eel

eel.init("www")

@eel.expose()
def hello(txt):
    print(txt)

eel.helloWorld("Hello from Python!")

hello("Hello from Python!")

eel.start("index.html", block=False)
print("Print from after start")
while True:
    eel.sleep(1)