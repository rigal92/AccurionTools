import pandas as pd 


def readROIdat(filename):
    try:
        df = pd.read_table(filename, header = [0,1]).droplevel(1, axis = 1)
    except:
        df = pd.read_table(filename, header = [0,1], encoding='unicode_escape').droplevel(1, axis = 1)
    df.rename(columns = {"#Lambda":"Lambda", "#AOI":"AOI", "#ROIidx":"ROIidx"}, inplace = True)
    return {i:data for i,data in df.groupby("ROIidx")}

def accurionToWase(filename):
    wase_header = """\nVASEmethod[EllipsometerType=5, Isotropic+Depolarization, AutoRetarder=1, TrackPol=1, ZoneAve=1, Revs=50.0, WinCorrected=1, AutoSlit=1700, WVASE=3.934, HardVer=6.256, Thu Jan 19 10:52:30 2023]\nOriginal[C:\\WVASE32\\DAT\\Ermes\\221214_exf_mos2_ellips\\221214_2_coarse_60deg.dat]\nnm\n"""
    dfs = readROIdat(filename)
    for i,df in dfs.items():
        new_filename = filename.replace(".dat", "_ROI"+str(i)+".dat")
        columns = df.columns.intersection(["Lambda","AOI","Psi", "Delta", "Psi_sigma", "Delta_sigma"])
        df[columns].to_csv(new_filename, sep = "\t", header = None, index = None)
        with open(new_filename) as f:
            content = f.read()       
        with open(new_filename, "w") as f:
            f.write(wase_header + content)

