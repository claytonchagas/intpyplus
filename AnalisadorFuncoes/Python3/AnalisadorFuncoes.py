# -*- coding: utf-8 -*-
import ast
import astor
import os
import sys

#Função principal
def main():
    if(exibeMsgConfirmacao()):

        #Testando se na chamada do programa foi especificada a pasta de saída
        if(sys.argv[1] == "-o"):
            #Pasta em que serão guardados os arquivos analisados por este programa
            pastaOutput = sys.argv[2]
            indicePrimeiroArquivo = 3

        else:
            pastaOutput = __file__ + "/../ExperimentosAnalisados"
            pastaOutput = os.path.abspath(pastaOutput)
            indicePrimeiroArquivo = 1

        #Criando pasta de saída
        if not(criaPastaOutput(pastaOutput)):
            sys.exit("Erro ao tentar criar pasta de output!")
        
        print()
        for arquivo in sys.argv[indicePrimeiroArquivo:]:
            print("Processando arquivo \"" + arquivo + "\" ...")
            print("Gerando AST do código ...")

            #Gerando AST a partir do código original
            arvoreAst = geraAstCodigo(arquivo)

            if(arvoreAst != None):
                #Analisando nós da AST e classificando as funções
                analisadorArvoreAST = AnalisadorArvoreAST(arvoreAst)
                novaArvoreAst = analisadorArvoreAST.analisar()
                               
                #Gerando código fonte a partir da nova AST
                #e salvando em um arquivo ".py"
                print("Gerando novo código a partir da AST ...")
                if not(geraCodigoAst(novaArvoreAst, arquivo, pastaOutput)):
                    sys.exit("Erro ao tentar salvar código com as classificações das funções!")
                
            print()
                
        print("Todos os arquivos foram analisados.")
        print("Os resultados podem ser encontrados na pasta " + pastaOutput + ".")
        return 0

def exibeMsgConfirmacao():
    print("Atenção: O(s) script(s) Python a ser(em) analisado(s) deve(m) preencher os seguintes requisitos:")
    print("         i)Não devem conter funções já marcadas com \"@deterministic\" nem comandos de importação para o módulo IntPy")
    print("        ii)Todas as importações devem ser feitas com o comando \"import\" seguido dos nomes dos módulos, não podendo ser utilizado o comando \"as\" para modificar o nome dos mesmos.")
    print("       iii)Todas as funções que utilizam variáveis globais em seu interior devem sempre apresentar o comando \"global\", mesmo que seu uso não seja obrigatório de acordo com a sintaxe do interpretador Python utilizado")
    print("        iv)Caso uma função manipule arquivos externos, o arquivo deve ser aberto, manipulado completamente e fechado dentro dessa função")
    print("         v)Não devem, em uma mesma linha, conter chamadas a mais de uma função. Ex.: \"variavel = funcaoA().funcaoB()\"")
    print("        vi)Todos os métodos de classes devem ser implementados com o marcador \"@staticmethod\"")
    print("       vii)Todas as chamadas a métodos de uma classe (estáticos) devem ser feitas através do nome da classe, jamais pelo nome da instância.")
    print("      viii)Dentro de um mesmo script, é possível utilizar um mesmo nome para mais de uma função/método declarado. Todavia, as anotações geradas por este analisador, no arquivo de saída, podem se tornar ambíguas pois, ao se referirem às funções declaradas dentro do script, citam apenas seus nomes")
    print("        ix)Somente os métodos de instância declarados no script podem utilizar a estrutura \"self.nomeFuncao()\", a qual sempre será interpretada por este analisador como uma chamada a outro método da instância")
    print("         x)Este analisador aceita apenas funções declarados com \"def\" e retornadas por instruções \"return\"")
    print("        xi)Todas as funções, objetos, classes, métodos, atributos e módulos importados devem possuir nomes distintos. Este analisador aceita apenas que funções e métodos tenham o mesmo nome caso não sejam definidos no mesmo escopo.")
    print("       xii)Todas as funções declaradas devem, obrigatoriamente, conter uma instrução de return no escopo mais externo da função, a não ser que se deseje retornar None")
    print("")

    print("Observações:")
    print("         i)Como a linguagem Python é dinamicamente tipada, este analisador não é capaz de determinar o tipo que cada variável assumirá durante a execução do programa. Logo, o usuário deve verificar em seu código se as funções declaradas não ferem a nenhuma das limitações explicitadas a seguir. As funções que contradizem a essas regras devem ser classificadas como não funcionam com o IntPy, independente da classificação dada pelo analisador ao final de sua execução:")
    print("               1)As tuplas podem ser passadas como parâmetros e retornadas por funções;")
    print("               2)As listas e dicionários podem ser passados como parâmetros/retornados para/por funções. Todavia, no caso de serem passados como parâmetros, não é possível alterar seus elementos dentro da função pois, o IntPy resultará em erro;")
    print("               3)O retorno de uma função não pode ser uma chamada para outra função. Caso seja, o IntPy resultará em erro.")
    print("               4)Objetos não podem ser passados como parâmetros para funções. Contudo, é possível retornar objetos instanciados dentro de uma função desde que o objeto retornado não tenha chamado nenhum método não determinístico dentro da função.")
    print("               Obs.: Os métodos dos objetos são sempre marcados como não funcionam com o IntPy porque não podem ser marcados como determinísticos diretamente. Entretanto, se esses métodos não são não determinísticos e são chamados dentro de outra função essa função, se não for não determinística pode ser marcada como determinística. A análise dos métodos dos objetos deve ser feita pelo usuário.")
    print("               5)Classes e funções não podem ser passados por parâmetro para funções nem assinaturas desses elementos, definidas dentro de funções, podem ser retornadas por elas.")
    print("        ii)Em todas as funções que manipulam objetos, sejam eles instâncias de classes definidas dentro do script ou instâncias de classes importadas com o comando \"import\", o usuário deve verificar se, no código da função, são chamados métodos que não são determinísticos. Em caso afirmativo, essas funções devem ser marcadas como não determinísticas.")
    print("       iii)Para que o cache do IntPy funcione corretamente, a função armazenada não pode, em hipótese nenhuma, retornar None. Quando este analisador detecta em uma função o uso de instruções \"return\", \"return None\" ou a ausência de instruções \"return\", a função é marcada como \"Não funciona com o IntPy\". Contudo, existem outros casos em que uma função pode retornar None. Ex.: A função retorna uma variável(ou chama outra função) que, em alguns casos, pode receber o valor None. Logo, o usuário sempre deve verificar, após executar esse analisador, se todas as funções marcadas como determinísticas sempre retornam valores diferentes de None. Caso algumas dessas funções possam retornar None, estas não devem ser usadas com o IntPy.")
    print("        iv)A fim de diminuir o tempo gasto para realizar a análise das funções, este programa verifica cada função apenas até encontrar o primeiro indício que permita classificá-la corretamente. Assim sendo, no arquivo gerado pelo analisador, os motivos explicitados para classificar as funções podem não ser os únicos que as façam ser classificadas desse modo.")
    print("         v)Para que o script possa ser analisado corretamente, é fundamental que, antes de rodar este analisador, o usuário teste se o programa está sendo executado com êxito pelo interpretador Python. Este analisador só funcionará corretamente, caso o script analisado não contenha nenhum tipo de erro.")
    print("        vi)Este analisador está em sua versão inicial. Desse modo, ainda é possível que contenha erros em suas análises. Assim, é recomendável que o usuário, sempre que utilizar esse software, verifique todas as funções classificadas como determinísticas, a fim de evitar erros em seus scripts.")

    while(True):
        resposta = input("O(s) script(s) atende(m) às condições acima:[s/n] ")

        if(resposta == "s"):
            return True
        elif(resposta == "n"):
            return False
        else:
            print("Resposta inválida! Tente novamente!\n")

def geraAstCodigo(nomeArquivo):
    #Testando se o nome do arquivo termina em ".py"

    #Preciso testar se ("." in arquivo) porque senão um arquivo chamado "py"
    #seria considerado válido
    if("." in nomeArquivo) and (nomeArquivo.split(".")[-1] == "py"):
        try:
            #Abrindo o arquivo
            arquivo = open(nomeArquivo, "r")

        #Neste caso, ocorreu erro ao tentar abrir o arquivo
        except:
            print("Erro ao tentar abrir o arquivo!")
            print("Verifique se o arquivo realmente existe.")
            return None
        
        #Neste caso, não houve ao abrir o arquivo
        else:
            try:
                #Gerando AST a partir do código original
                return ast.parse(arquivo.read())

            except:
                print("Erro ao tentar gerar AST a partir do código do arquivo!")
                print("Verifique se esse script Python está escrito corretamente.")
                return None

    #Arquivo com extensão inválida
    else:
        print("Erro: Arquivo Inválido!")
        print("Esse programa só consegue analisar arquivos com extensão \".py\".")
        
        return None

def criaPastaOutput(pastaOutput):
    try:
        #Criando pasta para armazenar os arquivos analisados
        if not(os.path.exists(pastaOutput)):
            os.mkdir(pastaOutput)
        return True
    
    except:
        print("Erro ao tentar criar pasta para armazenar os arquivos!")
        return False

def geraCodigoAst(arvoreAst, nomeArquivo, pastaOutput):
    
    #Gerando código fonte a partir da AST
    codigoFonte = astor.to_source(arvoreAst)
    
    try:
        #Separando o nome do arquivo do path passado por parâmetro
        #Tentei utilizar os.sep() ao invés de "/" mas ocorria erro no interpretador Python
        nomeArquivo = nomeArquivo.split("/")[-1]
        
        #Escrevendo código fonte em um arquivo
        arquivo = open(os.path.join(pastaOutput, nomeArquivo), "w")
        arquivo.write(codigoFonte)
        arquivo.close()        
        return True

    except:
        print("Erro ao tentar criar arquivo de saída!")
        return False

class AnalisadorArvoreAST():
    def __init__(self, arvoreAst):
        self.arvoreAst = arvoreAst
        self.classificacaoFuncoesMetodos = []
    
    def analisar(self):

        print("Buscando informações na AST ...")

        #Buscando nós FunctionDef na AST que correspondem às funções que o
        #programador criou no código original
        buscadorFuncoesClassesMetodos = BuscadorFuncoesClassesMetodos(self.arvoreAst)
        buscadorFuncoesClassesMetodos.buscaFuncoesClassesMetodos()

        print("Gerando grafo de funções ...")

        #Criando grafo dos nós "ast.FunctionDef"
        #Cada instancia de VerticeGrafo será uma função sendo armazenada em self.dado
        #A lista self.verticesLigados conterá todas as funções que chamam self.dado
        geradorGrafoFuncoes = GeradorGrafoFuncoes(self.arvoreAst,
                                buscadorFuncoesClassesMetodos.getFuncoes(),
                                buscadorFuncoesClassesMetodos.getMetodosClasse(),
                                buscadorFuncoesClassesMetodos.getMetodosInstancia())
        geradorGrafoFuncoes.geraGrafoFuncoes()
        
        #Criando elementos da lista "self.classificacaoFuncoesMetodos"
        #Ela contera os objetos "Funcao" das funções e dos métodos
        #declarados na AST
        dicionarioFuncoes = buscadorFuncoesClassesMetodos.getFuncoes()
        for nomeFuncao in dicionarioFuncoes:
            self.classificacaoFuncoesMetodos.append(Funcao(nomeFuncao, dicionarioFuncoes[nomeFuncao]))
                
        dicionarioMetodosClasse = buscadorFuncoesClassesMetodos.getMetodosClasse()
        for nomeMetodoClasse in dicionarioMetodosClasse:
            self.classificacaoFuncoesMetodos.append(Funcao(nomeMetodoClasse, dicionarioMetodosClasse[nomeMetodoClasse]))

        dicionarioMetodosInstancia = buscadorFuncoesClassesMetodos.getMetodosInstancia()
        for nomeMetodoInstancia in dicionarioMetodosInstancia:
            self.classificacaoFuncoesMetodos.append(Funcao(nomeMetodoInstancia, dicionarioMetodosInstancia[nomeMetodoInstancia]))
        
        funcoesProcessar = list(dicionarioFuncoes.values()) + list(dicionarioMetodosClasse.values()) + list(dicionarioMetodosInstancia.values())
                
        print("Classificando funções não determinísticas ...")

        #Verificando quais funções de "self.classificacaoFuncoesMetodos"
        #não são determinísticas
        classificadorFuncoesND = ClassificadorFuncoesND(funcoesProcessar.copy(), buscadorFuncoesClassesMetodos.getModulosImportados().copy())
        classificadorFuncoesND.classificaFuncoesND()
        
        #Atualizando "self.classificacaoFuncoesMetodos" com uma parte das
        #funções que não são determinísticas
        dicionarioFuncoesND = classificadorFuncoesND.getFuncoesND()
        for funcaoND in dicionarioFuncoesND:
            for funcao in self.classificacaoFuncoesMetodos:
                if(funcaoND == funcao.getDado()):
                    funcao.setClassificacao("ND")
                    funcao.setMotivoClassificacao(dicionarioFuncoesND[funcaoND])
                    break

        print("Classificando funções que chama funções não determinísticas ...")
        
        self.classificaFuncoesQueChamamFuncoesND(geradorGrafoFuncoes.getGrafoFuncoes())

        #Identificando funções e métodos ainda não classificados
        funcoesProcessar = []
        for funcao in self.classificacaoFuncoesMetodos:
            if(funcao.getClassificacao() == ""):
                funcoesProcessar.append(funcao.getDado())

        print("Buscando funções que não podem ser classificadas ...")

        #Verificando quais funções da AST não podem ser classificadas
        classificadorFuncoesNPSC = ClassificadorFuncoesNPSC(funcoesProcessar.copy(),
                                            buscadorFuncoesClassesMetodos.getModulosImportados())
        classificadorFuncoesNPSC.classificaFuncoesNPSC()
        
        #Identificando funções que não podem ser classificadas
        dicionarioFuncoesNPSC = classificadorFuncoesNPSC.getFuncoesNPSC()
        for funcaoNPSC in dicionarioFuncoesNPSC:
            for funcao in self.classificacaoFuncoesMetodos:
                #Não é necessário testar se essa função ainda não foi classificada porque isso
                #todas as funções analisadas não possuem classificação
                if(funcaoNPSC == funcao.getDado()):
                    funcao.setClassificacao("NPSC")
                    funcao.setMotivoClassificacao(dicionarioFuncoesNPSC[funcaoNPSC])
                    break

        print("Buscando funções que chamam funções que não podem ser classificadas ...")
        
        self.classificaFuncoesQueChamamFuncoesNPSC(geradorGrafoFuncoes.getGrafoFuncoes())

        #Identificando funções e métodos de classe ainda não classificados
        self.funcoesMetodosClasseNaoClassificados = {}
        for funcao in self.classificacaoFuncoesMetodos:
            if((funcao.getClassificacao() != "ND") and (funcao.getDado() not in dicionarioMetodosInstancia.values())):
                self.funcoesMetodosClasseNaoClassificados[funcao.getAssinaturaFuncao()] = funcao.getDado()
        
        print("Classificando funções que não funcionam com o IntPy ...")
        
        #Verificando quais funções da AST não funcionam com o IntPy
        classificadorFuncoesNF = ClassificadorFuncoesNF(self.arvoreAst, self.funcoesMetodosClasseNaoClassificados.copy())
        classificadorFuncoesNF.classificaFuncoesNF()

        #Atualizando "self.classificacaoFuncoesMetodos" com as funções que não funcionam no IntPy
        dicionarioFuncoesNF = classificadorFuncoesNF.getFuncoesNF()
        for funcaoNF in dicionarioFuncoesNF:
            for funcao in self.classificacaoFuncoesMetodos:
                #Não é necessário testar se a função já foi classificada como ND
                #porque todas as funções analisadas não tinham sido classificadas como ND
                #Não há importancia se a função estiver rotulada como NPSC pois dizer que
                #uma função NF é mais forte do que dizer que uma função NPSC
                if(funcaoNF == funcao.getDado()):
                    funcao.setClassificacao("NF")
                    funcao.setMotivoClassificacao(dicionarioFuncoesNF[funcaoNF])

        print("Classificando funções determinísticas ...")

        #Classificando as funções que ainda não foram classificadas como "determinísticas"
        for funcao in self.classificacaoFuncoesMetodos:
            if(funcao.getClassificacao() == ""):
                funcao.setClassificacao("D")

        print("Escrevendo nova AST com as classificações das funções ...")

        #Anotando na AST a classificação de cada uma das funções
        escritorAST =  EscritorAST(
                                                self.arvoreAst,
                                                buscadorFuncoesClassesMetodos.getClasses(),
                                                list(buscadorFuncoesClassesMetodos.getMetodosInstancia().values()),
                                                buscadorFuncoesClassesMetodos.getSuperClasses(),
                                                buscadorFuncoesClassesMetodos.getSuperFuncoes(),
                                                buscadorFuncoesClassesMetodos.getSuperMetodos(),
                                                self.classificacaoFuncoesMetodos)
        escritorAST.escreveImportacaoModuloIntPy()
        escritorAST.escreveClassificacaoFuncoesAST()

        #Atualizando árvore AST
        self.arvoreAst = escritorAST.getArvoreAst()

        return self.arvoreAst

    def classificaFuncoesQueChamamFuncoesND(self, grafoFuncoes):
        #Selecionando vértices do grafo classificados como não determinísticos
        verticesNaoProcessados = []
        for verticeGrafoFuncoes in grafoFuncoes.getVertices():
            for funcao in self.classificacaoFuncoesMetodos:
                if(funcao.getDado() == verticeGrafoFuncoes.getDado() and
                    funcao.getClassificacao() == "ND"):
                    verticesNaoProcessados.append(verticeGrafoFuncoes)
                    break

        verticesProcessadosFuncoesND = []
        while(verticesNaoProcessados != []):
            novosVerticesNaoProcessados = []
            for verticeGrafoFuncoes in verticesNaoProcessados:
                #Atualizando "verticesProcessadosFuncoesND"
                verticesProcessadosFuncoesND.append(verticeGrafoFuncoes)

                #Pegando a assinatura da função representada por "verticeGrafoFuncoes"
                nomeFuncaoChamada = ""
                for funcaoMetodo in self.classificacaoFuncoesMetodos:
                    if(verticeGrafoFuncoes.getDado() == funcaoMetodo.getDado()):
                        nomeFuncaoChamada = funcaoMetodo.getAssinaturaFuncao()

                        break
                
                for verticeLigado in verticeGrafoFuncoes.getVerticesLigados():
                    #Classificando as funções que chamam funções não determinísticas
                    #como funções não determinísticas
                    for funcao in self.classificacaoFuncoesMetodos:
                        if(funcao.getDado() == verticeLigado.getDado() and
                            funcao.getClassificacao() != "ND"):
                            
                            funcao.setClassificacao("ND")
                            motivoClassificacao = "Essa função chama a função \"" + nomeFuncaoChamada + "\" que não é determinística"
                            funcao.setMotivoClassificacao(motivoClassificacao)
                            
                            break
                    
                    #Verificando se as funções que chamam a função recém-classificada
                    #como não determinística já foram registrados como não determinísticas
                    if(verticeLigado not in verticesProcessadosFuncoesND):
                        novosVerticesNaoProcessados.append(verticeLigado)
            
            #Neste momento, todos os elementos de "verticesNaoProcessados" já foram
            #analisados. Então atualiza-se esse vetor com os novos vértices que precisam
            #ser analisados
            verticesNaoProcessados = novosVerticesNaoProcessados.copy()
    
    def classificaFuncoesQueChamamFuncoesNPSC(self, grafoFuncoes):
        #Selecionando vértices do grafo classificados como não determinísticos
        verticesNaoProcessados = []
        for verticeGrafoFuncoes in grafoFuncoes.getVertices():
            for funcao in self.classificacaoFuncoesMetodos:
                if(funcao.getDado() == verticeGrafoFuncoes.getDado() and
                    funcao.getClassificacao() == "NPSC"):
                    verticesNaoProcessados.append(verticeGrafoFuncoes)
                    break

        verticesProcessadosFuncoesNPSC = []
        while(verticesNaoProcessados != []):
            novosVerticesNaoProcessados = []
            for verticeGrafoFuncoes in verticesNaoProcessados:
                #Atualizando "verticesProcessadosFuncoesNPSC"
                verticesProcessadosFuncoesNPSC.append(verticeGrafoFuncoes)

                #Pegando a assinatura da função representada por "verticeGrafoFuncoes"
                nomeFuncaoChamada = ""
                for funcaoMetodo in self.classificacaoFuncoesMetodos:
                    if(verticeGrafoFuncoes.getDado() == funcaoMetodo.getDado()):
                        nomeFuncaoChamada = funcaoMetodo.getAssinaturaFuncao()
                        
                        break
                
                for verticeLigado in verticeGrafoFuncoes.getVerticesLigados():
                    #Classificando as funções que chamam funções que chamam FNCs
                    #como funções duvidosas
                    for funcao in self.classificacaoFuncoesMetodos:
                        if(funcao.getDado() == verticeLigado.getDado() and
                            funcao.getClassificacao() == ""):

                            funcao.setClassificacao("NPSC")
                            motivoClassificacao = "Essa função chama a função \"" + nomeFuncaoChamada + "\" que o analisador não é capaz de classificar"
                            funcao.setMotivoClassificacao(motivoClassificacao)

                            break

                    
                    #Verificando se as funções que chamam a função recém-classificada
                    #como duvidosa já foram registrados como não determinísticas
                    if(verticeLigado not in verticesProcessadosFuncoesNPSC):
                        novosVerticesNaoProcessados.append(verticeLigado)
            
            #Neste momento, todos os elementos de "verticesNaoProcessados" já foram
            #analisados. Então atualiza-se esse vetor com os novos vértices que precisam
            #ser analisados
            verticesNaoProcessados = novosVerticesNaoProcessados.copy()

class Funcao():
    def __init__(self, assinaturaFuncao, dado):
        self.dado = dado
        self.assinaturaFuncao = assinaturaFuncao
        self.classificacao = ""
        self.motivoClassificacao = ""
    
    def getDado(self):
        return self.dado

    def getClassificacao(self):
        return self.classificacao

    def getMotivoClassificacao(self):
        return self.motivoClassificacao
    
    def getAssinaturaFuncao(self):
        return self.assinaturaFuncao

    def setAssinaturaFuncao(self, assinaturaFuncao):
        self.assinaturaFuncao = assinaturaFuncao

    def setDado(self, dado):
        self.dado = dado

    def setClassificacao(self, classificacao):
        self.classificacao = classificacao

    def setMotivoClassificacao(self, motivoClassificacao):
        self.motivoClassificacao = motivoClassificacao

class BuscadorFuncoesClassesMetodos(ast.NodeVisitor):
    def __init__(self, arvoreAst):
        self.arvoreAst = arvoreAst
        self.modulosImportados = []
        
        self.funcoes = {}
        self.classes = []
        self.metodosInstancia = {}
        self.metodosClasse = {}

        self.superFuncoes = []
        self.superClasses = []
        self.superMetodos = []

    def buscaFuncoesClassesMetodos(self):
        #Neste percurso da AST, obteremos todas as funções declaradas e
        #todas as classes declaradas
        self.classeAtual = None
        self.nomeClasseAtual = ""
        self.funcaoAtual = None
        self.nomeFuncaoAtual = ""
        self.visit(self.arvoreAst)

    def visit_Import(self, node):
        if(node not in self.modulosImportados):
            self.modulosImportados.append(node)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        #Atualizando nome da classe e classe atuais
        nomeClasseAnterior = self.nomeClasseAtual
        if(self.nomeClasseAtual == ""):
            self.nomeClasseAtual = node.name
        else:
            self.nomeClasseAtual = self.nomeClasseAtual + "." + node.name
        
        classeAnterior = self.classeAtual
        self.classeAtual = node
        
        #Adicionando classe a "self.classes"
        self.classes.append(node)

        for no in node.body:
            #Verificando se há nós "ast.ClassDef" declarados dentro de "node"
            #Ou seja, verificando se "node" é uma superClasse
            if isinstance(no, ast.ClassDef):
                self.superClasses.append(node)
                break
            
            if(isinstance(no, ast.FunctionDef)):
                #Verificando se há nós "ast.FunctionDef" declarados dentro de "no"
                #Ou seja, verificando se "no" é um superMétodo
                for elemento in no.body:
                    if(isinstance(elemento, ast.FunctionDef)):
                        self.superMetodos.append(no)
                        break

                #Testando se a função declarada é um método de instância ou da classe
                metodoClasse = False
                for decorador in no.decorator_list:
                    if(decorador.id == "staticmethod"):
                        metodoClasse = True
                        break
                    
                if(not metodoClasse):
                    assinaturaMetodoInstancia = self.nomeClasseAtual + "." + no.name
                    self.metodosInstancia[assinaturaMetodoInstancia] = no

                else:
                    assinaturaMetodoClasse = self.nomeClasseAtual + "." + no.name
                    self.metodosClasse[assinaturaMetodoClasse] = no

        #Visitando código dentro da classe
        self.generic_visit(node)

        self.classeAtual = classeAnterior
        self.nomeClasseAtual = nomeClasseAnterior
    
    #Adiciona a self.funcoes cada um dos nós da AST que representam funções
    def visit_FunctionDef(self, node):
        #Atualizando nome da função e função atuais
        nomeFuncaoAnterior = self.nomeFuncaoAtual
        if(self.nomeFuncaoAtual == ""):
            self.nomeFuncaoAtual = node.name
        else:
            self.nomeFuncaoAtual = self.nomeFuncaoAtual + "." + node.name
        
        funcaoAnterior = self.funcaoAtual
        self.funcaoAtual = node

        if(self.classeAtual == None) or ((node not in self.metodosInstancia.values()) and (node not in self.metodosClasse.values())):
            
            #Adicionando função encontrada
            nomeFuncaoEncontrada = ""
            if(self.nomeClasseAtual != ""):
                nomeFuncaoEncontrada = self.nomeClasseAtual + "." + self.nomeFuncaoAtual
            else:
                nomeFuncaoEncontrada = self.nomeFuncaoAtual
            
            self.funcoes[nomeFuncaoEncontrada] = node

            #Verificando se há nós "ast.FunctionDef" declarados dentro de "node"
            #Ou seja, verificando se "node" é uma superFuncao
            for no in node.body:
                if isinstance(no, ast.FunctionDef):
                    self.superFuncoes.append(node)
                    break

        self.generic_visit(node)

        self.funcaoAtual = funcaoAnterior
        self.nomeFuncaoAtual = nomeFuncaoAnterior

    def getModulosImportados(self):
        return self.modulosImportados

    def getFuncoes(self):
        return self.funcoes

    def getClasses(self):
        return self.classes
    
    def getMetodosInstancia(self):
        return self.metodosInstancia

    def getMetodosClasse(self):
        return self.metodosClasse
    
    def getSuperFuncoes(self):
        return self.superFuncoes

    def getSuperClasses(self):
        return self.superClasses  

    def getSuperMetodos(self):
        return self.superMetodos

class GeradorGrafoFuncoes(ast.NodeVisitor):
    def __init__(self, arvoreAst, funcoes, metodosClasse, metodosInstancia):
        self.arvoreAst = arvoreAst
        self.funcoes = funcoes.copy()
        self.metodosClasse = metodosClasse.copy()
        self.metodosInstancia = metodosInstancia.copy()

        self.grafoFuncoes = Grafo()

    def geraGrafoFuncoes(self):
        #Inserindo todas as funções encontradas ao grafo de funções
        for funcao in self.funcoes.values():
            self.grafoFuncoes.inseriVertice(VerticeGrafo(funcao))
        
        for metodoClasse in self.metodosClasse.values():
            self.grafoFuncoes.inseriVertice(VerticeGrafo(metodoClasse))

        for metodoInstancia in self.metodosInstancia.values()   :
            self.grafoFuncoes.inseriVertice(VerticeGrafo(metodoInstancia))

        self.nomeClasseAtual = ""
        self.nomeFuncaoAtual = ""
        self.funcaoAtual = None
        self.visit(self.arvoreAst)

    def visit_ClassDef(self, node):
        nomeClasseAnterior = self.nomeClasseAtual
        if(self.nomeClasseAtual != ""):
            self.nomeClasseAtual = self.nomeClasseAtual + "." + node.name
        else:
            self.nomeClasseAtual = node.name

        self.generic_visit(node)

        self.nomeClasseAtual = nomeClasseAnterior

    def visit_FunctionDef(self, node):
        nomeFuncaoAnterior = self.nomeFuncaoAtual
        if(self.nomeFuncaoAtual != ""):
            self.nomeFuncaoAtual = self.nomeFuncaoAtual + "." + node.name
        else:
            self.nomeFuncaoAtual = node.name
        funcaoAnterior = self.funcaoAtual
        self.funcaoAtual = node

        self.generic_visit(node)

        self.nomeFuncaoAtual = nomeFuncaoAnterior
        self.funcaoAtual = funcaoAnterior

    def visit_Call(self, node):
        if(self.nomeFuncaoAtual != ""):
            funcaoChamada = None
            
            #Função chamada não é uma função importada de um módulo, nem um método de uma classe
            #nem um método de uma instância
            if(isinstance(node.func, ast.Name)):
                nomeFuncaoChamada = node.func.id
                
                #Encontrando possíveis funções chamdas
                possiveisFuncoesChamadas = []
                for nomeFuncao in self.funcoes:
                    if(nomeFuncao.split(".")[-1] == nomeFuncaoChamada):
                        possiveisFuncoesChamadas.append(nomeFuncao)

                if(len(possiveisFuncoesChamadas) >= 1):
                    #Procurando pela função definida no menor escopo possível
                    if(self.nomeClasseAtual != ""):
                        prefixoNomeFuncaoChamada = self.nomeClasseAtual + "." + self.nomeFuncaoAtual + "."
                    else:
                        prefixoNomeFuncaoChamada = self.nomeFuncaoAtual + "."
                    
                    while(funcaoChamada == None):

                        for possivelFuncaoChamada in possiveisFuncoesChamadas:
                            if(prefixoNomeFuncaoChamada + nomeFuncaoChamada == possivelFuncaoChamada):
                                funcaoChamada = self.funcoes[possivelFuncaoChamada]
                                break
                        
                        if(prefixoNomeFuncaoChamada == ""):
                            break

                        if(len(prefixoNomeFuncaoChamada.split(".")) > 2):
                            prefixoNomeFuncaoChamada = prefixoNomeFuncaoChamada.split(".")
                            prefixoNomeFuncaoChamada.pop(-2)
                            prefixoNomeFuncaoChamada = ".".join(prefixoNomeFuncaoChamada)
                        else:
                            prefixoNomeFuncaoChamada = ""
                        
                        if(self.nomeClasseAtual != ""):
                            if(len(prefixoNomeFuncaoChamada) == len(self.nomeClasseAtual) + 1 ):
                                prefixoNomeFuncaoChamada = ""
                        """
                        if(prefixoNomeFuncaoChamada == ""):
                            break
                        elif(self.nomeClasseAtual != ""):
                            if(len(prefixoNomeFuncaoChamada) > len(self.nomeClasseAtual) + 3):
                                prefixoNomeFuncaoChamada = prefixoNomeFuncaoChamada[:-2]
                            elif(len(prefixoNomeFuncaoChamada) == len(self.nomeClasseAtual) + 3):
                                prefixoNomeFuncaoChamada = ""
                        else:
                            if(len(prefixoNomeFuncaoChamada) > 2):
                                prefixoNomeFuncaoChamada = prefixoNomeFuncaoChamada[:-2]
                            elif(len(prefixoNomeFuncaoChamada) == 2):
                                prefixoNomeFuncaoChamada = ""
                        """
            
            #Função chamada é uma função importada de um módulo, um método de uma classe
            #ou um método de uma instância
            elif(isinstance(node.func, ast.Attribute)):
                #Construindo nome da função chamada
                noAtual = node.func
                partesNome = []
                while(isinstance(noAtual, ast.Attribute)):
                    partesNome.append(noAtual.attr)
                    noAtual = noAtual.value
                partesNome.append(noAtual.id)

                partesNome.reverse()
                nomeFuncaoChamada = ".".join(partesNome)
                
                #Testando se a função chamada é um método de uma instância
                if(partesNome[0] == "self"):
                    #Retirando "self." do nome da função chamada
                    nomeFuncaoChamada = ".".join(partesNome[1:])
                    
                    for nomeMetodoInstancia in self.metodosInstancia:
                        
                        if(self.nomeClasseAtual + "." + nomeFuncaoChamada == nomeMetodoInstancia):
                            funcaoChamada = self.metodosInstancia[nomeMetodoInstancia]
                            break
                else:

                    for nomeMetodoClasse in self.metodosClasse:

                        if(nomeFuncaoChamada == nomeMetodoClasse):
                            funcaoChamada = self.metodosClasse[nomeMetodoClasse]
                            break

            if(funcaoChamada != None):
                #Inserindo "funcaoChamada" no grafo de funções
                verticeFuncaoChamada = self.grafoFuncoes.buscaVertice(funcaoChamada)
                verticeFuncaoAtual = self.grafoFuncoes.buscaVertice(self.funcaoAtual)
                if(verticeFuncaoChamada == None or verticeFuncaoAtual == None):
                    sys.exit("Erro ao inserir ligação no vértice do grafo!")
                else:
                    verticeFuncaoChamada.inseriLigacao(verticeFuncaoAtual)
        
        self.generic_visit(node)
    
    def getGrafoFuncoes(self):
        return self.grafoFuncoes

class Grafo():
    def __init__(self):
        #Cada elemento de self.vertices será do tipo VerticeGrafo
        self.vertices = []

    def inseriVertice(self, vertice):
        if(vertice not in self.vertices):
            self.vertices.append(vertice)

    #Retorna o vertice que possui o mesmo valor de "dado"
    #Se nenhum dos vértices possuir o mesmo valor de "dado", retorna-se None
    def buscaVertice(self, dado):
        for vertice in self.vertices:
            if(vertice.getDado() == dado):
                return vertice
        return None

    def getVertices(self):
        return self.vertices

    def imprimeGrafo(self, dicio):
        for vertice in self.vertices:
            vertice.imprimeGrafo(dicio)

class VerticeGrafo():
    def __init__(self, dado):
        self.dado = dado

        #Os elementos de self.verticesLigados serão instâncias de "VerticeGrafo"
        self.verticesLigados = []

    #Inseri "ligacao" em "self.verticesLigados"
    def inseriLigacao(self, ligacao):
        if(ligacao not in self.verticesLigados):
            self.verticesLigados.append(ligacao)

    def getDado(self):
        return self.dado

    def getVerticesLigados(self):
        return self.verticesLigados

    def imprimeGrafo(self, dicio):
        indice = None
        for nome in dicio:
            if(dicio[nome] == self.dado):
                print(nome)
                break

        for verticeLigado in self.verticesLigados:
            for nome in dicio:
                if(dicio[nome] == verticeLigado.dado):
                    print("    ", nome)
                    break

class ClassificadorFuncoesNF(ast.NodeVisitor):
    def __init__(self, arvoreAst, funcoesMetodosClasse):
        self.arvoreAst = arvoreAst
        self.funcoesMetodosClasse = funcoesMetodosClasse

        #As chaves de "self.funcoesNF" serão objetos ast.FunctionDef e os valores
        #serão strings que indicam o motivo das funções serem classificadas como
        #não funcionam com o IntPy
        self.funcoesNF = {}
          
    def classificaFuncoesNF(self):
        self.analisandoFuncoes = True
        self.percorrendoAST = False
        for funcao in self.funcoesMetodosClasse.values():
            self.funcaoAtual = funcao
            self.visit(funcao)
        
        self.analisandoFuncoes = False
        self.percorrendoAST = True
        
        self.nomeFuncaoAtual = ""
        self.nomeClasseAtual = ""
        self.visit(self.arvoreAst)

    def visit_ClassDef(self, node):
        if(self.percorrendoAST):
            nomeClasseAnterior = self.nomeClasseAtual
            if(self.nomeClasseAtual == ""):
                self.nomeClasseAtual = node.name
            else:
                self.nomeClasseAtual = self.nomeClasseAtual + "." + node.name

            self.generic_visit(node)

            self.nomeClasseAtual = nomeClasseAnterior
        
        elif(self.analisandoFuncoes):
            self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        if(self.analisandoFuncoes and self.funcaoAtual == node):
            #Verificando se a função possui argumentos
            if(len(node.args.args) == 0):
                self.funcoesNF[node] = "Essa função não possui argumentos"
                return

            #Verificando se existe alguma instrução de "return" no escopo mais externo da função
            returnEncontrado = False
            for elemento in node.body:
                if(isinstance(elemento, ast.Return)):
                    returnEncontrado = True
                    break

            if(not returnEncontrado):
                self.funcoesNF[node] = "Essa função pode retornar None"
                return

            #Pesquisando se todos os comandos "return" da função não retornam "None"
            self.returnNoneEncontrado = False            
            self.generic_visit(node)

            #Caso algum dos comandos retorne "None" a função será classificada como
            #não funciona com o IntPy
            if(self.returnNoneEncontrado):
                self.funcoesNF[node] = "Essa função pode retornar None"
                return

        elif(self.percorrendoAST):
            nomeFuncaoAnterior = self.nomeFuncaoAtual
            if(self.nomeFuncaoAtual == ""):
                self.nomeFuncaoAtual = node.name
            else:
                self.nomeFuncaoAtual = self.nomeFuncaoAtual + "." + node.name

            self.generic_visit(node)

            self.nomeFuncaoAtual = nomeFuncaoAnterior
    
    #Se pelo menos uma instrução de "return" retorna "None", não há necessidade
    #de continuar a procurar
    def visit_Return(self, node):
        if(self.analisandoFuncoes):
            if(isinstance(node.value, ast.NameConstant)):
                if(node.value.value == None):
                    self.returnNoneEncontrado = True
                    return

            elif(node.value == None):
                self.returnNoneEncontrado = True
                return

            self.generic_visit(node)

        elif(self.percorrendoAST):
            self.generic_visit(node)

    def visit_Call(self, node):
        if(self.percorrendoAST):
            if(len(node.args) == 0):

                #Construindo nome da função chamada
                noAtual = node.func
                partesNome = []
                while(isinstance(noAtual, ast.Attribute)):
                    partesNome.append(noAtual.attr)
                    noAtual = noAtual.value
                partesNome.append(noAtual.id)

                partesNome.reverse()
                nomeFuncaoChamada = ".".join(partesNome)
                
                funcaoChamada = ""
                #Testando se a função chamada não é um método de classe
                if(isinstance(node.func, ast.Name)):
                    #Encontrando possíveis funções chamdas
                    possiveisFuncoesChamadas = []
                    for nomeFuncaoMetodo in self.funcoesMetodosClasse:
                        if(nomeFuncaoMetodo.split(".")[-1] == nomeFuncaoChamada):
                            possiveisFuncoesChamadas.append(nomeFuncaoMetodo)
                    
                    if(len(possiveisFuncoesChamadas) >= 1):
                        #Procurando pela função definida no menor escopo possível
                        prefixoNomeFuncaoChamada = ""
                        if(self.nomeClasseAtual != ""):
                            prefixoNomeFuncaoChamada = self.nomeClasseAtual + "."
                            if(self.nomeFuncaoAtual != ""):
                                prefixoNomeFuncaoChamada = prefixoNomeFuncaoChamada + self.nomeFuncaoAtual + "."
                        elif(self.nomeFuncaoAtual != ""):
                            prefixoNomeFuncaoChamada = self.nomeFuncaoAtual + "."
                        
                        while(funcaoChamada == ""):

                            for possivelFuncaoChamada in possiveisFuncoesChamadas:
                                if(prefixoNomeFuncaoChamada + nomeFuncaoChamada == possivelFuncaoChamada):
                                    funcaoChamada = possivelFuncaoChamada
                                    break

                            if(prefixoNomeFuncaoChamada == ""):
                                break

                            if(len(prefixoNomeFuncaoChamada.split(".")) > 2):
                                prefixoNomeFuncaoChamada = prefixoNomeFuncaoChamada.split(".")
                                prefixoNomeFuncaoChamada.pop(-2)
                                prefixoNomeFuncaoChamada = ".".join(prefixoNomeFuncaoChamada)
                            else:
                                prefixoNomeFuncaoChamada = ""
                            
                            if(self.nomeClasseAtual != ""):
                                if(len(prefixoNomeFuncaoChamada) == len(self.nomeClasseAtual) + 1 ):
                                    prefixoNomeFuncaoChamada = ""
                            """
                            if(prefixoNomeFuncaoChamada == ""):
                                break
                            elif(self.nomeClasseAtual != ""):
                                if(len(prefixoNomeFuncaoChamada) > len(self.nomeClasseAtual) + 3):
                                    prefixoNomeFuncaoChamada = prefixoNomeFuncaoChamada[:-2]
                                elif(len(prefixoNomeFuncaoChamada) == len(self.nomeClasseAtual) + 3):
                                    prefixoNomeFuncaoChamada = ""
                            else:
                                if(len(prefixoNomeFuncaoChamada) > 2):
                                    prefixoNomeFuncaoChamada = prefixoNomeFuncaoChamada[:-2]
                                elif(len(prefixoNomeFuncaoChamada) == 2):
                                    prefixoNomeFuncaoChamada = ""
                            """
                else:
                    funcaoChamada = nomeFuncaoChamada

                if(funcaoChamada in self.funcoesMetodosClasse):
                    self.funcoesNF[self.funcoesMetodosClasse[funcaoChamada]] = "Essa função é chamada sem que se passe nenhum argumento"
        self.generic_visit(node)

    def getFuncoesNF(self):
        return self.funcoesNF

class ClassificadorFuncoesND(ast.NodeVisitor):
    def __init__(self, funcoes, modulosImportados):
        self.funcoes = funcoes
        self.nomeModulosImportados = []
        for listaModulos in modulosImportados:
            for modulo in listaModulos.names:
                self.nomeModulosImportados.append(modulo.name)

        #As chaves de "self.funcoesND" serão objetos "ast.FunctionDef" e os valores
        #serão strings que indicam o motivo das funções serem classificadas como
        #não determinísticas
        self.funcoesND = {}
          
    def classificaFuncoesND(self):
        for funcao in self.funcoes:
            self.funcaoAtual = funcao
            self.visit(funcao)

    def visit_FunctionDef(self, node):
        if(self.funcaoAtual == node):
            #Visitando nós filhos de FunctionDef
            self.generic_visit(node)

    def visit_Call(self, node):
        motivoClassificacaoND = ""

        motivoClassificacaoND = self.funcoesNDBibliotecasExternasChamadas(node)
        if(motivoClassificacaoND == ""):
            motivoClassificacaoND = self.funcoesNDNativasPython(node)
            
        #Verificando se foi encontrado algum motivo para classificar a função como
        #não determinística
        if(motivoClassificacaoND != ""):
            self.funcoesND[self.funcaoAtual] = motivoClassificacaoND

        self.generic_visit(node)

    """
    def funcoesInstanciamObjetos(self, callNode):
        nomeFuncao = ""
        motivoClassificacaoND = ""

        #Obtendo o nome da função chamada
        if(isinstance(callNode.func, ast.Attribute)):
            nomeFuncao = callNode.func.attr
        elif(isinstance(callNode.func, ast.Name)):
            nomeFuncao = callNode.func.id
        
        #Testando se a função chamada é o construtor de uma classe
        if(nomeFuncao != ""):
            if(nomeFuncao[0].isupper()):
                motivoClassificacaoND = "Essa função instancia objetos durante seu processamento"
        
        return motivoClassificacaoND
    """

    def funcoesNDBibliotecasExternasChamadas(self, callNode):
        motivoClassificacaoND = ""
        funcaoChamada = ""

        if(isinstance(callNode.func, ast.Attribute)):
            attributeNode = callNode.func
            if(isinstance(attributeNode.value, ast.Name)):
                nameNode = attributeNode.value

                #Testando se a função chamada pertence à biblioteca "random"
                if((nameNode.id == "random") and ("random" in self.nomeModulosImportados)):
                    funcaoChamada = self.funcaoNDBibliotecaRandomChamada(callNode)
                
                #Testando se a função chamada pertence à biblioteca "numpy"
                if((funcaoChamada == "") and (nameNode.id == "numpy") and ("numpy" in self.nomeModulosImportados)):
                    funcaoChamada = self.funcaoNDBibliotecaNumpyChamada(callNode)

                #Testando se a função chamada pertence à biblioteca "os"
                if((funcaoChamada == "") and (nameNode.id == "os") and ("os" in self.nomeModulosImportados)):
                    funcaoChamada = self.funcaoNDBibliotecaOsChamada(callNode)
                            
                #Testando se a função chamada é a cPickle.dump()
                if((funcaoChamada == "") and (nameNode.id == "cPickle") and (attributeNode.attr == "dump")
                    and ("cPickle" in self.nomeModulosImportados)):
                    funcaoChamada = "cPickle.dump()"
                
                #Testando se a função chamada é a subprocess.check_call()
                if((funcaoChamada == "") and (nameNode.id == "subprocess") and (attributeNode.attr == "check_call")
                    and ("subprocess" in self.nomeModulosImportados)):
                    funcaoChamada = "subprocess.check_call()"

                #Testando se a função chamada é a toolshed.reader()
                if((funcaoChamada == "") and (nameNode.id == "toolshed") and (attributeNode.attr == "reader")
                    and ("toolshed" in self.nomeModulosImportados)):
                    funcaoChamada = "toolshed.reader()"

                #Testando se a função chamada é a gzip.open()
                if((funcaoChamada == "") and (nameNode.id == "gzip") and
                    (attributeNode.attr == "open") and ("gzip" in self.nomeModulosImportados)):
                    funcaoChamada = "gzip.open()"
                
                #Testando se a função chamada é a shutil.rmtree()
                if((funcaoChamada == "") and (nameNode.id == "shutil") and
                    (attributeNode.attr == "rmtree") and ("shutil" in self.nomeModulosImportados)):
                    funcaoChamada = "shutil.rmtree()"

                #Testando se a função chamada é a shutil.copy()
                if((funcaoChamada == "") and (nameNode.id == "shutil") and
                    (attributeNode.attr == "copy") and ("shutil" in self.nomeModulosImportados)):
                    funcaoChamada = "shutil.copy()"

                #Testando se a função chamada é a codecs.open()
                if((funcaoChamada == "") and (nameNode.id == "codecs") and
                    (attributeNode.attr == "open") and ("codecs" in self.nomeModulosImportados)):
                    funcaoChamada = "codecs.open()"
                
                #Testando se a função chamada é a time.sleep()
                if((funcaoChamada == "") and (nameNode.id == "time") and
                    (attributeNode.attr == "sleep") and ("time" in self.nomeModulosImportados)):
                    funcaoChamada = "time.sleep()"
                
                #Testando se a função chamada é a glob.glob()
                if((funcaoChamada == "") and (nameNode.id == "glob") and
                    (attributeNode.attr == "glob") and ("glob" in self.nomeModulosImportados)):
                    funcaoChamada = "glob.glob()"

            elif(isinstance(attributeNode.value, ast.Attribute)):
                attributeNodeInterno = attributeNode.value
                if(isinstance(attributeNodeInterno.value, ast.Name)):
                    nameNode = attributeNodeInterno.value

                    #Testando se a função chamada pertence à biblioteca "os.path"
                    if(nameNode.id == "os" and attributeNodeInterno.attr == "path" and (("os.path" in self.nomeModulosImportados) or ("os" in self.nomeModulosImportados))):
                        funcaoChamada = self.funcaoNDBibliotecaOsPathChamada(callNode)

                    #Testando se a função chamada pertence à biblioteca "numpy"
                    if((funcaoChamada == "") and (nameNode.id == "numpy") and ("numpy" in self.nomeModulosImportados)):
                        funcaoChamada = self.funcaoNDBibliotecaNumpyChamada(callNode)

                    #Testando se a função chamada pertence à biblioteca "matplotlib.pyplot"
                    if((funcaoChamada == "") and (nameNode.id == "matplotlib") and
                            (attributeNodeInterno.attr == "pyplot") and ("matplotlib.pyplot" in self.nomeModulosImportados)):
                        funcaoChamada = self.funcaoNDBibliotecaMatplotlibPyplotChamada(callNode)

                    #Testando se a função chamada pertence à biblioteca "sys"
                    if((funcaoChamada == "") and (nameNode.id == "sys") and ("sys" in self.nomeModulosImportados)):
                        funcaoChamada = self.funcaoNDBibliotecaSysChamada(callNode)
                    
                    #Testando se a função chamada é a matplotlib.pylab.imshow()
                    if((funcaoChamada == "") and (nameNode.id == "matplotlib") and
                        (attributeNodeInterno.attr == "pylab") and (attributeNode.attr == "imshow") and ("matplotlib.pylab" in self.nomeModulosImportados)):
                        funcaoChamada = "matplotlib.pylab.imshow()"

                    #Testando se a função chamada é a matplotlib.pylab.show()
                    if((funcaoChamada == "") and (nameNode.id == "matplotlib") and
                        (attributeNodeInterno.attr == "pylab") and (attributeNode.attr == "show") and ("matplotlib.pylab" in self.nomeModulosImportados)):
                        funcaoChamada = "matplotlib.pylab.show()"
        
        if(funcaoChamada != ""):
            motivoClassificacaoND = "Essa função chama a função " + funcaoChamada + " que não é determinística"

        return motivoClassificacaoND

    def funcaoNDBibliotecaRandomChamada(self, callNode):
        funcaoChamada = ""

        #Com certeza a função chamada começa com "random." por isso não é necessário
        #verificar se "callNode.func" é do tipo "ast.Attribute"
        attributeNode = callNode.func

        #Verificando se a função chamada é do tipo "a.b()"
        if(isinstance(attributeNode.value, ast.Name)):
            #Testando se a função chamada é a random.random()
            if(attributeNode.attr == "random"):
                funcaoChamada = "random.random()"

            #Testando se a função chamada é a random.choice()
            elif(attributeNode.attr == "choice"):
                funcaoChamada = "random.choice()"
            
            #Testando se a função chamada é a random.sample()
            elif(attributeNode.attr == "sample"):
                funcaoChamada = "random.sample()"
        
        return funcaoChamada

    def funcaoNDBibliotecaOsChamada(self, callNode):
        funcaoChamada = ""

        #Com certeza a função chamada começa com "os." por isso não é necessário
        #verificar se "callNode.func" é do tipo "ast.Attribute"
        attributeNode = callNode.func

        #Verificando se a função chamada é do tipo "a.b()"
        if(isinstance(attributeNode.value, ast.Name)):
            #Testando se a função chamada é a os.mkdir()
            if(attributeNode.attr == "mkdir"):
                funcaoChamada = "os.mkdir()"

            #Testando se a função chamada é a os.makedirs()
            elif(attributeNode.attr == "makedirs"):
                funcaoChamada = "os.makedirs()"

            #Testando se a função chamada é a os.unlink()
            elif(attributeNode.attr == "unlink"):
                funcaoChamada = "os.unlink()"

            #Testando se a função chamada é a os.fsync()
            elif(attributeNode.attr == "fsync"):
                funcaoChamada = "os.fsync()"
            
            #Testando se a função chamada é a os.rename()
            elif(attributeNode.attr == "rename"):
                funcaoChamada = "os.rename()"
            
            #Testando se a função chamada é a os.remove()
            elif(attributeNode.attr == "remove"):
                funcaoChamada = "os.remove()"
            
            #Testando se a função chamada é a os.rmdir()
            elif(attributeNode.attr == "rmdir"):
                funcaoChamada = "os.rmdir()"

            #Testando se a função chamada é a os.walk()
            elif(attributeNode.attr == "walk"):
                funcaoChamada = "os.walk()"

            #Testando se a função chamada é a os.getcwd()
            elif(attributeNode.attr == "getcwd"):
                funcaoChamada = "os.getcwd()"

            #Testando se a função chamada é a os.getchdir()
            elif(attributeNode.attr == "chdir"):
                funcaoChamada = "os.chdir()"

            #Testando se a função chamada é a os.system()
            elif(attributeNode.attr == "system"):
                funcaoChamada = "os.system()"

        return funcaoChamada

    def funcaoNDBibliotecaOsPathChamada(self, callNode):
        funcaoChamada = ""

        #Com certeza a função chamada começa com "os.path" por isso não é necessário
        #verificar se "callNode.func" é do tipo "ast.Attribute" nem se "attributeNode.value"
        #é do tipo "ast.Attribute"
        attributeNode = callNode.func
        attributeNodeInterno = attributeNode.value
        
        #Verificando se a função chamada é do tipo "a.b.c()"
        if(isinstance(attributeNodeInterno.value, ast.Name)):
            #Testando se a função chamada é a os.path.exists()
            if(attributeNode.attr == "exists"):
                funcaoChamada = "os.path.exists()"

            #Testando se a função chamada é a os.path.isfile()
            elif(attributeNode.attr == "isfile"):
                funcaoChamada = "os.path.isfile()"
            
            #Testando se a função chamada é a os.path.isdir()
            elif(attributeNode.attr == "isdir"):
                funcaoChamada = "os.path.isdir()"

            #Testando se a função chamada é a os.path.getsize()
            elif(attributeNode.attr == "getsize"):
                funcaoChamada = "os.path.getsize()"
            
        return funcaoChamada

    def funcaoNDBibliotecaNumpyChamada(self, callNode):
        funcaoChamada = ""

        #Com certeza a função chamada começa com "numpy" por isso não é necessário
        #verificar se "callNode.func" é do tipo "ast.Attribute"
        attributeNode = callNode.func
        
        #Verificando se a função chamada é do tipo "a.b()"
        if(isinstance(attributeNode.value, ast.Name)):
            #Testando se a função chamada é a numpy.load()
            if(attributeNode.attr == "load"):
                funcaoChamada = "numpy.load()"

            #Testando se a função chamada é a numpy.loadtxt()
            elif(attributeNode.attr == "loadtxt"):
                funcaoChamada = "numpy.loadtxt()"
            
            #Testando se a função chamada é a numpy.save()
            elif(attributeNode.attr == "save"):
                funcaoChamada = "numpy.save()"

            #Testando se a função chamada é a numpy.savetxt()
            elif(attributeNode.attr == "savetxt"):
                funcaoChamada = "numpy.savetxt()"

            #Testando se a função chamada é a numpy.set_printoptions()
            elif(attributeNode.attr == "set_printoptions"):
                funcaoChamada = "numpy.set_printoptions()"

        #Verificando se a função chamada é do tipo "a.b."
        elif(isinstance(attributeNode.value, ast.Attribute)):
            attributeNodeInterno = attributeNode.value
            
            #Verificando se a função chamada é do tipo "a.b.c()"
            if(isinstance(attributeNodeInterno.value, ast.Name)):
                #Testando se a função chamada é a numpy.random.choice()
                if(attributeNodeInterno.attr == "random" and
                    attributeNode.attr == "choice"):
                    funcaoChamada = "numpy.random.choice"

                #Testando se a função chamada é a numpy.random.poisson()
                elif(attributeNodeInterno.attr == "random" and
                    attributeNode.attr == "poisson"):
                    funcaoChamada = "numpy.random.poisson"

        return funcaoChamada

    def funcaoNDBibliotecaMatplotlibPyplotChamada(self, callNode):
        funcaoChamada = ""

        #Com certeza a função chamada começa com "matplotlib.pyplot" por isso não é necessário
        #verificar se "callNode.func" é do tipo "ast.Attribute" nem se "attributeNode.value" é
        #do tipo "ast.Attribute"
        attributeNode = callNode.func
        attributeNodeInterno = attributeNode.value
        
        #Verificando se a função chamada é do tipo "a.b.c()"
        if(isinstance(attributeNodeInterno.value, ast.Name)):
            #Testando se a função chamada é a matplotlib.pyplot.savefig()
            if(attributeNode.attr == "savefig"):
                funcaoChamada = "matplotlib.pyplot.savefig"

            #Testando se a função chamada é a matplotlib.pyplot.show()
            elif(attributeNode.attr == "show"):
                funcaoChamada = "matplotlib.pyplot.show"

        return funcaoChamada

    def funcaoNDBibliotecaSysChamada(self, callNode):
        funcaoChamada = ""

        #Com certeza a função chamada começa com "sys" por isso não é necessário
        #verificar se "callNode.func" é do tipo "ast.Attribute"
        attributeNode = callNode.func
        
        #Verificando se a função chamada é do tipo "a.b."
        if(isinstance(attributeNode.value, ast.Attribute)):
            attributeNodeInterno = attributeNode.value
            
            #Verificando se a função chamada é do tipo "a.b.c()"
            if(isinstance(attributeNodeInterno.value, ast.Name)):
                #Testando se a função chamada é a sys.stdout.write()
                if((attributeNodeInterno.attr == "stdout") and
                    (attributeNode.attr == "write")):
                    funcaoChamada = "sys.stdout.write()"
                
                #Testando se a função chamada é a sys.stdout.flush()
                elif((attributeNodeInterno.attr == "stdout") and
                    (attributeNode.attr == "flush")):
                    funcaoChamada = "sys.stdout.flush()"

                #Testando se a função chamada é a sys.stderr.write()
                elif((attributeNodeInterno.attr == "stderr") and
                    (attributeNode.attr == "write")):
                    funcaoChamada = "sys.stderr.write()"
        
        return funcaoChamada

    def funcoesNDNativasPython(self, callNode):
        funcaoChamada = ""
        motivoClassificacaoND = ""
        if(isinstance(callNode.func, ast.Name)):
            nameNode= callNode.func

            #Testando se a função chamada é a print()
            if(nameNode.id == "print"):
                funcaoChamada = "print()"

            #Testando se a função chamada é a open()
            elif(nameNode.id == "open"):
                funcaoChamada = "open()"

            #Testando se a função chamada é a repr()
            elif(nameNode.id == "repr"):
                funcaoChamada = "repr()"

        if(funcaoChamada != ""):
             motivoClassificacaoND = "Essa função chama a função " + funcaoChamada + " que não é determinística"
        
        return motivoClassificacaoND

    #Indentificando funções que utilizam "global" (variáveis globais) em seu processamento
    def visit_Global(self, node):
        self.funcoesND[self.funcaoAtual] = "Essa função utiliza em seu processamento valores contidos em variáveis globais"
        self.generic_visit(node)

    def getFuncoesND(self):
        return self.funcoesND

class ClassificadorFuncoesNPSC(ast.NodeVisitor):
    def __init__(self, funcoesMetodos, modulosImportados):        
        self.funcoesMetodos = funcoesMetodos
        self.modulosImportados = modulosImportados
        self.funcoesNPSC = {}

    def classificaFuncoesNPSC(self):
        for funcao in self.funcoesMetodos:
            self.funcaoAtual = funcao
            self.visit(funcao)

    #Não chamamos
    #recursivamente o "node" porque pode ocorrer que o valor de "node.value"
    #seja do tipo "ast.Attribute" e avaliaríamos o mesmo atributo duas vezes
    #o que poderia gerar erros.
    #Ex.: import sys
    #     a = ConstrutorClasse()
    #     a.sys.argv = 1
    def visit_Attribute(self, node):
        if(self.attributeNodeNomeFuncao != node):
            #Recuperando nome do atributo
            noAtual = node
            partesNomeAtributo = []
            while(isinstance(noAtual, ast.Attribute)):
                partesNomeAtributo.append(noAtual.attr)
                noAtual = noAtual.value
            
            if(isinstance(noAtual, ast.Name)):
                partesNomeAtributo.append(noAtual.id)
            
            partesNomeAtributo.reverse()

            achou = False
            for instImport in self.modulosImportados:
                listaModulos = instImport.names
                for modulo in listaModulos:
                    partesNomeModulo = modulo.name.split(".")
                    j = set(partesNomeModulo)

                    i = set(partesNomeAtributo[:len(partesNomeModulo)])
                    
                    if(i == j):
                        achou = True
                        self.funcoesNPSC[self.funcaoAtual] = ("Essa função utiliza o atributo " + ".".join(partesNomeAtributo) + " do módulo " +
                                modulo.name + " que não está presente no banco deste analisador")
                        break
                    
                if(achou):
                    break

    def visit_FunctionDef(self, node):
        #Testando se esse nó FunctionDef é uma subfunção
        if(self.funcaoAtual == node):
            #Visitando nós filhos de FunctionDef
            self.generic_visit(node)
        else:
            return None

    #Cada vez que encontramos um nó "ast.Call" gravamos o nome da função ("node.func")
    #pois o nome da função sempre será um "ast.Attribute" ou um "ast.Name"
    #Se for um "ast.Attribute", ao chamarmos a função "self.generic_visit(node)", o nome
    #da função será enviado para ela e corre-se o risco de identificá-lo como um atributo do módulo
    #importado e não como uma chamada à uma função do módulo importado.
    #Por isso sempre que começamos a executar a função "visit_Attribute(self, node)", verificamos se
    #o nó recebido não é o que contém o nome de uma função chamada
    def visit_Call(self, node):
        partesNomeFuncaoChamada = []

        #Juntando nome da função chamada
        noAtual = node.func
        while(isinstance(noAtual, ast.Attribute)):
            partesNomeFuncaoChamada.append(noAtual.attr)
            noAtual = noAtual.value
        if(isinstance(noAtual, ast.Name)):
            partesNomeFuncaoChamada.append(noAtual.id)

        if(len(partesNomeFuncaoChamada) > 1):
            partesNomeFuncaoChamada.reverse()
            
            #i = set(partesNomeFuncaoChamada[:-1])

            achou = False
            for instImport in self.modulosImportados:
                listaModulos = instImport.names
                for modulo in listaModulos:
                    partesNomeModulo = modulo.name.split(".")
                    j = set(partesNomeModulo)

                    i = set(partesNomeFuncaoChamada[:len(partesNomeModulo)])
                    
                    if(i == j):
                        achou = True
                        if(not self.funcaoChamadaDeterministica(".".join(partesNomeFuncaoChamada))):
                            self.funcoesNPSC[self.funcaoAtual] = ("Essa função chama a função " +
                                ".".join(partesNomeFuncaoChamada) + "() que não está presente no banco deste analisador")
                        break
                    
                if(achou):
                    break
        
        self.attributeNodeNomeFuncao = node.func
        self.generic_visit(node)
            
    def funcaoChamadaDeterministica(self, funcao):
        retorno = False
        if(funcao == "os.path.join" or funcao == "os.path.dirname" or
           funcao == "os.path.splitext" or funcao == "os.path.abspath" or
           funcao == "os.path.basename"):
            retorno = True

        elif(funcao == "numpy.log" or funcao == "numpy.median" or
             funcao == "numpy.abs" or funcao == "numpy.absolute" or
             funcao == "numpy.empty" or funcao == "numpy.hstack" or
             funcao == "numpy.isnan" or funcao == "numpy.repeat" or
             funcao == "numpy.dot" or funcao == "numpy.diagflat" or
             funcao == "numpy.transpose" or funcao == "numpy.linalg.det" or
             funcao == "numpy.zeros_like" or funcao == "numpy.diag" or
             funcao == "numpy.zeros" or funcao == "numpy.intersect1d" or
             funcao == "numpy.mean" or funcao == "numpy.reshape" or
             funcao == "numpy.nonzero" or funcao == "numpy.logical_and" or
             funcao == "numpy.unique" or funcao == "numpy.any" or 
             funcao == "numpy.exp" or funcao == "numpy.sum" or
             funcao == "numpy.var" or funcao == "numpy.std" or
             funcao == "numpy.log10" or funcao == "numpy.log2" or
             funcao == "numpy.arange" or funcao == "numpy.floor" or
             funcao == "numpy.ceil" or funcao == "numpy.mod" or
             funcao == "numpy.logical_or" or funcao == "numpy.argsort" or
             funcao == "numpy.array"):
            retorno = True

        elif(funcao == "scipy.special.polygamma" or
             funcao == "scipy.stats.nbinom.logpmf" or
             funcao == "scipy.special.digamma"):
            retorno = True
        
        elif(funcao == "sys.exit"):
            retorno = True

        elif(funcao == "math.floor" or funcao == "math.sqrt"):
            retorno = True

        elif(funcao == "textwrap.fill"):
            retorno = True

        return retorno

    def getFuncoesNPSC(self):
        return self.funcoesNPSC

class EscritorAST(ast.NodeTransformer):
    def __init__(self, arvoreAst, classes, metodosInstancia, superClasses, superFuncoes, superMetodos, classificacaoFuncoesMetodos):
        self.arvoreAst = arvoreAst
        self.classes = classes
        self.metodosInstancia = metodosInstancia
        self.superClasses = superClasses
        self.superFuncoes = superFuncoes
        self.superMetodos = superMetodos
        self.classificacaoFuncoesMetodos = classificacaoFuncoesMetodos

    def escreveClassificacaoFuncoesAST(self):
        #Marcando todos os métodos de instância
        #Precisei usar a "listaAuxiliar" porque se fosse deletando direto em
        #"metodosInstanciaNaoEscritos" enquanto ocorria o segundo for, haveria erro no
        #percurso dos elementos de "metodosInstanciaNaoEscritos"
        marcadorFuncaoNF = ast.Expr(value=ast.Constant(
                value="A função logo abaixo não funciona com o IntPy", kind=None)) 
        
        metodosInstanciaNaoEscritos = self.metodosInstancia.copy()
        listaAuxiliar = self.metodosInstancia.copy()
        
        for classe in self.classes:
            for metodoInstancia in metodosInstanciaNaoEscritos:
                if(metodoInstancia in classe.body):
                    #Verificando como o método de instância foi classificado
                    marcador = None
                    motivoClassificacao = ""
                    for funcaoMetodo in self.classificacaoFuncoesMetodos:
                        if(funcaoMetodo.getDado() == metodoInstancia):
                            if(funcaoMetodo.getClassificacao() == "D"):
                                marcador = ast.Expr(value=ast.Constant(
                                            value="apesar de ser determinística", kind=None))
                            elif(funcaoMetodo.getClassificacao() == "ND"):
                                marcador = ast.Expr(value=ast.Constant(
                                            value="e não é determinística", kind=None))
                            elif(funcaoMetodo.getClassificacao() == "NPSC"):
                                marcador = ast.Expr(value=ast.Constant(
                                            value="e não pode ser classificada por este analisador", kind=None))
                            
                            motivoClassificacao = funcaoMetodo.getMotivoClassificacao()

                            #Atualizando self.classificacaoFuncoesMetodos
                            self.classificacaoFuncoesMetodos.remove(funcaoMetodo)
                            break
                    
                    #Classificando função na AST                    
                    indiceMetodoInstancia = classe.body.index(metodoInstancia)
                    
                    if(motivoClassificacao != ""):
                        classe.body.insert(indiceMetodoInstancia, ast.Expr(value=ast.Constant(
                                                                value=motivoClassificacao, kind=None)))
                    if(marcador != None):
                        classe.body.insert(indiceMetodoInstancia, marcador)    
                    classe.body.insert(indiceMetodoInstancia, marcadorFuncaoNF)

                    #Atualizando listaAuxiliar com os métodos de instância que estão sendo processados
                    listaAuxiliar.remove(metodoInstancia)

            #Atualizando lista de métodos de instância que ainda não foram processados
            metodosInstanciaNaoEscritos = listaAuxiliar.copy()

        #Escrevendo classificação das demais funções
        marcadorFuncaoND = ast.Expr(value=ast.Constant(
                value="A função logo abaixo não é determinística", kind=None))
        marcadorFuncaoNPSC = ast.Expr(value=ast.Constant(
                value="O IntPy não é capaz de classificar a função abaixo", kind=None))
        
        for funcaoMetodo in self.classificacaoFuncoesMetodos:
            #Funções determinísticas
            if(funcaoMetodo.getClassificacao() == "D"):
                funcaoMetodo.getDado().decorator_list.append("deterministic")
            
            else:
                marcador = None
                if(funcaoMetodo.getClassificacao() == "ND"):
                    marcador = marcadorFuncaoND
                elif(funcaoMetodo.getClassificacao() == "NF"):
                    marcador = marcadorFuncaoNF
                elif(funcaoMetodo.getClassificacao() == "NPSC"):
                    marcador = marcadorFuncaoNPSC

                if(funcaoMetodo.getDado() in self.arvoreAst.body):
                    indiceFuncaoMetodo = self.arvoreAst.body.index(funcaoMetodo.getDado())
                    self.arvoreAst.body.insert(indiceFuncaoMetodo, ast.Expr(value=ast.Constant(
                                                                value=funcaoMetodo.getMotivoClassificacao(), kind=None)))
                    self.arvoreAst.body.insert(indiceFuncaoMetodo, marcador)
                else:
                    funcaoEncontrada = False
                    #Pesquisando dentro de qual superfunção essa função está definida
                    for superFuncao in self.superFuncoes:
                        if(funcaoMetodo.getDado() in superFuncao.body):
                            indiceFuncaoMetodo = superFuncao.body.index(funcaoMetodo.getDado())
                            superFuncao.body.insert(indiceFuncaoMetodo, ast.Expr(value=ast.Constant(
                                                                value=funcaoMetodo.getMotivoClassificacao(), kind=None)))
                            superFuncao.body.insert(indiceFuncaoMetodo, marcador)

                            funcaoEncontrada = True
                            break

                    if(not funcaoEncontrada):
                        #Se a função for um método de uma classe (estático) ela estará definida dentro de uma classe
                        #Pesquisando dentro de qual classe essa função está definida
                        for classe in self.classes:
                            if(funcaoMetodo.getDado() in classe.body):
                                indiceFuncaoMetodo = classe.body.index(funcaoMetodo.getDado())
                                classe.body.insert(indiceFuncaoMetodo, ast.Expr(value=ast.Constant(
                                                                    value=funcaoMetodo.getMotivoClassificacao(), kind=None)))
                                classe.body.insert(indiceFuncaoMetodo, marcador)
                                
                                funcaoEncontrada = True
                                break

                        if(not funcaoEncontrada):
                            #Se a função está declarada dentro de um método de uma instância
                            #Pesquisando dentro de qual superMétodo essa função está definida
                            for superMetodo in self.superMetodos:
                                if(funcaoMetodo.getDado() in superMetodo.body):
                                    indiceFuncaoMetodo = superMetodo.body.index(funcaoMetodo.getDado())
                                    superMetodo.body.insert(indiceFuncaoMetodo, ast.Expr(value=ast.Constant(
                                                                        value=funcaoMetodo.getMotivoClassificacao(), kind=None)))
                                    superMetodo.body.insert(indiceFuncaoMetodo, marcador)
                                    break
                
        #Acertando informacoes da AST modificada
        self.arvoreAst = ast.fix_missing_locations(self.arvoreAst)

    def escreveImportacaoModuloIntPy(self):
        #Inserindo módulo sys no topo da AST
        self.arvoreAst.body.insert(0, ast.Import(names=[ast.alias(name="sys", asname=None)]))

        #Inserindo comando sys.path.append()
        pathAnalisadorFuncoes = os.path.abspath(__file__)
        pathRepositorio = os.path.normpath(pathAnalisadorFuncoes + "/../../..")

        comandoSysPath = ast.Attribute(value=ast.Name(id='sys', ctx=ast.Load()), attr='path', ctx=ast.Load())
        comandoSysPathAppend = ast.Attribute(value=comandoSysPath, attr='append', ctx=ast.Load())

        self.arvoreAst.body.insert(1, ast.Expr(value=ast.Call(func=comandoSysPathAppend,
                                                        args=[ast.Constant(value=pathRepositorio, kind=None)],
                                                        keywords=[])))
        
        #Inserindo import para o IntPy
        self.arvoreAst.body.insert(2, ast.ImportFrom(module='intpy.intpy',
                                            names=[ast.alias(name='deterministic', asname=None)],
                                            level=0))
        
        #Atualizando árvore AST
        self.arvoreAst = ast.fix_missing_locations(self.arvoreAst)

    def getArvoreAst(self):
        return self.arvoreAst

def exibeMsgAjuda():
    print("Utilização: AnalisadorFuncoes.py [-h | --help]")
    print("Utilização: AnalisadorFuncoes.py [-o PASTA_OUTPUT] ARQUIVO_1.py, ARQUIVO_2.py, ...")
    print("Opções:")
    print("-h, --help                           imprime essa mensagem de ajuda")
    print("-o PASTA_OUTPUT                      especifica a pasta onde serão colocados os arquivos analisados")
    print("ARQUIVO_1.py, ARQUIVO_2.py, ...      arquivos a serem analisados")

if __name__ == "__main__":
    if(len(sys.argv) < 2 or sys.argv[1] == "-h" or sys.argv[1] == "--help"):
        exibeMsgAjuda()
    else:
        main()
