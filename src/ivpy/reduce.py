import pandas as pd
from sklearn.manifold import TSNE
import umap as ump
from .data import _typecheck

#------------------------------------------------------------------------------

def tsne(X,**kwargs):
    _typecheck(**locals())
    xy = TSNE(n_components=2,**kwargs).fit_transform(X)
    return pd.DataFrame(xy,index=X.index,columns=['x','y'])

def umap(X,**kwargs):
    _typecheck(**locals())
    xy = ump.UMAP(**kwargs).fit_transform(X)
    return pd.DataFrame(xy,index=X.index,columns=['x','y'])
