#include <GL/glut.h>
#include <math.h>

// Variáveis globais
float anguloRoda = 0.0f;
bool movimentoAtivo = true; // Determina se a Roda gigante está girando ou não
float anguloCabineBalanço = 0.0f;  // Controla o balanço das cabines
float velocidadeBalanço = 0.2f;  // Controla a velocidade de oscilação das cabines
bool direcaoBalanço = true;  // Alterna a direção do balanço

float anguloAzimute = 0.0f;  // Ângulo para mover a câmera ao redor da roda (horizontal)
float anguloElevação = 0.0f;  // Ângulo para inclinar a câmera para cima/baixo (vertical)
float distanciaCamera = 6.0f;  // Distância da câmera para a roda

void desenhaJanela() {
    glColor4f(0.5, 0.8, 1.0, 0.5); // cor azul claro com 50% de opacidade

    glBegin(GL_QUADS);
      glVertex3f(-0.2, -0.15, 0.0);
      glVertex3f( 0.2, -0.15, 0.0);
      glVertex3f( 0.2,  0.15, 0.0);
      glVertex3f(-0.2,  0.15, 0.0);
    glEnd();
}

void desenhaJanelasCabine() {
    // Janela frontal
    glPushMatrix();
      glTranslatef(0.0, 0.18, 0.2); // posiciona na frente da cabine
      desenhaJanela();
    glPopMatrix();

    // Janela traseira
    glPushMatrix();
      glTranslatef(0.0, 0.18, -0.2); // posiciona atrás da cabine
      glRotatef(180, 0, 1, 0);  // Rotaciona 180 graus em torno do eixo Y para manter a orientação correta
      desenhaJanela();
    glPopMatrix();

    // Janela lateral esquerda
    glPushMatrix();
      glTranslatef(-0.2, 0.18, 0.0); // posiciona à esquerda
      glRotatef(-90, 0, 1, 0);  // Rotaciona -90 graus em torno do eixo Y
      desenhaJanela();
    glPopMatrix();

    // Janela lateral direita
    glPushMatrix();
      glTranslatef(0.2, 0.18, 0.0); // posiciona à direita
      glRotatef(90, 0, 1, 0);   // Rotaciona 90 graus em torno do eixo Y
      desenhaJanela();
    glPopMatrix();
}

// Função para desenhar uma cabine com cor
void desenhaCabine(float r, float g, float b) {
    // Corpo principal da cabine
    glPushMatrix();
      glColor3f(r, g, b);
      glScalef(1.0, 0.6, 1.0);  // Escala para formar um retângulo
      glutSolidCube(0.45);
    glPopMatrix();
    
    // Teto ou capota da cabine
    glPushMatrix();
      glTranslatef(0.0, 0.3, 0.0); // Move para a parte superior
      glColor3f(r * 0.8, g * 0.8, b * 0.8); // Um tom um pouco diferente para diferenciar o teto
      glScalef(1.0, 0.15, 1.0);
      glutSolidCube(0.45);
    glPopMatrix();
    
    // Janelas da cabine
    desenhaJanelasCabine();
}

void defineCorMetalica() {
    // Define propriedades metálicas
    float matAmbiente[] = {0.3f, 0.3f, 0.3f, 1.0f};  // Cor ambiente
    float matDifusa[] = {0.7f, 0.7f, 0.7f, 1.0f};  // Cor difusa (cinza metálico)
    float matEspecular[] = {1.0f, 1.0f, 1.0f, 1.0f};  // Reflexão especular (brilho)
    float brilho = 50.0f;  // Quanto maior, mais brilhante

    // Aplica as propriedades de material
    glMaterialfv(GL_FRONT, GL_AMBIENT, matAmbiente);
    glMaterialfv(GL_FRONT, GL_DIFFUSE, matDifusa);
    glMaterialfv(GL_FRONT, GL_SPECULAR, matEspecular);
    glMaterialf(GL_FRONT, GL_SHININESS, brilho);
}

void desenhaEixoCentral(){
    GLUquadric* quadratic = gluNewQuadric();

    // Desenha Eixo
    glPushMatrix();
        glColor3f(0.5f, 0.5f, 0.5f);  // Cor metálica mais escura para o eixo
        glTranslatef(0.0, 0.0, -0.41);
        glRotatef(90.0f, 0.0f, 0.0f, 1.0f);  // Alinha o cilindro no eixo Z
        gluCylinder(quadratic, 0.1, 0.1, 0.81, 20, 10);  // Eixo com raio 0.1 e altura 0.3
    glPopMatrix();

    // Desenha a tampa inferior
    glPushMatrix();
        glTranslatef(0.0f, 0.0f, -0.41f);  // Coloca a tampa inferior na posição correta
        gluDisk(quadratic, 0.0f, 0.1, 20, 20); // Disco com o raio da base
    glPopMatrix();

    // Desenha a tampa superior
    glPushMatrix();
        glTranslatef(0.0f, 0.0f, 0.4f);  // Coloca a tampa inferior na posição correta
        gluDisk(quadratic, 0.0f, 0.1, 20, 20); // Disco com o raio da base
    glPopMatrix();

    gluDeleteQuadric(quadratic);
}

void desenhaAros(){
    glColor3f(0.7f, 0.7f, 0.7f); // cor metalica para os aros
    
    // Desenha o primeiro aro (frontal)
    glPushMatrix();
        glTranslatef(0.0f, 0.0f, 0.3f); // Leve translação no eixo Z
        glutSolidTorus(0.05, 2.0, 20, 60);
    glPopMatrix();

    // Desenha o segundo aro (traseiro)
    glPushMatrix();
        glTranslatef(0.0f, 0.0f, -0.3f); // Leve translação no eixo Z, na direção oposta
        glutSolidTorus(0.05, 2.0, 20, 60);
    glPopMatrix();
}

void desenhaCabosdeAco(float angulo){
    glPushMatrix();
        // Frente
        glRotatef(angulo, 0.0f, 0.0f, 1.0f);
        glTranslatef(0.0, 0.0, 0.3);
        glScalef(0.5f, 5.6f, 0.5f);  // Faz uma haste fina e alongada
        glColor3f(0.7f, 0.7f, 0.7f); // Cor metálica
        glRotatef(90, 1.0f, 0.0f, 0.0f); // Rotaciona o cilindro
        // Cria uma quadrica para desenhar o cilindro
        GLUquadric* quadrica = gluNewQuadric();
        gluCylinder(quadrica, 0.05, 0.05, 0.35, 20, 10);  // Cilindro fino (raio 0.05, altura 0.3)
        // Libera a memória alocada pela quadrica
        gluDeleteQuadric(quadrica);

        // fundo
        glTranslatef(0, -1.2, -0.1);
        glScalef(1.0f, 1.0f, 1.3f);  // Faz uma haste fina e alongada
        glColor3f(0.7f, 0.7f, 0.7f); // Cor metálica
        glRotatef(90, 0.0f, 0.0f, 1.0f); // Rotaciona o cilindro
        // Cria uma quadrica para desenhar o cilindro
        GLUquadric* quadrica0 = gluNewQuadric();
        gluCylinder(quadrica0, 0.05, 0.05, 0.35, 20, 10);  // Cilindro fino (raio 0.05, altura 0.3)
        // Libera a memória alocada pela quadrica
        gluDeleteQuadric(quadrica0);
    glPopMatrix();
}

void desenhaEixoCabines(){
    glPushMatrix();
        glTranslatef(0.0, 0.0, -0.3);
        glColor3f(0.7f, 0.7f, 0.7f); // Cor metálica
        GLUquadric* quadrica1 = gluNewQuadric();    // Cria uma quadrica para desenhar o cilindro
        gluCylinder(quadrica1, 0.05, 0.05, 0.6, 20, 10);  // Cilindro fino (raio 0.05, altura 0.3)
        gluDeleteQuadric(quadrica1);    // Libera a memória alocada pela quadrica
    glPopMatrix();
}

// Função para desenhar a roda e posicionar as cabines
void desenhaRoda() {
    // Define o reflexo metálico
    defineCorMetalica();
    // Desenha os aros da roda gigante
    desenhaAros();
    // Desenha o eixo central da roda gigante (cilindro no centro)
    desenhaEixoCentral();

    const int numCabines = 10;
    for (int i = 0; i < numCabines; i++) {
        float angulo = i * (360.0f / numCabines);
        
        // Desenha uma haste que conecta os aros ao eixo
        desenhaCabosdeAco(angulo);        

        glPushMatrix();
            glRotatef(angulo, 0.0f, 0.0f, 1.0f);
            glTranslatef(2.0, 0.0, 0.0);
            
            // Aplica o balanço nas cabines antes de desenhá-las
            glRotatef(anguloCabineBalanço, 0.0f, 0.0f, 1.0f);

            glRotatef(-angulo, 0.0f, 0.0f, 1.0f);
            glRotatef(-anguloRoda, 0, 0, 1); // Mantém as cabines na vertical

            // Desenha uma haste que conecta a cabine aos aros
            desenhaEixoCabines();           
        
            switch(i) {
                case 0: desenhaCabine(0.0f, 1.0f, 1.0f); break; // ciano
                case 1: desenhaCabine(0.0f, 1.0f, 0.0f); break; // verde
                case 2: desenhaCabine(0.0f, 0.0f, 1.0f); break; // azul
                case 3: desenhaCabine(1.0f, 1.0f, 0.0f); break; // amarelo
                case 4: desenhaCabine(0.6f, 0.1f, 0.6f); break; // roxo
                case 5: desenhaCabine(1.0f, 0.0f, 1.0f); break; // rosa
                case 6: desenhaCabine(0.0f, 1.0f, 0.0f); break; // verde
                case 7: desenhaCabine(0.0f, 0.0f, 1.0f); break; // azul
                case 8: desenhaCabine(1.0f, 0.5f, 0.0f); break; // laranja
                case 9: desenhaCabine(1.0f, 1.0f, 0.0f); break; // amarelo
            }
        glPopMatrix();
    }
}

void desenhaPe(GLfloat p) {
    glPushMatrix();
        glTranslatef(0.0f, -2.6f, p); // Posiciona o pé
        glScalef(3.5f, 0.2f, 0.4f); // Faz um paralelepípedo para representar o pé
        glutSolidCube(1.0);
    glPopMatrix();
}

void desenhaColunasBase(GLfloat rot1, GLfloat rot2, GLfloat transl1){
    glPushMatrix();
        glTranslatef(0.0f, 0.0f, transl1);  // Translada para o lado esquerdo e para baixo
        glRotatef(rot1, 1.0f, 0.0f, 0.0f);  // Rotação 1
        glRotatef(rot2, 0.0f, 1.0f, 0.0f);  // Rotacão 2
        
        GLUquadric* quadricaBase1 = gluNewQuadric();
        gluCylinder(quadricaBase1, 0.1, 0.1, 3.0, 20, 10);  // Cilindro com altura de 3.0
        gluDeleteQuadric(quadricaBase1);
    glPopMatrix();
}

void desenhaBase() {
    glColor3f(0.5f, 0.5f, 0.5f);  // Cor para a base
    desenhaPe(0.75);    // Pé direito
    desenhaPe(-0.75);   // Pé esquerdo

    // Base frontal
    desenhaColunasBase(80.0, 30.0, 0.3);    // Desenha o primeiro cilindro (perna da base)
    desenhaColunasBase(80.0, -30.0, 0.3);   // Desenha o segundo cilindro (perna da base)
    
    // Base traseira
    desenhaColunasBase(100.0, 30.0, -0.3);  // Desenha o primeiro cilindro (perna da base)
    desenhaColunasBase(100.0, -30.0, -0.3); // Desenha o segundo cilindro (perna da base)
}


// Função de renderização da cena
void display() {
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glLoadIdentity();

    // Converte os ângulos esféricos para coordenadas cartesianas para controlar a posição da câmera
    float cameraX = distanciaCamera * cos(anguloElevação) * sin(anguloAzimute);
    float cameraY = distanciaCamera * sin(anguloElevação);  // Controla a altura (elevação)
    float cameraZ = distanciaCamera * cos(anguloElevação) * cos(anguloAzimute);

    // Configuração da câmera
    gluLookAt(cameraX, cameraY, cameraZ,   // Posição da câmera com base nos ângulos
              0.0, 0.0, 0.0,   // Para onde a câmera aponta (centro da roda)
              0.0, 1.0, 0.0);  // Vetor "up" (mantido fixo no eixo Y)

    glPushMatrix();
        glRotatef(anguloRoda, 0.0f, 0.0f, 1.0f);
        desenhaRoda();
    glPopMatrix();

    desenhaBase();

    glutSwapBuffers();
}

void inicializaIluminacao() {
    glEnable(GL_LIGHTING);  // Habilita o uso da iluminação

    // Configuração da luz ambiente
    float luzAmbiente[] = {0.2f, 0.2f, 0.2f, 1.0f};
    float luzDifusa[] = {0.8f, 0.8f, 0.8f, 1.0f};  // Luz branca suave
    float luzEspecular[] = {1.0f, 1.0f, 1.0f, 1.0f};  // Reflexão especular (brilho)
    float posicaoLuz[] = {5.0f, 5.0f, 10.0f, 1.0f};  // Posição da luz

    // Configuração da luz 0 (fonte de luz)
    glLightfv(GL_LIGHT0, GL_AMBIENT, luzAmbiente);
    glLightfv(GL_LIGHT0, GL_DIFFUSE, luzDifusa);
    glLightfv(GL_LIGHT0, GL_SPECULAR, luzEspecular);
    glLightfv(GL_LIGHT0, GL_POSITION, posicaoLuz);

    glEnable(GL_LIGHT0);  // Habilita a fonte de luz 0

    // Configuração global do ambiente da cena
    float luzGlobalAmbiente[] = {0.3f, 0.3f, 0.3f, 1.0f};
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, luzGlobalAmbiente);

    // Habilita a definição automática de material com a função glColor
    glEnable(GL_COLOR_MATERIAL);
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE);

    // Ativa o teste de profundidade
    glEnable(GL_DEPTH_TEST);
}


// Função de animação
void timer(int value) {
    if (movimentoAtivo) {
        // Atualiza o ângulo de rotação da roda
        anguloRoda += 0.5f;
        if (anguloRoda > 360.0f)
            anguloRoda -= 360.0f;

        // Atualiza o balanço das cabines
        if (direcaoBalanço) {
            anguloCabineBalanço += velocidadeBalanço;
            if (anguloCabineBalanço > 5.0f) direcaoBalanço = false;  // Limita o ângulo do balanço
        } else {
            anguloCabineBalanço -= velocidadeBalanço;
            if (anguloCabineBalanço < -5.0f) direcaoBalanço = true;
        }

        // Reinicia a velocidade do balanço quando o movimento é reativado
        if (velocidadeBalanço < 0.2f) {
            velocidadeBalanço = 0.2f;  // Restabelece a velocidade do balanço ao valor inicial
        }
    } else {
        // Se o movimento for pausado, desacelere o balanço até ele parar suavemente
        if (velocidadeBalanço > 0.0f) {
            velocidadeBalanço -= 0.0005f;  // Reduz a velocidade do balanço gradualmente, mais lentamente
        }
        
        // Continua atualizando o ângulo de balanço mesmo após a desaceleração
        if (direcaoBalanço) {
            anguloCabineBalanço += velocidadeBalanço;
            if (anguloCabineBalanço > 5.0f) direcaoBalanço = false;
        } else {
            anguloCabineBalanço -= velocidadeBalanço;
            if (anguloCabineBalanço < -5.0f) direcaoBalanço = true;
        }
    }

    // Se a velocidade ficar muito baixa, pare o balanço
    if (velocidadeBalanço < 0.01f) {
        velocidadeBalanço = 0.0f;
    }

    glutPostRedisplay();
    glutTimerFunc(16, timer, 0);  // Aproximadamente 60 FPS
}

// Função para tratar entrada do teclado
void keyboard(unsigned char key, int x, int y) {
    // Rotaciona a câmera ao redor da roda gigante (horizontal)
    if (key == 'a' || key == 'A') {
        anguloAzimute -= 0.05f;  // Move a câmera para a esquerda (ânguloAzimute)
    }
    if (key == 'd' || key == 'D') {
        anguloAzimute += 0.05f;  // Move a câmera para a direita (ânguloAzimute)
    }

    // Inclina a câmera para cima/baixo (vertical)
    if (key == 'w' || key == 'W') {
        anguloElevação += 0.05f;  // Inclina a câmera para cima
        if (anguloElevação > 1.5f) anguloElevação = 1.5f;  // Limita a rotação para cima
    }
    if (key == 's' || key == 'S') {
        anguloElevação -= 0.05f;  // Inclina a câmera para baixo
        if (anguloElevação < -1.5f) anguloElevação = -1.5f;  // Limita a rotação para baixo
    }

    // Aproxima ou afasta a câmera
    if (key == 'e' || key == 'E' || key == '=') {
        distanciaCamera -= 0.2f;  // Aproxima a câmera
        if (distanciaCamera < 2.0f) distanciaCamera = 2.0f;  // Limite mínimo de aproximação
    }
    if (key == 'q' || key == 'Q' || key == '-') {
        distanciaCamera += 0.2f;  // Afasta a câmera
    }

    // Parar o movimento da roda com 'L'
    if (key == 'l' || key == 'L') {
        movimentoAtivo = !movimentoAtivo;
    }
}

// Função reshape para configurar a viewport e a projeção
void reshape(int w, int h) {
    if (h == 0) h = 1; // Evita divisão por zero
    glViewport(0, 0, w, h);
    
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluPerspective(45.0, (double)w/h, 1.0, 100.0);
    
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
}

// Inicialização do OpenGL, iluminação e configurações de material
void inicializa() {
    glEnable(GL_DEPTH_TEST);
    glEnable(GL_LIGHTING);
    glEnable(GL_LIGHT0);

    // Habilita o uso de glColor para definir os materiais
    glEnable(GL_COLOR_MATERIAL);
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE);
    
    float luzAmbiente[] = {0.2f, 0.2f, 0.2f, 1.0f};
    float luzDifusa[]   = {0.8f, 0.8f, 0.8f, 1.0f};
    float posicaoLuz[]  = {5.0f, 5.0f, 10.0f, 1.0f};
    glLightfv(GL_LIGHT0, GL_AMBIENT,  luzAmbiente);
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  luzDifusa);
    glLightfv(GL_LIGHT0, GL_POSITION, posicaoLuz);

    inicializaIluminacao();  // Chama a configuração da iluminação
    glClearColor(0.0, 0.0, 0.0, 1.0); // Fundo preto
}

int main(int argc, char** argv) {
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
    glutInitWindowSize(800,600);
    glutCreateWindow("Roda Gigante");
    
    inicializa();
    
    glutDisplayFunc(display);
    glutReshapeFunc(reshape);
    glutTimerFunc(0, timer, 0);
    glutKeyboardFunc(keyboard);
    glutMainLoop();
    return 0;
}
