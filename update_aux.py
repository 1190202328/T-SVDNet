import mars.tensor as mt
import numpy as np
import torch


def soft(S, thd):
    #     pdb.set_trace()
    return np.sign(S) * np.maximum(0, abs(S) - thd)


def update_aux(A, rho, eps=1e-5):
    A = A.cpu().numpy()
    A = A.transpose(1, 2, 0)
    n_3 = np.size(A, 2)

    A_fft = np.fft.fft(A, axis=2)
    End_Value = np.floor(n_3 / 2).astype(int) + 1
    # print(f'n_3 = {n_3}')
    # print(f'A_fft.shape = {A_fft.shape}')
    # print(f'End_Value = {End_Value}')
    # # A_fft.shape = (10, 5, 10)
    # # End_Value = 6
    # # n_3 = 10

    # pdb.set_trace()
    for i in range(End_Value + 1):
        # S_hat <-- S * F
        U, S, V = mt.linalg.svd(A_fft[:, :, i])
        # print(U)

        # U, S, V = np.linalg.svd(A_fft[:, :, i])

        # print(f'A_fft[:, :, i].shape = {A_fft[:, :, i].shape}')
        # print(f'U.shape = {U.shape}')
        # print(f'S.shape = {S.shape}')
        # print(f'V.shape = {V.shape}')

        # mt.linalg.svd
        # A_fft[:, :, i].shape = (10, 5)
        # U.shape = (10, 5)
        # S.shape = (5,)
        # V.shape = (5, 5)

        # np.linalg.svd
        # A_fft[:, :, i].shape = (10, 5)
        # U.shape = (10, 10)
        # S.shape = (5,)
        # V.shape = (5, 5)

        weight = rho * n_3 / (S + eps)
        S_hat = soft(np.diag(S), np.diag(weight))

        # A_hat <-- U * S_hat * V
        A_fft[:, :, i] = U.dot(S_hat).dot(V)
        if i > 0:
            A_fft[:, :, n_3 - i] = U.conj().dot(S_hat).dot(V.conj())
    A = np.fft.ifft(A_fft, axis=2)
    A = A.transpose(2, 0, 1)
    A = torch.from_numpy(np.real(A))
    return A
