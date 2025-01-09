from routing import process_query

def chatbot():
    print("Selamat datang! Saya adalah chatbot Anda. Tanyakan apa saja, atau ketik 'keluar' untuk berhenti.")
    chat_history = []  # Untuk menyimpan sejarah percakapan
    while True:
        query = input("Anda: ")
        if query.lower() in ["keluar", "exit"]:
            print("Bot: Sampai jumpa! Semoga harimu menyenangkan!")
            break
        result = process_query(query)
        chat_history.append({"role": "user", "content": query})
        chat_history.append({"role": "assistant", "content": result["response"]})
        print(f"Bot: {result['response']}")

if __name__ == "__main__":
    chatbot()
