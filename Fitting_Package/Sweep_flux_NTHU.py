#import pyautogui as auto
#import time
"""
w, h = auto.position()

for i in range(1000):
    time.sleep(3)
    auto.click(562, 507)
"""

import numpy as np
from numpy import cos, pi
from scipy.optimize import curve_fit as CF
import matplotlib.pyplot as plt

# sweep data
x = np.array([-1100, -1090, -1080, -1070, -1060, -1050, -1041, -1040, -1000, -600, -550, -500, -450, -400, -350, -300, -250, -200, -150, -100, -40, 220, 380, -650, -700, -730, -825, -850, -877, -888, -920, -960, -1100]) * 1e-3
y = np.array([2.01024, 2.0832 , 2.1536, 2.2213, 2.2894, 2.35301, 2.40662, 2.41341, 2.64964, 4.1679, 4.2866, 4.3926, 4.4865, 4.5690, 4.64, 4.7, 4.7499, 4.7885, 4.817, 4.8345, 4.8427, 4.7026, 4.4723, 4.0365, 3.89195, 3.79791, 3.4576, 3.3588, 3.2468, 3.19933, 3.0552, 2.8616, 2.01024]) 

#fitting function, f ~ cos**0.5
f = lambda x,a,b,d: (a*abs(cos(b*pi*(x-40))))**0.5 + d # 23.435 = 8*0.188*15.582

param, _ = CF(f, x, y, p0=[23.435, 0.4, 0], maxfev = 100000)

print("fitting param: ", param)

# plot fitting curve
xplot = np.arange(-2, 1, 0.001)
yfit = f(xplot, *param)

# analytic parameters
Ejmax = 15.5820
Ec = 0.1881
phi_extlist = np.linspace(-1, 1, 500)

Ej = Ejmax * (abs(cos(phi_extlist*pi / 2.4  )))
E01 = (8*Ej*Ec)**0.5
#print()

plt.figure(1)
plt.plot(phi_extlist - 0.04, E01, '--', label = "analytic")


#plt.figure(2)
plt.plot(xplot, yfit, label = "exp")
plt.plot(x, y, "k.")
#plt.plot(xplot, f(xplot, 23.435, 0.4, 0))

plt.legend()
plt.xlabel("current(mA)")
plt.ylabel("E01(GHz)")

plt.show()

def fit_freq(I):
    a_find = np.where(np.round(xplot,4) == I)
    return (f"{I}mA", yfit[a_find[0]])
'''
for I in [-0.82, -0.95, -1.08]:
    print(fit_freq(I))
'''  
current = np.linspace(-0.80, -1.1, 301) 

for I in current:
    I = np.round(I,4)
    print(I)
    print(fit_freq(I))

"""
a_find=np.where(np.round(xplot,4)==-0.82)
print("-0.82mA",yfit[a_find[0]])  #3.478

a_find=np.where(np.round(xplot,4)==-0.9)
print("-0.9mA",yfit[a_find[0]])

a_find=np.where(np.round(xplot,4)==-0.888)
print("-0.888mA",yfit[a_find[0]])  #3.201

a_find=np.where(np.round(xplot,4)==-0.88)
print("-0.88mA",yfit[a_find[0]])  #3.234

a_find=np.where(np.round(xplot,4)==-0.89)
print("-0.89mA",yfit[a_find[0]])

a_find=np.where(np.round(xplot,4)==-0.9)
print("-0.9mA",yfit[a_find[0]])

a_find=np.where(np.round(xplot,4)==-0.91)
print("-0.91mA",yfit[a_find[0]])

a_find=np.where(np.round(xplot,4)==-0.92)
print("-0.92mA",yfit[a_find[0]])

a_find=np.where(np.round(xplot,4)==-0.93)
print("-0.93mA",yfit[a_find[0]])

a_find=np.where(np.round(xplot,4)==-0.94)
print("-0.94mA",yfit[a_find[0]])

a_find=np.where(np.round(xplot,4)==-0.95)
print("-0.95mA",yfit[a_find[0]])

a_find=np.where(np.round(xplot,4)==-0.96)
print("-0.96mA",yfit[a_find[0]])

a_find=np.where(np.round(xplot,4)==-0.97)
print("-0.97mA",yfit[a_find[0]])

a_find=np.where(np.round(xplot,4)==-0.98)
print("-0.98mA",yfit[a_find[0]])

a_find=np.where(np.round(xplot,4)==-0.99)
print("-0.99mA",yfit[a_find[0]])

a_find=np.where(np.round(xplot,4)==-1)
print("-1mA",yfit[a_find[0]])

a_find=np.where(np.round(xplot,4)==-1.01)
print("-1.01mA",yfit[a_find[0]])

a_find=np.where(np.round(xplot,4)==-1.02)
print("-1.02mA",yfit[a_find[0]])

a_find=np.where(np.round(xplot,4)==-1.03)
print("-1.03mA",yfit[a_find[0]])

a_find=np.where(np.round(xplot,4)==-1.04)
print("-1.04mA",yfit[a_find[0]])

a_find=np.where(np.round(xplot,4)==-1.05)
print("-1.05mA",yfit[a_find[0]])

a_find=np.where(np.round(xplot,4)==-1.1)
print("-1.1mA",yfit[a_find[0]])

a_find=np.where(np.round(xplot,4)==-1.2)
print("-1.2mA",yfit[a_find[0]])
"""