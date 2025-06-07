import os
import sys
import shlex
import subprocess
import threading

# Flag global de controle
sair = False

def executar_comando(comando):
    global sair
    if not comando:
        return

    tokens = shlex.split(comando)
    if not tokens:
        return

    cmd = tokens[0]
    args = tokens[1:]

    if cmd == "exit":
        sair = True
        return

    elif cmd == "pwd":
        print(os.getcwd())

    elif cmd == "cd":
        if len(args) != 1:
            print("Uso correto: cd <caminho>")
        else:
            try:
                os.chdir(args[0])
            except FileNotFoundError:
                print("no such file or directory")

    elif cmd == "cat":
        if len(args) != 1:
            print("Uso correto: cat <arquivo>")
        else:
            try:
                with open(args[0], 'r') as f:
                    print(f.read(), end="")
            except FileNotFoundError:
                print("Arquivo não encontrado.")

    elif cmd == "ls":
        print("\n".join(os.listdir()))

    elif cmd == "echo":
        print(" ".join(args))

    else:
        try:
            subprocess.run([cmd] + args)
        except FileNotFoundError:
            print(f"{cmd}: comando não encontrado")

def tratar_redirecionamento(comando):
    if ">" in comando:
        partes = comando.split(">")
        cmd = partes[0].strip()
        destino = partes[1].strip()

        try:
            with open(destino, 'w') as f:
                tokens = shlex.split(cmd)
                if not tokens:
                    return
                nome = tokens[0]
                args = tokens[1:]

                if nome == "echo":
                    f.write(" ".join(args) + "\n")
                elif nome == "cat":
                    if len(args) != 1:
                        f.write("Uso correto: cat <arquivo>\n")
                    else:
                        try:
                            with open(args[0], 'r') as arq:
                                f.write(arq.read())
                        except FileNotFoundError:
                            f.write("Arquivo não encontrado.\n")
                elif nome == "pwd":
                    f.write(os.getcwd() + "\n")
                elif nome == "ls":
                    f.write("\n".join(os.listdir()) + "\n")
                else:
                    resultado = subprocess.run([nome] + args, stdout=f, stderr=subprocess.PIPE, text=True)
                    if resultado.returncode != 0:
                        f.write(resultado.stderr)

        except Exception as e:
            print(f"Erro ao redirecionar: {e}")
    else:
        executar_comando(comando)

def executar_em_thread(comando):
    thread = threading.Thread(target=tratar_redirecionamento, args=(comando,))
    thread.start()
    return thread

def interpretar_linha(linha):
    sequencias = [seq.strip() for seq in linha.strip().split(";")]
    for seq in sequencias:
        paralelos = [par.strip() for par in seq.split("&")]
        threads = []
        for p in paralelos:
            thread = executar_em_thread(p)
            threads.append(thread)
        for t in threads:
            t.join()

def shell_loop():
    global sair
    while not sair:
        try:
            linha = input("> ")
            interpretar_linha(linha)
        except EOFError:
            print("\nSaindo.")
            break
        except KeyboardInterrupt:
            print("\nUse 'exit' para sair.")

if __name__ == "__main__":
    shell_loop()
