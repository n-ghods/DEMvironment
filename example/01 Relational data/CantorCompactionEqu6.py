from math import pi, log as ln
def CantorCompactionEqu6(phi, phi_0, phi_max, alpha, b, k, Z_0):
    P_star = (
        - b*phi/(2*pi) * (Z_0 + k*(phi-phi_0)**alpha) *
        ln((phi_max-phi)/(phi_max-phi_0)))
    return P_star