from pathlib import Path
import math
import numpy as np
# Angles from vertical in the character's local plane. Each phrase has a preparation, accent and release.
L=[(255.7,10,-7),(256.24,12,-15),(256.82,24,-89),(257.17,23,-93),(258.07,15,-32),(259.15,14,-25),(260.0,10,-12),(262.85,12,-19),(263.7,20,-70),(264.55,18,-81),(265.53,12,-29),(266.3,12,-20),(267.14,23,-89),(267.66,23,-98),(268.65,16,-44),(269.55,12,-21),(270.8,11,-16),(272.4,8,-7)]
R=[(255.7,8,-9),(256.9,10,-14),(258.0,13,-23),(258.71,23,-78),(259.18,23,-77),(259.94,16,-34),(260.62,21,-58),(261.24,21,-67),(262.4,12,-20),(263.3,10,-11),(265.24,11,-16),(266.6,12,-28),(267.65,15,-45),(268.58,12,-28),(269.08,15,-32),(269.7,19,-65),(270.4,17,-50),(271.26,12,-23),(272.5,8,-10)]
def curve(keys,t):
 if t<=keys[0][0]:return keys[0][1:]
 for a,b in zip(keys,keys[1:]):
  if t<=b[0]:
   u=(t-a[0])/(b[0]-a[0]);u=u*u*(3-2*u);return tuple(x+(y-x)*u for x,y in zip(a[1:],b[1:]))
 return keys[-1][1:]
def arm(side,t,walk):
 keys=L if side<0 else R;alpha,beta=curve(keys,t);_,lag=curve(keys,t-.10);stride=math.sin(t*7)*walk
 alpha+=side*4*stride;beta+=side*9*stride
 a=np.array([side*68.,-433.]);rad=math.radians
 def limb(deg,n):return n*np.array([side*math.sin(rad(deg)),math.cos(rad(deg))])
 b=a+limb(alpha,100);d=b+limb(beta,98);rotation=-side*(.7*beta+.3*lag);return a,b,d,rotation
