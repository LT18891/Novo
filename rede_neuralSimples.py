import numpy as np

def inicializar_parametros(dimensoes, semente=42):
    np.random.seed(semente)
    parametros = {}
    for i in range(1, len(dimensoes)):
        if i == len(dimensoes)-1:
            parametros["W"+str(i)] = np.random.randn(dimensoes[i], dimensoes[i-1]) * np.sqrt(1/dimensoes[i-1])
        else:
            parametros["W"+str(i)] = np.random.randn(dimensoes[i], dimensoes[i-1]) * np.sqrt(2/dimensoes[i-1])
        parametros["b"+str(i)] = np.zeros((dimensoes[i], 1))
    return parametros

def sigmoid(z):
    return 1/(1+np.exp(-z))

def relu(z):
    return np.maximum(0, z)

def softmax(z):
    exp_z = np.exp(z - np.max(z, axis=0, keepdims=True))
    return exp_z / np.sum(exp_z, axis=0, keepdims=True)

def derivada_sigmoid(a):
    return a*(1-a)

def derivada_relu(a):
    return (a>0).astype(float)

def propagacao_frente(X, parametros, ativacoes, dropout_keep=1.0):
    caches = []
    A = X
    D_caches = []
    L = len(parametros)//2
    for l in range(1, L):
        W = parametros["W"+str(l)]
        b = parametros["b"+str(l)]
        Z = np.dot(W,A)+b
        if ativacoes[l-1] == "relu":
            A = relu(Z)
        elif ativacoes[l-1] == "sigmoid":
            A = sigmoid(Z)
        A_drop = A
        if dropout_keep<1.0:
            D = (np.random.rand(*A.shape)<dropout_keep).astype(float)
            A_drop = (A*D)/dropout_keep
            D_caches.append(D)
        else:
            D_caches.append(None)
        caches.append((Z,A_drop,W,b))
        A = A_drop
    W = parametros["W"+str(L)]
    b = parametros["b"+str(L)]
    Z = np.dot(W,A)+b
    if ativacoes[-1]=="softmax":
        A = softmax(Z)
    elif ativacoes[-1]=="sigmoid":
        A = sigmoid(Z)
    elif ativacoes[-1]=="relu":
        A = relu(Z)
    caches.append((Z,A,W,b))
    return caches, A, D_caches

def custo(Y_pred, Y, tipo_custo="cross_entropy", lambda_reg=0.0, parametros=None):
    m = Y.shape[1]
    if tipo_custo=="cross_entropy":
        c = -np.sum(Y*np.log(Y_pred+1e-15))/m
    else:
        c = np.sum((Y_pred - Y)**2)/(2*m)
    if lambda_reg>0.0:
        L = len(parametros)//2
        reg = 0
        for l in range(1,L+1):
            reg+=np.sum(np.square(parametros["W"+str(l)]))
        reg = (lambda_reg/(2*m))*reg
        c+=reg
    return c

def propagacao_retroativa(X, Y, caches, D_caches, ativacoes, tipo_custo="cross_entropy", lambda_reg=0.0):
    L = len(caches)
    m = Y.shape[1]
    d_parametros = {}
    Z_final,A_final,W_final,b_final = caches[-1]
    if tipo_custo=="cross_entropy":
        dZ = A_final - Y
    else:
        if ativacoes[-1]=="sigmoid":
            dZ = (A_final - Y)*derivada_sigmoid(A_final)
        elif ativacoes[-1]=="relu":
            dZ = (A_final - Y)*derivada_relu(A_final)
    A_prev = caches[-2][1] if L>1 else X
    d_parametros["dW"+str(L)] = (np.dot(dZ, A_prev.T)+lambda_reg*W_final)/m
    d_parametros["db"+str(L)] = np.sum(dZ, axis=1, keepdims=True)/m
    dA_prev = np.dot(W_final.T,dZ)
    for l in range(L-1,0,-1):
        Z_l,A_l,W_l,b_l = caches[l-1]
        D = D_caches[l-1]
        if D is not None:
            dA_prev = (dA_prev*D)/np.count_nonzero(D)*D.shape[1]
        if ativacoes[l-1]=="relu":
            dZ = dA_prev*derivada_relu(A_l)
        elif ativacoes[l-1]=="sigmoid":
            dZ = dA_prev*derivada_sigmoid(A_l)
        A_prev = X if l==1 else caches[l-2][1]
        d_parametros["dW"+str(l)] = (np.dot(dZ,A_prev.T) + lambda_reg*W_l)/m
        d_parametros["db"+str(l)] = np.sum(dZ, axis=1, keepdims=True)/m
        dA_prev = np.dot(W_l.T,dZ)
    return d_parametros

def inicializar_adam(parametros):
    L = len(parametros)//2
    v = {}
    s = {}
    for l in range(1,L+1):
        v["dW"+str(l)] = np.zeros_like(parametros["W"+str(l)])
        v["db"+str(l)] = np.zeros_like(parametros["b"+str(l)])
        s["dW"+str(l)] = np.zeros_like(parametros["W"+str(l)])
        s["db"+str(l)] = np.zeros_like(parametros["b"+str(l)])
    return v,s

def atualizar_parametros(parametros, d_parametros, v, s, t, beta1=0.9, beta2=0.999, alfa=0.001, epsilon=1e-8):
    L = len(parametros)//2
    for l in range(1,L+1):
        v["dW"+str(l)] = beta1*v["dW"+str(l)] + (1-beta1)*d_parametros["dW"+str(l)]
        v["db"+str(l)] = beta1*v["db"+str(l)] + (1-beta1)*d_parametros["db"+str(l)]
        s["dW"+str(l)] = beta2*s["dW"+str(l)] + (1-beta2)*(d_parametros["dW"+str(l)]**2)
        s["db"+str(l)] = beta2*s["db"+str(l)] + (1-beta2)*(d_parametros["db"+str(l)]**2)
        v_corr_dW = v["dW"+str(l)]/(1-beta1**t)
        v_corr_db = v["db"+str(l)]/(1-beta1**t)
        s_corr_dW = s["dW"+str(l)]/(1-beta2**t)
        s_corr_db = s["db"+str(l)]/(1-beta2**t)
        parametros["W"+str(l)] = parametros["W"+str(l)] - alfa*(v_corr_dW/(np.sqrt(s_corr_dW)+epsilon))
        parametros["b"+str(l)] = parametros["b"+str(l)] - alfa*(v_corr_db/(np.sqrt(s_corr_db)+epsilon))
    return parametros,v,s

def treinar(X, Y, dimensoes, ativacoes, tipo_custo="cross_entropy", epocas=1000, alfa=0.001, lambda_reg=0.0, dropout_keep=1.0):
    parametros = inicializar_parametros(dimensoes)
    v,s = inicializar_adam(parametros)
    for i in range(1,epocas+1):
        caches, A_final, D_caches = propagacao_frente(X, parametros, ativacoes, dropout_keep=dropout_keep)
        d_parametros = propagacao_retroativa(X,Y,caches,D_caches,ativacoes,tipo_custo,lambda_reg)
        parametros,v,s = atualizar_parametros(parametros, d_parametros, v, s, i, alfa=alfa)
    return parametros

def prever(X, parametros, ativacoes):
    _, A_final, _ = propagacao_frente(X, parametros, ativacoes, dropout_keep=1.0)
    return A_final

if __name__=="__main__":
    np.random.seed(0)
    m=500
    X=np.random.randn(2,m)
    raio=1.5
    Y=(X[0,:]**2+X[1,:]**2<raio**2).astype(int).reshape(1,m)
    dimensoes=[2,10,5,1]
    ativacoes=["relu","relu","sigmoid"]
    parametros=treinar(X,Y,dimensoes,ativacoes,epocas=2000,alfa=0.01,lambda_reg=0.001,dropout_keep=0.8)
    X_teste=np.array([[0.5,-1.0],[0.5,1.0]])
    Y_pred=prever(X_teste,parametros,ativacoes)
    print((Y_pred>0.5).astype(int))
