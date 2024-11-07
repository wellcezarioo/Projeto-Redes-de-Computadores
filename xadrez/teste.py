from palavra import palavra
def jogar():
    erros = 0
    letras = []

    letras_certas = ""
    print(letras)


    while(erros != 5):

        resposta = input("qual letra voce acha que tem na palavra?\n").strip().lower()


        while len(resposta) != 1:
            resposta = input("por favor, uma letra!").strip().lower()

        if resposta not in palavra:
            erros += 1
            if(erros == 5):
                break

        elif resposta in palavra:
            letras_certas.append(resposta)

        for i in palavra:
            if i in letras_certas:
                print(i, end=" ")
            else:
                print("_", end=" ")

        print()

        letras.append(resposta)

    if erros == 5:
        print("voce perdeu")
    else:
        print(f"parabéns a palavra era {palavra}!")

jogar()
