def offline_gyani_response(prompt):
    prompt = prompt.lower()

    # Physics
    if "newton" in prompt and "first" in prompt:
        return "Newton ka pehla niyam: Ek vastu tab tak vishram ya seedhi gati me rehti hai jab tak koi external force us par kaam na kare."
    elif "newton" in prompt and "second" in prompt:
        return "Newton ka doosra niyam: F = m × a (Bal = Dravya × Veegh)."
    elif "newton" in prompt and "third" in prompt:
        return "Newton ka teesra niyam: Har kriya ke barabar aur vipreet pratikriya hoti hai."

    # Chemistry
    elif "acid" in prompt:
        return "Acid ka pH 7 se kam hota hai. Jaise HCl ek strong acid hai."
    elif "base" in prompt:
        return "Base ya alkali ka pH 7 se jyada hota hai. Jaise NaOH ek strong base hai."
    elif "neutral" in prompt:
        return "Neutral solution ka pH bilkul 7 hota hai. Jaise distilled water."

    # Math
    elif "pythagoras" in prompt:
        return "Pythagoras theorem: In a right triangle, (hypotenuse)^2 = (base)^2 + (height)^2"
    elif "derivative" in prompt:
        return "Derivative ek function ki rate of change ko dikhata hai. f(x) = x^2 ka derivative hai 2x."

    # Python Programming
    elif "for loop" in prompt:
        return "Python me for loop aise chalta hai:\nfor i in range(5):\n    print(i)"
    elif "if else" in prompt:
        return "Python me if-else statement:\nif condition:\n    # code\nelse:\n    # code"
    elif "function" in prompt:
        return "Python me function define karte hain:\ndef my_func():\n    print(\"Hello\")"

    # HTML
    elif "html structure" in prompt:
        return "Basic HTML structure:\n<html>\n  <head><title>Page</title></head>\n  <body>Content here</body>\n</html>"

    # GK / SSC
    elif "constitution" in prompt:
        return "Bharat ka samvidhan 26 January 1950 ko lagu hua tha."
    elif "president of india" in prompt:
        return "Bharat ke vartaman rashtrapati ka naam Draupadi Murmu hai (2024 tak)."
    elif "first prime minister" in prompt:
        return "Bharat ke pehle pradhanmantri the Pandit Jawaharlal Nehru."

    else:
        return "🧠 Gyani: Ye prashn mere offline gyaan me nahi hai. Kripya aur prashn poochhiye ya internet model ka upyog kijiye."

# Test
if __name__ == "__main__":
    while True:
        user_q = input("Prashn puchho: ")
        if user_q.strip().lower() in ["exit", "quit"]:
            break
        print(offline_gyani_response(user_q))
