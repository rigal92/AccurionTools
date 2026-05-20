import pandas as pd 
import os 
from typing import Dict, Hashable
from .nanofilm.ndimage.io import imread

def readROIdat(filename:str)->Dict[Hashable,pd.DataFrame]:
    try:
        df = pd.read_table(filename, header = [0,1]).droplevel(1, axis = 1)
    except UnicodeDecodeError:
        df = pd.read_table(filename, header = [0,1], encoding='unicode_escape').droplevel(1, axis = 1)
    df.rename(columns = {"#Lambda":"Lambda", "#AOI":"AOI", "#ROIidx":"ROIidx"}, inplace = True)
    return {i:data for i,data in df.groupby("ROIidx")}

def accurionToWase(filename:str):
    wase_header = """\nVASEmethod[EllipsometerType=5, Isotropic+Depolarization, AutoRetarder=1, TrackPol=1, ZoneAve=1, Revs=50.0, WinCorrected=1, AutoSlit=1700, WVASE=3.934, HardVer=6.256, Thu Jan 19 10:52:30 2023]\nOriginal[C:\\WVASE32\\DAT\\Ermes\\221214_exf_mos2_ellips\\221214_2_coarse_60deg.dat]\nnm\n"""
    dfs = readROIdat(filename)
    for i,df in dfs.items():
        new_filename = filename.replace(".dat", "_ROI"+str(i)+".dat")
        columns = [i for i in ["Lambda","AOI","Psi", "Delta", "Psi_sigma", "Delta_sigma"] if i in df.columns]
        df[columns].to_csv(new_filename, sep="\t", header=None, index=None)
        with open(new_filename) as f:
            content = f.read()       
        with open(new_filename, "w") as f:
            f.write(wase_header + content)

def read_map(info_file:str)->tuple[pd.DataFrame,pd.DataFrame]:
    """
    Opens an accurion map and returns two DataFrame with psi and delta 

    Inputs
    ------
    info_file:str
        filename from which retrieve the names of each png with the data

    Return
    ------
    tuple[tuple, DataFrame,DataFrame]
        returns a tuple 
            - shape of the image
            - DataFrame of Delta
            - DataFrame of Psi
    """
    info_df = pd.read_table(info_file, header=[0,1]).droplevel(1, axis=1)
    file_dir = os.path.dirname(info_file)
    lbd = info_df["#Lambda"]
    aoi = info_df["AOI"]
    delta_df = [imread(f"{file_dir}/{d}") for d in info_df["Delta"]]
    shape = delta_df[0].shape
    columns = pd.MultiIndex.from_product([range(shape[0]), range(shape[1])], names=["xpixel", "ypixel"])
    delta_df = pd.DataFrame([df.flatten() for df in delta_df], index=[lbd,aoi], columns=columns)
    psi_df = pd.DataFrame([imread(f"{file_dir}/{d}").flatten() for d in info_df["Psi"]], index=[lbd,aoi], columns=columns)
    return delta_df, psi_df


