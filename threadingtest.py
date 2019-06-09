import threading

def func(text):
    print (text)

thread_list = []
for i in range (4):
    thread = threading.Thread(target = func,args=(i,))
    thread_list.append(thread)
    thread.start()