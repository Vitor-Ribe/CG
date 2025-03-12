# Nome do compilador
CC = g++-13

# Flags de compilação
CFLAGS = -g -Wall

# Flags de linkagem para as bibliotecas OpenGL, GLU e GLUT
LDFLAGS = -lglut -lGLU -lGL

# Nome do arquivo fonte e do executável
SRC = skeleton.cpp
OUT = skeleton

# Regra padrão: compilar o executável
all: $(OUT)

$(OUT): $(SRC)
	$(CC) $(CFLAGS) -o $(OUT) $(SRC) $(LDFLAGS)

# Target para executar o programa
run: $(OUT)
	./$(OUT)

# Limpa os arquivos gerados
clean:
	rm -f $(OUT)
