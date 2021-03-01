import umap
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rcParams
from typing import Union, Sequence
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

rcParams['mathtext.fontset'] = 'stix'
rcParams['font.family'] = 'STIXGeneral'
Num = Union[int, float]


def import_csv_data(path: str = '') -> pd.DataFrame:
    '''
    Creates a pandas dataframe from the path to a csv data file.
    '''
    if not path:
        path = input('Enter the path of your csv data file: ')
    return pd.read_csv(path)


def clean_data(data: pd.DataFrame, dim: int = 2):
    '''    
    Removes ghost cells (if present) and other data columns that
    are not relevant for the dimensionality reduction (i.e. spatial 
    coordinates) from the original data in place .
    '''
    if dim not in [2, 3]:
        raise ValueError(
            'dim can only be 2 or 3. Use 2 for 2D-plane data and 3 for 3D-volume data')

    cols_to_drop = ['XYZ:'+str(x) for x in range(3)]
    cols_to_drop.extend(['T'])

    if 'vtkGhostType' in data.columns:
        data.drop(data[data.vtkGhostType == 2].index, inplace=True)
        cols_to_drop.append('vtkGhostType')

    if dim == 2:
        cols_to_drop.append('U:2')

    data.drop(columns=cols_to_drop, axis=1, inplace=True)
    data.reset_index(drop=True, inplace=True)


def scale_data(data: pd.DataFrame) -> np.ndarray:
    '''    
    Scales input data based on sklearn standard scaler.
    '''
    scaled_data = StandardScaler().fit_transform(data)
    return scaled_data


def embed_data(data: pd.DataFrame, algorithm, scale: bool = True, **params) -> np.ndarray:
    '''
    Applies either UMAP or t-SNE dimensionality reduction algorithm 
    to the input data (with optional scaling) and returns the
    embedding array. Also accepts specific and optional algorithm 
    parameters.
    '''
    algorithms = [umap.UMAP, TSNE]
    if algorithm not in algorithms:
        raise ValueError(
            'invalid algorithm. Expected one of: %s' % algorithms)

    if scale:
        data = scale_data(data)

    reducer = algorithm(**params)
    embedding = reducer.fit_transform(data)
    return embedding


def plot_embedding(embedding: np.ndarray, data: pd.DataFrame = pd.DataFrame(), cmap_var: str = None, cmap_minmax: Sequence[Num] = list()):
    '''
    Plots input embedding as a scatter plot. Optionally, a variable
    with an optional range can be supplied to use as the colormap.
    '''
    if cmap_var not in data.columns and cmap_var:
        raise ValueError(
            'invalid variable for the color map. Expected one of: %s' % data.columns)

    if len(cmap_minmax) != 2 and cmap_minmax:
        raise ValueError(
            'too many values to unpack. Expected 2')

    fig, ax = plt.subplots(figsize=[6, 5])
    plt.gca().set_aspect('equal', 'datalim')
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    if cmap_var:
        if cmap_minmax:
            plt.scatter(embedding[:, 0], embedding[:, 1], c=data[cmap_var],
                        vmin=cmap_minmax[0], vmax=cmap_minmax[1], cmap='inferno')
        else:
            plt.scatter(embedding[:, 0], embedding[:, 1],
                        c=data[cmap_var], cmap='inferno')
        cb = plt.colorbar()
        cb.ax.tick_params(labelsize=16)
        cb.set_label(cmap_var, size=16)
    else:
        plt.scatter(embedding[:, 0], embedding[:, 1])
    plt.tight_layout()
    plt.show()


def main():
    path = 'data/LES/2D/toy.csv'
    data = import_csv_data(path)
    clean_data(data, dim=2)
    embedding = embed_data(data, umap.UMAP, scale=True,
                           n_neighbors=20, min_dist=0.2)
    plot_embedding(embedding, data=data, cmap_var='Phi', cmap_minmax=[0,5])


if __name__ == '__main__':
    main()
