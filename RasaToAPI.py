import requests

sender = input("Please tell me your name : \n")

bot_message =" "

while bot_message !="Bye":
    
    message = input("Type your message : \n")
    
    print("Sending now")
    
    r=requests.post('http://localhost:5005/webhooks/rest/webhook' , json={"sender": sender, "message":message})
    
    print("Bot says,", end='')

    data = r.json()
    
    for i in data:
        dictionary = i
        
        if 'text' in dictionary.keys():
            print(i['text'])
        else:
            print(i['image'])
