import os 

def menu():
    print("Menu".center(65,"*"))
    print("Qual seu Sistema Operacional ?")
    print("\t1 - Linux")
    print("\t2 - Windows")
    print("*"*65)

def linux():
    print("*"*65)
    print("Linux".center(65))
    print("\t1 - Printar o IP")
    print("\t2 - Pingar o Google")
    print("\t3 - Printar dados da maquina")
    print("\t4 - Sair")    
    print("*"*65)

def win():
    print("*"*65)
    print("Windows".center(65))
    print("\t1 - Printar o IP")
    print("\t2 - Pingar o Google")
    print("\t3 - Printar o hostname da maquina")
    print("\t4 - Sair")    
    print("*"*65)


def main():
    escolha = ""
    menu()
    escolha = input("Qual sua escolha? ")
    if escolha == "1":
        linux()
        while True:
            new = input("Escolha uma opção: ")
            if new == "1":
                print(os.system("ifconfig"))
                linux()
            elif new =="2":
                print(os.system("ping 8.8.8.8 -c 4"))
                linux()
            elif new == "3":
                print(os.system("neofetch"))
                linux()
            elif new == "4":
                print("Fim do programa")
                break

    elif escolha == "2":
        win()
        while True:
            new = input("Escolha uma opção: ")
            if new == "1":
                print(os.system("ipconfig"))
            elif new =="2":
                print(os.system("ping 8.8.8.8 "))
            elif new == "3":
                print(os.system("hostname"))
            elif new == "4":
                print("Fim do programa")
                break


main()