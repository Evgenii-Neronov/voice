from pathlib import Path
import pickle,io,zipfile,os,numpy as np
Z=Path(os.environ.get('AIST_ARCHIVE','I:/VOICE/voice/models/motion/aistplusplus/keypoints3d.zip'))
class ArrayReader(pickle.Unpickler):
 def find_class(self,module,name):
  allowed={('numpy','ndarray'):np.ndarray,('numpy','dtype'):np.dtype,('numpy.core.multiarray','_reconstruct'):np._core.multiarray._reconstruct,('numpy.core.multiarray','scalar'):np._core.multiarray.scalar}
  if (module,name) in allowed:return allowed[module,name]
  raise ValueError((module,name))
def read(z,name):return ArrayReader(io.BytesIO(z.read(name))).load()
if __name__=='__main__':
 with zipfile.ZipFile(Z) as z:
  names=[n for n in z.namelist() if Path(n).name.startswith(('gMH','gLH')) and n.endswith('.pkl')];print('hiphop',len(names),names[:8]);d=read(z,names[0]);print(d.keys());a=d['keypoints3d_optim'];print(a.shape);print('frame0',a[0].round(2));print('ranges',np.nanmin(a,axis=(0,1)),np.nanmax(a,axis=(0,1)))
